from sqlalchemy.orm import Session
from database import Notification, User
from typing import Optional


def create_notification(
    db: Session,
    user_id: int,
    title: str,
    message: str,
    notification_type: str = "info"
):
    notification = Notification(
        user_id=user_id,
        title=title,
        message=message,
        type=notification_type
    )
    db.add(notification)
    db.commit()
    return notification


def notify_team(
    db: Session,
    team_id: int,
    title: str,
    message: str,
    notification_type: str = "info"
):
    from database import Team
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        return
    
    for user in team.members:
        create_notification(db, user.id, title, message, notification_type)

