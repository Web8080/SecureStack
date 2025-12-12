from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from database import get_db, PolicyTemplate, User
from auth import get_current_active_user

router = APIRouter()


class PolicyTemplateCreate(BaseModel):
    name: str
    framework: str
    description: Optional[str] = None
    policy_content: Dict[str, Any]
    is_public: bool = False


class PolicyTemplateResponse(BaseModel):
    id: int
    name: str
    framework: str
    description: Optional[str]
    is_public: bool
    created_at: str

    class Config:
        from_attributes = True


@router.post("/policy-templates", response_model=PolicyTemplateResponse)
async def create_policy_template(
    template_data: PolicyTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    template = PolicyTemplate(
        name=template_data.name,
        framework=template_data.framework,
        description=template_data.description,
        policy_content=template_data.policy_content,
        is_public=template_data.is_public,
        created_by=current_user.id
    )
    db.add(template)
    db.commit()
    db.refresh(template)
    
    return PolicyTemplateResponse(
        id=template.id,
        name=template.name,
        framework=template.framework,
        description=template.description,
        is_public=template.is_public,
        created_at=template.created_at.isoformat()
    )


@router.get("/policy-templates", response_model=List[PolicyTemplateResponse])
async def list_policy_templates(
    framework: Optional[str] = None,
    public_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(PolicyTemplate)
    
    if public_only:
        query = query.filter(PolicyTemplate.is_public == True)
    else:
        query = query.filter(
            (PolicyTemplate.is_public == True) |
            (PolicyTemplate.created_by == current_user.id)
        )
    
    if framework:
        query = query.filter(PolicyTemplate.framework == framework)
    
    templates = query.all()
    return templates


@router.get("/policy-templates/{template_id}")
async def get_policy_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    template = db.query(PolicyTemplate).filter(PolicyTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Policy template not found")
    
    if not template.is_public and template.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        "id": template.id,
        "name": template.name,
        "framework": template.framework,
        "description": template.description,
        "policy_content": template.policy_content,
        "is_public": template.is_public,
        "created_at": template.created_at.isoformat()
    }

