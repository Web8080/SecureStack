from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import croniter

from database import get_db, ScheduledScan, User
from auth import get_current_active_user

router = APIRouter()


class ScheduledScanCreate(BaseModel):
    name: str
    scan_type: str
    schedule: str
    config: Dict[str, Any]
    project_id: Optional[int] = None


class ScheduledScanResponse(BaseModel):
    id: int
    name: str
    scan_type: str
    schedule: str
    enabled: bool
    next_run: Optional[str]
    created_at: str

    class Config:
        from_attributes = True


@router.post("/scheduled-scans", response_model=ScheduledScanResponse)
async def create_scheduled_scan(
    scan_data: ScheduledScanCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    try:
        croniter.croniter(scan_data.schedule)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid cron schedule format")
    
    from datetime import datetime
    cron = croniter.croniter(scan_data.schedule, datetime.utcnow())
    next_run = cron.get_next(datetime)
    
    scheduled_scan = ScheduledScan(
        name=scan_data.name,
        scan_type=scan_data.scan_type,
        schedule=scan_data.schedule,
        config=scan_data.config,
        user_id=current_user.id,
        project_id=scan_data.project_id,
        next_run=next_run
    )
    db.add(scheduled_scan)
    db.commit()
    db.refresh(scheduled_scan)
    
    return ScheduledScanResponse(
        id=scheduled_scan.id,
        name=scheduled_scan.name,
        scan_type=scheduled_scan.scan_type,
        schedule=scheduled_scan.schedule,
        enabled=scheduled_scan.enabled,
        next_run=scheduled_scan.next_run.isoformat() if scheduled_scan.next_run else None,
        created_at=scheduled_scan.created_at.isoformat()
    )


@router.get("/scheduled-scans", response_model=List[ScheduledScanResponse])
async def list_scheduled_scans(
    project_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(ScheduledScan).filter(ScheduledScan.user_id == current_user.id)
    if project_id:
        query = query.filter(ScheduledScan.project_id == project_id)
    
    scans = query.all()
    return [
        ScheduledScanResponse(
            id=scan.id,
            name=scan.name,
            scan_type=scan.scan_type,
            schedule=scan.schedule,
            enabled=scan.enabled,
            next_run=scan.next_run.isoformat() if scan.next_run else None,
            created_at=scan.created_at.isoformat()
        )
        for scan in scans
    ]


@router.post("/scheduled-scans/{scan_id}/toggle")
async def toggle_scheduled_scan(
    scan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    scan = db.query(ScheduledScan).filter(
        ScheduledScan.id == scan_id,
        ScheduledScan.user_id == current_user.id
    ).first()
    
    if not scan:
        raise HTTPException(status_code=404, detail="Scheduled scan not found")
    
    scan.enabled = not scan.enabled
    db.commit()
    
    return {"enabled": scan.enabled}

