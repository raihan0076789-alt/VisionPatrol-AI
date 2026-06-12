from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.core.seeder import seed_sample_data
from app.api import auth, violations, challans, analytics, upload


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create folders
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(f"{settings.UPLOAD_DIR}/evidence", exist_ok=True)
    os.makedirs(f"{settings.UPLOAD_DIR}/challans", exist_ok=True)
    os.makedirs(f"{settings.UPLOAD_DIR}/videos", exist_ok=True)

    # Mount static files
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

    # Auto-seed sample data
    async with AsyncSessionLocal() as db:
        await seed_sample_data(db)

    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

import os as _os
allowed_origins = _os.getenv("ALLOWED_ORIGINS", "*")
origins = [o.strip() for o in allowed_origins.split(",")] if allowed_origins != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1")
app.include_router(violations.router, prefix="/api/v1")
app.include_router(challans.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(upload.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"app": settings.APP_NAME, "version": settings.APP_VERSION, "status": "running"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/api/v1/seed", tags=["Admin"])
async def manual_seed():
    """Manually trigger data seeding"""
    async with AsyncSessionLocal() as db:
        from sqlalchemy import text
        await db.execute(text("DELETE FROM challans"))
        await db.execute(text("DELETE FROM violations"))
        await db.execute(text("DELETE FROM detection_sessions"))
        await db.execute(text("DELETE FROM cameras"))
        await db.execute(text("DELETE FROM vehicles"))
        await db.commit()
        await seed_sample_data(db)
    return {"message": "Data seeded successfully"}