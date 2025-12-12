from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from database import engine, Base, get_db
from routers import api_security, compliance, dependencies, sbom, health
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    yield
    logger.info("Application shutdown")


app = FastAPI(
    title="SecureStack API",
    description="Unified DevSecOps platform providing API security testing, compliance automation, dependency risk management, and SBOM generation. Built for engineering teams who want to ship secure code without compromising velocity.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(api_security.router, prefix="/api/v1", tags=["API Security"])
app.include_router(compliance.router, prefix="/api/v1", tags=["Compliance"])
app.include_router(dependencies.router, prefix="/api/v1", tags=["Dependencies"])
app.include_router(sbom.router, prefix="/api/v1", tags=["SBOM"])


@app.get("/")
async def root():
    return {
        "name": "SecureStack",
        "message": "Unified DevSecOps Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "modules": [
            "API Security Testing",
            "Compliance-as-Code",
            "Dependency Management",
            "SBOM Generation"
        ]
    }

