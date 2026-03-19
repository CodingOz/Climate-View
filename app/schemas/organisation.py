from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from app.models.organisation import OrgType


class OrganisationBase(BaseModel):
    name: str
    org_type: OrgType
    country: str
    description: Optional[str] = None
    founding_date: Optional[date] = None
    website: Optional[str] = None
    member_count: Optional[int] = None
    is_active: bool = True


class OrganisationCreate(OrganisationBase):
    pass


class OrganisationUpdate(OrganisationBase):
    pass


class OrganisationResponse(OrganisationBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}