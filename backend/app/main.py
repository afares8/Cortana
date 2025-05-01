from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import logging

from app.core.config import settings
from app.db.init_db import init_db
from app.routers import auth, contracts, ai
from app.services.email import setup_scheduler
from app.legal.routers import router as legal_router
from app.legal.services import init_legal_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
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
app.include_router(
    contracts, prefix=f"{settings.API_V1_STR}/contracts", tags=["contracts"]
)
app.include_router(
    ai, prefix=f"{settings.API_V1_STR}/ai", tags=["ai"]
)
app.include_router(
    legal_router, prefix=f"{settings.API_V1_STR}/legal", tags=["legal"]
)

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
    
    scheduler = setup_scheduler()
    scheduler.start()
    logger.info("Scheduler started")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down application...")
