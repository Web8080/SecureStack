from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
from database import SessionLocal, AuditLog
from datetime import datetime


class AuditLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        db: Session = SessionLocal()
        
        try:
            response = await call_next(request)
            
            user_id = None
            if hasattr(request.state, "user"):
                user_id = request.state.user.id if request.state.user else None
            
            if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
                action = f"{request.method} {request.url.path}"
                resource_type = request.url.path.split("/")[-2] if len(request.url.path.split("/")) > 2 else "unknown"
                
                audit_log = AuditLog(
                    user_id=user_id,
                    action=action,
                    resource_type=resource_type,
                    ip_address=request.client.host if request.client else None,
                    user_agent=request.headers.get("user-agent"),
                    created_at=datetime.utcnow()
                )
                db.add(audit_log)
                db.commit()
            
            return response
        finally:
            db.close()

