from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
import json

from database import get_db, SBOMDocument, User
from auth import get_current_active_user

router = APIRouter()


class SBOMComparisonResponse(BaseModel):
    added: list
    removed: list
    updated: list
    unchanged: list
    summary: dict


@router.get("/sbom/compare/{sbom_id1}/{sbom_id2}")
async def compare_sboms(
    sbom_id1: int,
    sbom_id2: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    sbom1 = db.query(SBOMDocument).filter(SBOMDocument.id == sbom_id1).first()
    sbom2 = db.query(SBOMDocument).filter(SBOMDocument.id == sbom_id2).first()
    
    if not sbom1 or not sbom2:
        raise HTTPException(status_code=404, detail="SBOM not found")
    
    content1 = json.loads(sbom1.content)
    content2 = json.loads(sbom2.content)
    
    components1 = {c.get("purl", c.get("name", "")): c for c in content1.get("components", [])}
    components2 = {c.get("purl", c.get("name", "")): c for c in content2.get("components", [])}
    
    added = [components2[k] for k in components2.keys() - components1.keys()]
    removed = [components1[k] for k in components1.keys() - components2.keys()]
    
    updated = []
    unchanged = []
    for key in components1.keys() & components2.keys():
        if components1[key] != components2[key]:
            updated.append({
                "component": key,
                "old": components1[key],
                "new": components2[key]
            })
        else:
            unchanged.append(components1[key])
    
    return SBOMComparisonResponse(
        added=added,
        removed=removed,
        updated=updated,
        unchanged=unchanged,
        summary={
            "total_components_old": len(components1),
            "total_components_new": len(components2),
            "added_count": len(added),
            "removed_count": len(removed),
            "updated_count": len(updated),
            "unchanged_count": len(unchanged)
        }
    )

