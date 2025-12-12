from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from database import get_db, ComplianceCheck
from modules.compliance import ComplianceEngine

router = APIRouter()


class ComplianceCheckRequest(BaseModel):
    framework: str
    policy_name: Optional[str] = None
    resource_type: str
    resource_data: Dict[str, Any]
    custom_policy: Optional[str] = None


class ComplianceCheckResponse(BaseModel):
    check_id: int
    framework: str
    policy_name: str
    status: str
    details: Dict[str, Any]
    created_at: str


@router.post("/compliance/check", response_model=ComplianceCheckResponse)
async def run_compliance_check(
    request: ComplianceCheckRequest,
    db: Session = Depends(get_db)
):
    try:
        engine = ComplianceEngine()
        result = await engine.check_compliance(
            framework=request.framework,
            policy_name=request.policy_name,
            resource_type=request.resource_type,
            resource_data=request.resource_data,
            custom_policy=request.custom_policy
        )
        
        db_check = ComplianceCheck(
            framework=request.framework,
            policy_name=result.get("policy_name", request.policy_name or "default"),
            status=result.get("status", "unknown"),
            details=result,
            evidence=result.get("evidence", {})
        )
        db.add(db_check)
        db.commit()
        db.refresh(db_check)
        
        return ComplianceCheckResponse(
            check_id=db_check.id,
            framework=db_check.framework,
            policy_name=db_check.policy_name,
            status=db_check.status,
            details=db_check.details,
            created_at=db_check.created_at.isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Compliance check failed: {str(e)}")


@router.get("/compliance/checks")
async def list_checks(
    framework: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(ComplianceCheck)
    
    if framework:
        query = query.filter(ComplianceCheck.framework == framework)
    if status:
        query = query.filter(ComplianceCheck.status == status)
    
    checks = query.order_by(ComplianceCheck.created_at.desc()).offset(offset).limit(limit).all()
    total = query.count()
    
    return {
        "checks": [
            {
                "id": check.id,
                "framework": check.framework,
                "policy_name": check.policy_name,
                "status": check.status,
                "created_at": check.created_at.isoformat()
            }
            for check in checks
        ],
        "total": total
    }


@router.get("/compliance/checks/{check_id}")
async def get_check(check_id: int, db: Session = Depends(get_db)):
    check = db.query(ComplianceCheck).filter(ComplianceCheck.id == check_id).first()
    if not check:
        raise HTTPException(status_code=404, detail="Compliance check not found")
    
    return {
        "id": check.id,
        "framework": check.framework,
        "policy_name": check.policy_name,
        "status": check.status,
        "details": check.details,
        "evidence": check.evidence,
        "created_at": check.created_at.isoformat()
    }


@router.get("/compliance/frameworks")
async def list_frameworks():
    return {
        "frameworks": [
            {
                "name": "SOC 2",
                "description": "Service Organization Control 2 compliance",
                "policies": ["access_control", "encryption", "monitoring", "incident_response"]
            },
            {
                "name": "PCI-DSS",
                "description": "Payment Card Industry Data Security Standard",
                "policies": ["data_encryption", "access_control", "network_security", "vulnerability_management"]
            },
            {
                "name": "GDPR",
                "description": "General Data Protection Regulation",
                "policies": ["data_encryption", "access_control", "data_retention", "privacy_by_design"]
            }
        ]
    }


