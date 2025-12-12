from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from database import get_db, InfrastructureScan, User
from auth import get_current_active_user
from modules.infrastructure_scanner import InfrastructureScanner

router = APIRouter()


class InfrastructureScanRequest(BaseModel):
    scan_type: str
    target: str
    config: Optional[Dict[str, Any]] = None
    project_id: Optional[int] = None


class InfrastructureScanResponse(BaseModel):
    id: int
    scan_type: str
    target: str
    risk_score: float
    findings_count: int
    created_at: str

    class Config:
        from_attributes = True


@router.post("/infrastructure/scan", response_model=InfrastructureScanResponse)
async def scan_infrastructure(
    scan_data: InfrastructureScanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    scanner = InfrastructureScanner()
    result = await scanner.scan(
        scan_type=scan_data.scan_type,
        target=scan_data.target,
        config=scan_data.config or {}
    )
    
    scan = InfrastructureScan(
        scan_type=scan_data.scan_type,
        target=scan_data.target,
        findings=result.get("findings", []),
        risk_score=result.get("risk_score", 0.0),
        user_id=current_user.id,
        project_id=scan_data.project_id
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    
    return InfrastructureScanResponse(
        id=scan.id,
        scan_type=scan.scan_type,
        target=scan.target,
        risk_score=scan.risk_score,
        findings_count=len(scan.findings) if scan.findings else 0,
        created_at=scan.created_at.isoformat()
    )


@router.get("/infrastructure/scans", response_model=List[InfrastructureScanResponse])
async def list_infrastructure_scans(
    scan_type: Optional[str] = None,
    project_id: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(InfrastructureScan).filter(InfrastructureScan.user_id == current_user.id)
    if scan_type:
        query = query.filter(InfrastructureScan.scan_type == scan_type)
    if project_id:
        query = query.filter(InfrastructureScan.project_id == project_id)
    
    scans = query.order_by(InfrastructureScan.created_at.desc()).offset(offset).limit(limit).all()
    return [
        InfrastructureScanResponse(
            id=scan.id,
            scan_type=scan.scan_type,
            target=scan.target,
            risk_score=scan.risk_score,
            findings_count=len(scan.findings) if scan.findings else 0,
            created_at=scan.created_at.isoformat()
        )
        for scan in scans
    ]

