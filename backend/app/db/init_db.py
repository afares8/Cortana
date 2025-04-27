from app.db.base import InMemoryDB
from app.models.user import UserInDB
from app.models.contract import ContractInDB
from app.core.security import get_password_hash

users_db = InMemoryDB[UserInDB](UserInDB)
contracts_db = InMemoryDB[ContractInDB](ContractInDB)

def init_db() -> None:
    """Initialize the database with some sample data."""
    if not users_db.get_multi(filters={"email": "admin@legalcontracttracker.com"}):
        users_db.create(
            obj_in=UserInDB(
                email="admin@legalcontracttracker.com",
                hashed_password=get_password_hash("admin"),
                full_name="Admin User",
                is_superuser=True,
            )
        )
