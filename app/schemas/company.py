from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import datetime
from app.models.company import CompanySector


class CompanyBase(BaseModel):
    name: str
    sector: CompanySector
    country_of_registration: str
    description: Optional[str] = None
    esg_score: Optional[float] = None
    annual_emissions_mtonnes: Optional[float] = None
    is_paris_signatory: bool = False
    website: Optional[str] = None


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(CompanyBase):
    pass


class CompanyResponse(CompanyBase):
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}