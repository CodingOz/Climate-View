from pydantic import BaseModel
from typing import Optional
from app.models.threat import ThreatType, ThreatStatus
from app.models.organisation import OrgType
from app.models.campaign import CampaignType, CampaignStatus


class ThreatSearchResult(BaseModel):
    id: str
    name: str
    threat_type: ThreatType
    status: ThreatStatus
    country: str
    estimated_co2_impact_tonnes: Optional[float] = None
    result_type: str = "threat"


class OrganisationSearchResult(BaseModel):
    id: str
    name: str
    org_type: OrgType
    country: str
    description: Optional[str] = None
    result_type: str = "organisation"


class CampaignSearchResult(BaseModel):
    id: str
    campaign_name: str
    campaign_type: CampaignType
    status: CampaignStatus
    outcome_summary: Optional[str] = None
    result_type: str = "campaign"


class SearchResponse(BaseModel):
    query: str
    total_results: int
    threats: list[ThreatSearchResult]
    organisations: list[OrganisationSearchResult]
    campaigns: list[CampaignSearchResult]