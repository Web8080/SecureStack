from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from database import get_db, DependencyScan
from modules.dependencies import DependencyAnalyzer

router = APIRouter()


class DependencyScanRequest(BaseModel):
    package_name: str
    version: str
    ecosystem: Optional[str] = "npm"
    include_dev: bool = False


class DependencyScanResponse(BaseModel):
    scan_id: int
    package_name: str
    version: str
    risk_score: float
    vulnerabilities: List[Dict[str, Any]]
    created_at: str


@router.post("/dependencies/scan", response_model=DependencyScanResponse)
async def scan_dependency(
    request: DependencyScanRequest,
    db: Session = Depends(get_db)
):
    try:
        analyzer = DependencyAnalyzer()
        result = await analyzer.analyze_package(
            package_name=request.package_name,
            version=request.version,
            ecosystem=request.ecosystem
        )
        
        db_scan = DependencyScan(
            package_name=request.package_name,
            version=request.version,
            risk_score=result.get("risk_score", 0.0),
            vulnerabilities=result.get("vulnerabilities", [])
        )
        db.add(db_scan)
        db.commit()
        db.refresh(db_scan)
        
        return DependencyScanResponse(
            scan_id=db_scan.id,
            package_name=db_scan.package_name,
            version=db_scan.version,
            risk_score=db_scan.risk_score,
            vulnerabilities=db_scan.vulnerabilities,
            created_at=db_scan.created_at.isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Dependency scan failed: {str(e)}")


@router.post("/dependencies/scan-batch")
async def scan_dependencies_batch(
    packages: List[Dict[str, str]],
    db: Session = Depends(get_db)
):
    results = []
    analyzer = DependencyAnalyzer()
    
    for package in packages:
        try:
            result = await analyzer.analyze_package(
                package_name=package.get("name"),
                version=package.get("version", "latest"),
                ecosystem=package.get("ecosystem", "npm")
            )
            
            db_scan = DependencyScan(
                package_name=package.get("name"),
                version=package.get("version", "latest"),
                risk_score=result.get("risk_score", 0.0),
                vulnerabilities=result.get("vulnerabilities", [])
            )
            db.add(db_scan)
            results.append(result)
        except Exception as e:
            results.append({
                "package_name": package.get("name"),
                "error": str(e)
            })
    
    db.commit()
    
    return {
        "scanned": len(results),
        "results": results
    }


@router.get("/dependencies/scans")
async def list_scans(
    package_name: Optional[str] = None,
    min_risk_score: Optional[float] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(DependencyScan)
    
    if package_name:
        query = query.filter(DependencyScan.package_name == package_name)
    if min_risk_score is not None:
        query = query.filter(DependencyScan.risk_score >= min_risk_score)
    
    scans = query.order_by(DependencyScan.risk_score.desc()).offset(offset).limit(limit).all()
    total = query.count()
    
    return {
        "scans": [
            {
                "id": scan.id,
                "package_name": scan.package_name,
                "version": scan.version,
                "risk_score": scan.risk_score,
                "vulnerability_count": len(scan.vulnerabilities) if scan.vulnerabilities else 0,
                "created_at": scan.created_at.isoformat()
            }
            for scan in scans
        ],
        "total": total
    }


@router.get("/dependencies/scans/{scan_id}")
async def get_scan(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(DependencyScan).filter(DependencyScan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Dependency scan not found")
    
    return {
        "id": scan.id,
        "package_name": scan.package_name,
        "version": scan.version,
        "risk_score": scan.risk_score,
        "vulnerabilities": scan.vulnerabilities,
        "created_at": scan.created_at.isoformat()
    }


