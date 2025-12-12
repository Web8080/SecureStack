from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from database import get_db, Project, User, Team
from auth import get_current_active_user

router = APIRouter()


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    team_id: Optional[int] = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    team_id: Optional[int]
    owner_id: int
    created_at: str

    class Config:
        from_attributes = True


@router.post("/projects", response_model=ProjectResponse)
async def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if db.query(Project).filter(Project.name == project_data.name).first():
        raise HTTPException(status_code=400, detail="Project name already exists")
    
    if project_data.team_id:
        team = db.query(Team).filter(Team.id == project_data.team_id).first()
        if not team or current_user not in team.members:
            raise HTTPException(status_code=403, detail="Not a team member")
    
    project = Project(
        name=project_data.name,
        description=project_data.description,
        team_id=project_data.team_id,
        owner_id=current_user.id
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.get("/projects", response_model=List[ProjectResponse])
async def list_projects(
    team_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    query = db.query(Project).filter(
        (Project.owner_id == current_user.id) |
        (Project.team_id.in_([t.id for t in current_user.teams]))
    )
    if team_id:
        query = query.filter(Project.team_id == team_id)
    projects = query.all()
    return projects


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.owner_id != current_user.id:
        if project.team_id:
            team = db.query(Team).filter(Team.id == project.team_id).first()
            if not team or current_user not in team.members:
                raise HTTPException(status_code=403, detail="Access denied")
    
    return project

