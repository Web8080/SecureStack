from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
import httpx
import hmac
import hashlib
import json

from database import get_db, Webhook, User
from auth import get_current_active_user

router = APIRouter()


class WebhookCreate(BaseModel):
    url: str
    events: List[str]
    project_id: int = None


class WebhookResponse(BaseModel):
    id: int
    url: str
    events: List[str]
    active: bool
    created_at: str

    class Config:
        from_attributes = True


@router.post("/webhooks", response_model=WebhookResponse)
async def create_webhook(
    webhook_data: WebhookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    import secrets
    secret = secrets.token_urlsafe(32)
    
    webhook = Webhook(
        url=webhook_data.url,
        events=webhook_data.events,
        secret=secret,
        user_id=current_user.id,
        project_id=webhook_data.project_id
    )
    db.add(webhook)
    db.commit()
    db.refresh(webhook)
    return webhook


@router.get("/webhooks", response_model=List[WebhookResponse])
async def list_webhooks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    webhooks = db.query(Webhook).filter(Webhook.user_id == current_user.id).all()
    return webhooks


async def trigger_webhook(webhook: Webhook, event: str, payload: dict):
    if not webhook.active or event not in webhook.events:
        return
    
    try:
        payload_json = json.dumps(payload)
        signature = hmac.new(
            webhook.secret.encode(),
            payload_json.encode(),
            hashlib.sha256
        ).hexdigest()
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            await client.post(
                webhook.url,
                json=payload,
                headers={
                    "X-SecureStack-Signature": signature,
                    "X-SecureStack-Event": event
                }
            )
    except Exception as e:
        print(f"Webhook delivery failed: {e}")

