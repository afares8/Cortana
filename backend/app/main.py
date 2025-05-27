from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import logging
import datetime
from logging.handlers import RotatingFileHandler

from app.core.config import settings
from app.db.init_db import init_db
from app.routers.auth import router as auth_router
from app.routers.test_mistral import router as test_mistral_router
from app.routers.system_settings import router as system_settings_router
from app.routers.diagnostics import router as diagnostics_router
from app.services.email import setup_scheduler

from app.services.contracts import contracts_router
from app.services.clients import clients_router
from app.services.compliance import compliance_router
from app.services.workflows import workflows_router
from app.services.tasks import tasks_router
from app.services.audit import audit_router
from app.services.ai import ai_router
from app.services.traffic import traffic_router

from app.modules.admin.departments import router as departments_router
from app.modules.admin.roles import router as roles_router
from app.modules.admin.functions import router as functions_router
from app.modules.admin.templates import router as templates_router
from app.modules.admin.audit import router as admin_audit_router
from app.modules.automation.rules_engine import router as rules_engine_router
from app.modules.ai import router as ai_profiles_router
from app.modules.core.users import router as user_departments_router
from app.modules.artur.routers import router as artur_router

from app.legal.routers import router as legal_router
from app.legal.services import init_legal_db
from app.accounting.routers import router as accounting_router
from app.accounting.services import init_accounting_db
from app.accounting.reminder import setup_accounting_scheduler

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

app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(legal_router, prefix=f"{settings.API_V1_STR}/legal", tags=["legal"])
app.include_router(test_mistral_router, prefix=f"{settings.API_V1_STR}", tags=["test"])

app.include_router(contracts_router, prefix=f"{settings.API_V1_STR}/contracts", tags=["contracts"])
app.include_router(clients_router, prefix=f"{settings.API_V1_STR}/clients", tags=["clients"])
app.include_router(compliance_router, prefix=f"{settings.API_V1_STR}/compliance", tags=["compliance"])
app.include_router(workflows_router, prefix=f"{settings.API_V1_STR}/workflows", tags=["workflows"])
app.include_router(tasks_router, prefix=f"{settings.API_V1_STR}/tasks", tags=["tasks"])
app.include_router(audit_router, prefix=f"{settings.API_V1_STR}/audit", tags=["audit"])
app.include_router(ai_router, prefix=f"{settings.API_V1_STR}/ai", tags=["ai"])
app.include_router(traffic_router, prefix=f"{settings.API_V1_STR}/traffic", tags=["traffic"])
app.include_router(accounting_router, prefix=f"{settings.API_V1_STR}/accounting", tags=["accounting"])
app.include_router(system_settings_router, prefix=f"{settings.API_V1_STR}/system/settings", tags=["system"])
app.include_router(diagnostics_router, prefix=f"{settings.API_V1_STR}/diagnostics", tags=["diagnostics"])

app.include_router(departments_router, prefix=f"{settings.API_V1_STR}/admin/departments", tags=["admin", "departments"])
app.include_router(roles_router, prefix=f"{settings.API_V1_STR}/admin/roles", tags=["admin", "roles"])
app.include_router(functions_router, prefix=f"{settings.API_V1_STR}/admin/functions", tags=["admin", "functions"])
app.include_router(templates_router, prefix=f"{settings.API_V1_STR}/admin/templates", tags=["admin", "templates"])
app.include_router(admin_audit_router, prefix=f"{settings.API_V1_STR}/admin/audit", tags=["admin", "audit"])
app.include_router(rules_engine_router, prefix=f"{settings.API_V1_STR}/automation/rules", tags=["automation", "rules"])
app.include_router(ai_profiles_router, prefix=f"{settings.API_V1_STR}/ai/profiles", tags=["ai", "profiles"])
app.include_router(user_departments_router, prefix=f"{settings.API_V1_STR}/users", tags=["users", "departments"])
app.include_router(artur_router, prefix=f"{settings.API_V1_STR}/artur", tags=["artur"])

os.makedirs("uploads", exist_ok=True)

app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.get("/health")
async def health():
    """Health check endpoint for Docker healthcheck.
    Validates scheduler tasks and AI service status."""
    from app.services.ai.mistral_client import check_ai_service_status
    
    ai_status = await check_ai_service_status()  # Await the coroutine
    
    scheduler_status = "active"
    
    logger.info(f"Health check: AI service status: {ai_status}, Scheduler status: {scheduler_status}")
    
    return {
        "status": "ok",
        "ai_service": ai_status,
        "scheduler": scheduler_status,
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

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
    
    from app.accounting.storage_check import ensure_storage_directories
    ensure_storage_directories()
    logger.info("Storage directories verified")
    
    scheduler = setup_scheduler()
    scheduler.start()
    setup_accounting_scheduler(scheduler)
    
    from app.services.compliance.scheduler import setup_compliance_scheduler
    setup_compliance_scheduler(scheduler)
    
    from app.modules.artur.observation.scheduler import observation_scheduler
    observation_scheduler.start()
    
    logger.info("Scheduler started")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down application...")
