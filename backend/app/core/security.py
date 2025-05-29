from datetime import datetime, timedelta
from typing import Any, Union, Optional, Dict, List, Tuple
import os
import base64
import logging
import secrets
import hashlib
import pyotp
import qrcode
from io import BytesIO

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes

from app.core.config import settings

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login",
    scopes={
        "admin": "Full access to all resources",
        "user": "Standard user access",
    },
)

ENCRYPTION_KEY_ENV = "DOCUMENT_ENCRYPTION_KEY"
SALT_LENGTH = 16
KEY_LENGTH = 32
ITERATIONS = 100000

TOTP_ISSUER = "LegalContractTracker"


def create_access_token(
    subject: Union[str, Any], 
    expires_delta: Optional[timedelta] = None,
    scopes: List[str] = None
) -> str:
    """
    Create a JWT access token with optional scopes.
    """
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    
    if scopes:
        to_encode["scopes"] = scopes
        
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password for storage.
    """
    return pwd_context.hash(password)


def get_current_user(
    security_scopes: SecurityScopes, 
    token: str = Depends(oauth2_scheme)
):
    """
    Get the current user from a JWT token with scope validation.
    Checks auth mode setting to determine whether to use production auth or testing bypass.
    """
    use_production_auth = os.getenv("PRODUCTION_AUTH_MODE", "false").lower() == "true"
    
    if not use_production_auth:
        # Testing mode - bypass authentication
        return {
            "id": "admin-user",
            "name": "Test Admin",
            "scopes": ["admin", "user"]
        }
    
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
        
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
    except JWTError:
        raise credentials_exception
        
    for scope in security_scopes.scopes:
        if scope not in token_scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Not enough permissions. Required scope: {scope}",
                headers={"WWW-Authenticate": authenticate_value},
            )
    
    return {"id": user_id, "name": "Test User", "scopes": token_scopes}


def admin_required(user = Security(get_current_user, scopes=["admin"])):
    """
    Dependency to require admin access.
    Uses the same auth mode logic as get_current_user.
    """
    return user  # get_current_user already handles the auth mode logic



def get_encryption_key() -> bytes:
    """
    Get or generate the encryption key for document encryption.
    
    The key is stored in an environment variable. If not present, a new key is generated.
    In production, this key should be stored securely in a key management system.
    """
    key = os.environ.get(ENCRYPTION_KEY_ENV)
    
    if not key:
        key = base64.urlsafe_b64encode(os.urandom(32)).decode()
        os.environ[ENCRYPTION_KEY_ENV] = key
        logger.warning(
            "Generated new document encryption key. In production, this should be stored securely."
        )
    
    return base64.urlsafe_b64decode(key)


def derive_key(password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
    """
    Derive an encryption key from a password using PBKDF2.
    
    Returns a tuple of (key, salt).
    """
    if salt is None:
        salt = os.urandom(SALT_LENGTH)
        
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_LENGTH,
        salt=salt,
        iterations=ITERATIONS,
    )
    
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt


def encrypt_document(document_data: bytes, password: Optional[str] = None) -> Dict[str, str]:
    """
    Encrypt document data using Fernet symmetric encryption.
    
    If a password is provided, it is used to derive the encryption key.
    Otherwise, the system encryption key is used.
    
    Returns a dictionary with the encrypted data and metadata.
    """
    try:
        if password:
            key, salt = derive_key(password)
            fernet = Fernet(key)
            encrypted_data = fernet.encrypt(document_data)
            
            return {
                "encrypted_data": base64.b64encode(encrypted_data).decode(),
                "salt": base64.b64encode(salt).decode(),
                "encryption_type": "password",
                "encryption_algorithm": "Fernet (AES-128-CBC)",
                "encrypted_at": datetime.utcnow().isoformat(),
            }
        else:
            key = get_encryption_key()
            fernet = Fernet(base64.urlsafe_b64encode(key))
            encrypted_data = fernet.encrypt(document_data)
            
            return {
                "encrypted_data": base64.b64encode(encrypted_data).decode(),
                "encryption_type": "system",
                "encryption_algorithm": "Fernet (AES-128-CBC)",
                "encrypted_at": datetime.utcnow().isoformat(),
            }
    except Exception as e:
        logger.error(f"Document encryption failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document encryption failed",
        )


def decrypt_document(encrypted_doc: Dict[str, str], password: Optional[str] = None) -> bytes:
    """
    Decrypt document data.
    
    If the document was encrypted with a password, the same password must be provided.
    """
    try:
        encrypted_data = base64.b64decode(encrypted_doc["encrypted_data"])
        encryption_type = encrypted_doc.get("encryption_type", "system")
        
        if encryption_type == "password":
            if not password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Password required to decrypt this document",
                )
                
            salt = base64.b64decode(encrypted_doc["salt"])
            key, _ = derive_key(password, salt)
            fernet = Fernet(key)
        else:
            key = get_encryption_key()
            fernet = Fernet(base64.urlsafe_b64encode(key))
            
        return fernet.decrypt(encrypted_data)
    except Exception as e:
        logger.error(f"Document decryption failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document decryption failed",
        )



def generate_totp_secret() -> str:
    """
    Generate a new TOTP secret for 2FA.
    """
    return pyotp.random_base32()


def get_totp_uri(secret: str, username: str) -> str:
    """
    Get the TOTP URI for QR code generation.
    """
    return pyotp.totp.TOTP(secret).provisioning_uri(
        name=username,
        issuer_name=TOTP_ISSUER
    )


def generate_qr_code(totp_uri: str) -> bytes:
    """
    Generate a QR code image for the TOTP URI.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(totp_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer)
    return buffer.getvalue()


def verify_totp(secret: str, token: str) -> bool:
    """
    Verify a TOTP token against a secret.
    """
    totp = pyotp.TOTP(secret)
    return totp.verify(token)



def log_security_event(
    event_type: str,
    user_id: Optional[str] = None,
    resource_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None,
) -> None:
    """
    Log a security event for audit purposes.
    """
    if request and not ip_address:
        ip_address = request.client.host if request.client else None
        
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "user_id": user_id,
        "resource_id": resource_id,
        "ip_address": ip_address,
        "details": details or {},
    }
    
    logger.info(f"Security event: {event}")
    
    return event


def check_password_strength(password: str) -> Dict[str, Any]:
    """
    Check the strength of a password.
    
    Returns a dictionary with the strength assessment.
    """
    strength = {
        "length": len(password) >= 12,
        "uppercase": any(c.isupper() for c in password),
        "lowercase": any(c.islower() for c in password),
        "digits": any(c.isdigit() for c in password),
        "special": any(not c.isalnum() for c in password),
    }
    
    strength["score"] = sum(1 for v in strength.values() if v)
    
    if strength["score"] <= 2:
        strength["assessment"] = "weak"
    elif strength["score"] <= 4:
        strength["assessment"] = "moderate"
    else:
        strength["assessment"] = "strong"
        
    return strength
