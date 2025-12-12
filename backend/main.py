from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging

from database import engine, Base, get_db
from routers import (
    api_security, compliance, dependencies, sbom, health,
    auth, users, teams, notifications, projects, webhooks,
    containers, infrastructure, scheduled_scans, reports,
    sbom_comparison, policy_templates, audit
)
from middleware.audit import AuditLogMiddleware
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

app.add_middleware(AuditLogMiddleware)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


app.include_router(health.router, prefix="/api/v1", tags=["Health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/v1", tags=["Users"])
app.include_router(teams.router, prefix="/api/v1", tags=["Teams"])
app.include_router(projects.router, prefix="/api/v1", tags=["Projects"])
app.include_router(notifications.router, prefix="/api/v1", tags=["Notifications"])
app.include_router(webhooks.router, prefix="/api/v1", tags=["Webhooks"])
app.include_router(api_security.router, prefix="/api/v1", tags=["API Security"])
app.include_router(compliance.router, prefix="/api/v1", tags=["Compliance"])
app.include_router(dependencies.router, prefix="/api/v1", tags=["Dependencies"])
app.include_router(sbom.router, prefix="/api/v1", tags=["SBOM"])
app.include_router(containers.router, prefix="/api/v1", tags=["Containers"])
app.include_router(infrastructure.router, prefix="/api/v1", tags=["Infrastructure"])
app.include_router(scheduled_scans.router, prefix="/api/v1", tags=["Scheduled Scans"])
app.include_router(reports.router, prefix="/api/v1", tags=["Reports"])
app.include_router(sbom_comparison.router, prefix="/api/v1", tags=["SBOM"])
app.include_router(policy_templates.router, prefix="/api/v1", tags=["Policy Templates"])
app.include_router(audit.router, prefix="/api/v1", tags=["Audit"])


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

