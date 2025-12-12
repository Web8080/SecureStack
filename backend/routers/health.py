from fastapi import APIRouter
from datetime import datetime
import psutil
import os

router = APIRouter()


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "SecureStack API",
        "version": "1.0.0"
    }


@router.get("/health/detailed")
async def detailed_health():
    process = psutil.Process(os.getpid())
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "SecureStack API",
        "version": "1.0.0",
        "system": {
            "cpu_percent": process.cpu_percent(),
            "memory_mb": process.memory_info().rss / 1024 / 1024,
            "uptime_seconds": (datetime.utcnow() - datetime.fromtimestamp(process.create_time())).total_seconds()
        }
    }


