from fastapi import APIRouter, HTTPException, Depends, Response
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from database import get_db, SBOMDocument
from modules.sbom import SBOMGenerator

router = APIRouter()


class SBOMGenerateRequest(BaseModel):
    project_name: str
    version: str
    format: str = "cyclonedx"
    dependencies: List[Dict[str, Any]]
    metadata: Optional[Dict[str, Any]] = None
    include_attestation: bool = True


class SBOMGenerateResponse(BaseModel):
    sbom_id: int
    project_name: str
    version: str
    format: str
    created_at: str


@router.post("/sbom/generate", response_model=SBOMGenerateResponse)
async def generate_sbom(
    request: SBOMGenerateRequest,
    db: Session = Depends(get_db)
):
    try:
        generator = SBOMGenerator()
        sbom_data = await generator.generate_sbom(
            project_name=request.project_name,
            version=request.version,
            format_type=request.format,
            dependencies=request.dependencies,
            metadata=request.metadata or {},
            include_attestation=request.include_attestation
        )
        
        db_sbom = SBOMDocument(
            project_name=request.project_name,
            version=request.version,
            format=request.format,
            content=sbom_data.get("content", ""),
            attestation=sbom_data.get("attestation", "")
        )
        db.add(db_sbom)
        db.commit()
        db.refresh(db_sbom)
        
        return SBOMGenerateResponse(
            sbom_id=db_sbom.id,
            project_name=db_sbom.project_name,
            version=db_sbom.version,
            format=db_sbom.format,
            created_at=db_sbom.created_at.isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SBOM generation failed: {str(e)}")


@router.get("/sbom/documents")
async def list_sboms(
    project_name: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(SBOMDocument)
    
    if project_name:
        query = query.filter(SBOMDocument.project_name == project_name)
    
    sboms = query.order_by(SBOMDocument.created_at.desc()).offset(offset).limit(limit).all()
    total = query.count()
    
    return {
        "sboms": [
            {
                "id": sbom.id,
                "project_name": sbom.project_name,
                "version": sbom.version,
                "format": sbom.format,
                "has_attestation": bool(sbom.attestation),
                "created_at": sbom.created_at.isoformat()
            }
            for sbom in sboms
        ],
        "total": total
    }


@router.get("/sbom/documents/{sbom_id}")
async def get_sbom(sbom_id: int, db: Session = Depends(get_db)):
    sbom = db.query(SBOMDocument).filter(SBOMDocument.id == sbom_id).first()
    if not sbom:
        raise HTTPException(status_code=404, detail="SBOM document not found")
    
    return {
        "id": sbom.id,
        "project_name": sbom.project_name,
        "version": sbom.version,
        "format": sbom.format,
        "content": sbom.content,
        "attestation": sbom.attestation,
        "created_at": sbom.created_at.isoformat()
    }


@router.get("/sbom/documents/{sbom_id}/download")
async def download_sbom(sbom_id: int, db: Session = Depends(get_db)):
    sbom = db.query(SBOMDocument).filter(SBOMDocument.id == sbom_id).first()
    if not sbom:
        raise HTTPException(status_code=404, detail="SBOM document not found")
    
    content_type = "application/json"
    if sbom.format == "spdx":
        content_type = "text/spdx"
    
    return Response(
        content=sbom.content,
        media_type=content_type,
        headers={
            "Content-Disposition": f"attachment; filename={sbom.project_name}-{sbom.version}.{sbom.format}.json"
        }
    )


