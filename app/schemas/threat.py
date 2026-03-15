from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.threat import ThreatType, ThreatStatus

class ThreatBase(BaseModel):
    name: str
    threat_type: ThreatType
    status: ThreatStatus
    country: str
    region: Optional[str] = None
    description: Optional[str] = None
    estimated_co2_impact_tonnes: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    source_url: Optional[str] = None

class ThreatCreate(ThreatBase):
    pass

class ThreatUpdate(ThreatBase):
    pass

class ThreatResponse(ThreatBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}