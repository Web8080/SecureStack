from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from database import get_db, Team, User
from auth import get_current_active_user

router = APIRouter()


class TeamCreate(BaseModel):
    name: str
    description: str = None


class TeamResponse(BaseModel):
    id: int
    name: str
    description: str
    owner_id: int
    created_at: str

    class Config:
        from_attributes = True


@router.post("/teams", response_model=TeamResponse)
async def create_team(
    team_data: TeamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    if db.query(Team).filter(Team.name == team_data.name).first():
        raise HTTPException(status_code=400, detail="Team name already exists")
    
    team = Team(
        name=team_data.name,
        description=team_data.description,
        owner_id=current_user.id
    )
    team.members.append(current_user)
    db.add(team)
    db.commit()
    db.refresh(team)
    return team


@router.get("/teams", response_model=List[TeamResponse])
async def list_teams(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    teams = db.query(Team).filter(Team.members.any(id=current_user.id)).all()
    return teams


@router.get("/teams/{team_id}", response_model=TeamResponse)
async def get_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    if current_user not in team.members and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Not a team member")
    
    return team

