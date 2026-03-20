from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.core.limiter import limiter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.campaign import Campaign
from app.models.threat import Threat
from app.models.organisation import Organisation
from app.schemas.campaign import CampaignCreate, CampaignUpdate, CampaignResponse
from typing import List
import uuid

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])

@router.get("/", response_model=List[CampaignResponse])
@limiter.limit("100/minute")
async def get_campaigns(request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Campaign))
    return result.scalars().all()


@router.post("/", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")
async def create_campaign(request: Request, campaign: CampaignCreate, db: AsyncSession = Depends(get_db)):
    # Validate threat exists
    threat = await db.execute(select(Threat).where(Threat.id == campaign.threat_id))
    if not threat.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Threat not found")
    # Validate organisation exists
    org = await db.execute(select(Organisation).where(Organisation.id == campaign.organisation_id))
    if not org.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Organisation not found")
    db_campaign = Campaign(id=str(uuid.uuid4()), **campaign.model_dump())
    db.add(db_campaign)
    await db.commit()
    await db.refresh(db_campaign)
    return db_campaign


@router.get("/{campaign_id}", response_model=CampaignResponse)
@limiter.limit("100/minute")
async def get_campaign(request: Request, campaign_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.put("/{campaign_id}", response_model=CampaignResponse)
@limiter.limit("20/minute")
async def update_campaign(request: Request, campaign_id: str, campaign_data: CampaignUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    for key, value in campaign_data.model_dump().items():
        setattr(campaign, key, value)
    await db.commit()
    await db.refresh(campaign)
    return campaign


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("20/minute")
async def delete_campaign(request: Request, campaign_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    await db.delete(campaign)
    await db.commit()