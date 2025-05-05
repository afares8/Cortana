from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import logging
from logging.handlers import RotatingFileHandler

from app.core.config import settings
from app.db.init_db import init_db
from app.routers import auth, test_mistral
from app.services.email import setup_scheduler

from app.services.contracts import contracts_router
from app.services.clients import clients_router
from app.services.compliance import compliance_router
from app.services.workflows import workflows_router
from app.services.tasks import tasks_router
from app.services.audit import audit_router
from app.services.ai import ai_router
from app.services.traffic import traffic_router

from app.legal.routers import router as legal_router
from app.legal.services import init_legal_db
from app.accounting.routers import router as accounting_router
from app.accounting.services import init_accounting_db

logs_dir = "/app/logs" if os.path.exists("/app") else "logs"
os.makedirs(logs_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),  # Console handler
        RotatingFileHandler(
            os.path.join(logs_dir, "backend.log"), 
            maxBytes=10485760,  # 10MB
            backupCount=5,
            encoding="utf-8"
        )
    ]
)
logger = logging.getLogger(__name__)

app = FastAPI(title=settings.PROJECT_NAME)

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.include_router(auth, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(legal_router, prefix=f"{settings.API_V1_STR}/legal", tags=["legal"])
app.include_router(test_mistral.router, prefix=f"{settings.API_V1_STR}", tags=["test"])

app.include_router(contracts_router, prefix=f"{settings.API_V1_STR}/contracts", tags=["contracts"])
app.include_router(clients_router, prefix=f"{settings.API_V1_STR}/clients", tags=["clients"])
app.include_router(compliance_router, prefix=f"{settings.API_V1_STR}/compliance", tags=["compliance"])
app.include_router(workflows_router, prefix=f"{settings.API_V1_STR}/workflows", tags=["workflows"])
app.include_router(tasks_router, prefix=f"{settings.API_V1_STR}/tasks", tags=["tasks"])
app.include_router(audit_router, prefix=f"{settings.API_V1_STR}/audit", tags=["audit"])
app.include_router(ai_router, prefix=f"{settings.API_V1_STR}/ai", tags=["ai"])
app.include_router(traffic_router, prefix=f"{settings.API_V1_STR}/traffic", tags=["traffic"])
app.include_router(accounting_router, prefix=f"{settings.API_V1_STR}/accounting", tags=["accounting"])

os.makedirs("uploads", exist_ok=True)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/api/v1/test")
async def test_api_v1():
    return {"status": "api_v1_working"}


@app.on_event("startup")
async def startup_event():
    logger.info("Initializing application...")
    
    init_db()
    init_legal_db()
    init_accounting_db()
    
    logger.info("Service modules initialized")
    
    scheduler = setup_scheduler()
    scheduler.start()
    logger.info("Scheduler started")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down application...")
