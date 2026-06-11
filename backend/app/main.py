from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import os

from app.core.config import settings
from app.api import auth, violations, challans, analytics


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create folders first
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(f"{settings.UPLOAD_DIR}/evidence", exist_ok=True)
    os.makedirs(f"{settings.UPLOAD_DIR}/challans", exist_ok=True)
    os.makedirs(f"{settings.UPLOAD_DIR}/videos", exist_ok=True)

    # Mount static files after folders exist
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(violations.router, prefix="/api/v1")
app.include_router(challans.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {"app": settings.APP_NAME, "version": settings.APP_VERSION, "status": "running"}


@app.get("/health")
async def health():
    return {"status": "ok"}