from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://devsecops:devsecops_password@localhost:5432/devsecops"
    REDIS_URL: str = "redis://localhost:6379"
    SECRET_KEY: str = "change-me-in-production"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # Authentication
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # External API endpoints
    NVD_API_URL: str = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    OSV_API_URL: str = "https://api.osv.dev/v1/query"
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


