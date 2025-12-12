from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from database import get_db, ContainerScan, User
from auth import get_current_active_user
from modules.container_scanner import ContainerScanner

router = APIRouter()


class ContainerScanRequest(BaseModel):
    image_name: str
    image_tag: str = "latest"
    project_id: Optional[int] = None


class ContainerScanResponse(BaseModel):
    id: int
    image_name: str
    image_tag: str
    risk_score: float
    vulnerability_count: int
    created_at: str

    class Config:
        from_attributes = True


@router.post("/containers/scan", response_model=ContainerScanResponse)
async def scan_container(
    scan_data: ContainerScanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    scanner = ContainerScanner()
    result = await scanner.scan_image(
        image_name=scan_data.image_name,
        image_tag=scan_data.image_tag
    )
    
    scan = ContainerScan(
        image_name=scan_data.image_name,
        image_tag=scan_data.image_tag,
        digest=result.get("digest"),
        vulnerabilities=result.get("vulnerabilities", []),
        risk_score=result.get("risk_score", 0.0),
        user_id=current_user.id,
        project_id=scan_data.project_id
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    
    return ContainerScanResponse(
        id=scan.id,
        image_name=scan.image_name,
        image_tag=scan.image_tag,
        risk_score=scan.risk_score,
        vulnerability_count=len(scan.vulnerabilities) if scan.vulnerabilities else 0,
        created_at=scan.created_at.isoformat()
    )


@router.get("/containers/scans", response_model=List[ContainerScanResponse])
async def list_container_scans(
    project_id: Optional[int] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(ContainerScan).filter(ContainerScan.user_id == current_user.id)
    if project_id:
        query = query.filter(ContainerScan.project_id == project_id)
    
    scans = query.order_by(ContainerScan.created_at.desc()).offset(offset).limit(limit).all()
    return [
        ContainerScanResponse(
            id=scan.id,
            image_name=scan.image_name,
            image_tag=scan.image_tag,
            risk_score=scan.risk_score,
            vulnerability_count=len(scan.vulnerabilities) if scan.vulnerabilities else 0,
            created_at=scan.created_at.isoformat()
        )
        for scan in scans
    ]

