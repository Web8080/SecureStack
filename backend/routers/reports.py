from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime, timedelta
import json
import csv
import io

from database import (
    get_db, User, APISecurityTest, ComplianceCheck,
    DependencyScan, ContainerScan, InfrastructureScan
)
from auth import get_current_active_user

router = APIRouter()


@router.get("/reports/dashboard")
async def get_dashboard_stats(
    project_id: Optional[int] = None,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    since = datetime.utcnow() - timedelta(days=days)
    
    base_filter = []
    if project_id:
        base_filter = [APISecurityTest.project_id == project_id]
    
    api_tests = db.query(APISecurityTest).filter(
        APISecurityTest.created_at >= since,
        *base_filter
    ).count()
    
    api_passed = db.query(APISecurityTest).filter(
        APISecurityTest.status == "passed",
        APISecurityTest.created_at >= since,
        *base_filter
    ).count()
    
    compliance_checks = db.query(ComplianceCheck).filter(
        ComplianceCheck.created_at >= since
    ).count()
    
    compliance_passed = db.query(ComplianceCheck).filter(
        ComplianceCheck.status == "passed",
        ComplianceCheck.created_at >= since
    ).count()
    
    dependency_scans = db.query(DependencyScan).filter(
        DependencyScan.created_at >= since
    ).count()
    
    high_risk_deps = db.query(DependencyScan).filter(
        DependencyScan.risk_score >= 7.0,
        DependencyScan.created_at >= since
    ).count()
    
    container_scans = db.query(ContainerScan).filter(
        ContainerScan.created_at >= since
    ).count()
    
    high_risk_containers = db.query(ContainerScan).filter(
        ContainerScan.risk_score >= 7.0,
        ContainerScan.created_at >= since
    ).count()
    
    return {
        "period_days": days,
        "api_security": {
            "total_tests": api_tests,
            "passed": api_passed,
            "failed": api_tests - api_passed,
            "pass_rate": (api_passed / api_tests * 100) if api_tests > 0 else 0
        },
        "compliance": {
            "total_checks": compliance_checks,
            "passed": compliance_passed,
            "failed": compliance_checks - compliance_passed,
            "pass_rate": (compliance_passed / compliance_checks * 100) if compliance_checks > 0 else 0
        },
        "dependencies": {
            "total_scans": dependency_scans,
            "high_risk": high_risk_deps,
            "risk_percentage": (high_risk_deps / dependency_scans * 100) if dependency_scans > 0 else 0
        },
        "containers": {
            "total_scans": container_scans,
            "high_risk": high_risk_containers,
            "risk_percentage": (high_risk_containers / container_scans * 100) if container_scans > 0 else 0
        }
    }


@router.get("/reports/export/csv")
async def export_csv_report(
    report_type: str,
    project_id: Optional[int] = None,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    since = datetime.utcnow() - timedelta(days=days)
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    if report_type == "api_security":
        writer.writerow(["ID", "Endpoint", "Method", "Status", "Created At"])
        tests = db.query(APISecurityTest).filter(
            APISecurityTest.created_at >= since
        ).all()
        for test in tests:
            writer.writerow([
                test.id, test.endpoint, test.method, test.status,
                test.created_at.isoformat()
            ])
    
    elif report_type == "dependencies":
        writer.writerow(["ID", "Package", "Version", "Risk Score", "Vulnerabilities", "Created At"])
        scans = db.query(DependencyScan).filter(
            DependencyScan.created_at >= since
        ).all()
        for scan in scans:
            writer.writerow([
                scan.id, scan.package_name, scan.version, scan.risk_score,
                len(scan.vulnerabilities) if scan.vulnerabilities else 0,
                scan.created_at.isoformat()
            ])
    
    csv_content = output.getvalue()
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=report_{report_type}_{datetime.utcnow().date()}.csv"}
    )


@router.get("/reports/export/json")
async def export_json_report(
    report_type: str,
    project_id: Optional[int] = None,
    days: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    since = datetime.utcnow() - timedelta(days=days)
    
    data = {}
    
    if report_type == "api_security":
        tests = db.query(APISecurityTest).filter(
            APISecurityTest.created_at >= since
        ).all()
        data = [
            {
                "id": test.id,
                "endpoint": test.endpoint,
                "method": test.method,
                "status": test.status,
                "created_at": test.created_at.isoformat()
            }
            for test in tests
        ]
    
    elif report_type == "dependencies":
        scans = db.query(DependencyScan).filter(
            DependencyScan.created_at >= since
        ).all()
        data = [
            {
                "id": scan.id,
                "package_name": scan.package_name,
                "version": scan.version,
                "risk_score": scan.risk_score,
                "vulnerabilities": scan.vulnerabilities,
                "created_at": scan.created_at.isoformat()
            }
            for scan in scans
        ]
    
    return Response(
        content=json.dumps(data, indent=2),
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=report_{report_type}_{datetime.utcnow().date()}.json"}
    )

