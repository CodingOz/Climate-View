from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from app.models.campaign import CampaignType, CampaignStatus


class CampaignBase(BaseModel):
    campaign_name: str
    campaign_type: CampaignType
    status: CampaignStatus = CampaignStatus.ACTIVE
    organisation_id: str
    threat_id: str
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    outcome_summary: Optional[str] = None
    signatures_count: Optional[int] = None


class CampaignCreate(CampaignBase):
    pass


class CampaignUpdate(CampaignBase):
    pass


class CampaignResponse(CampaignBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}