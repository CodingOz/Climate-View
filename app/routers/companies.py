from fastapi import APIRouter, Depends, HTTPException, status, Request
from app.core.limiter import limiter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.company import Company, CompanySector
from app.schemas.company import CompanyCreate, CompanyUpdate, CompanyResponse
from typing import List, Optional
import uuid

router = APIRouter(prefix="/companies", tags=["Companies"])


@router.get("/", response_model=List[CompanyResponse])
@limiter.limit("100/minute")
async def get_companies(
    request: Request,
    sector: Optional[CompanySector] = None,
    country: Optional[str] = None,
    is_paris_signatory: Optional[bool] = None,
    max_esg_score: Optional[float] = None,
    min_emissions: Optional[float] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    query = select(Company)

    if sector:
        query = query.where(Company.sector == sector)
    if country:
        query = query.where(Company.country_of_registration.ilike(f"%{country}%"))
    if is_paris_signatory is not None:
        query = query.where(Company.is_paris_signatory == is_paris_signatory)
    if max_esg_score is not None:
        query = query.where(Company.esg_score <= max_esg_score)
    if min_emissions is not None:
        query = query.where(Company.annual_emissions_mtonnes >= min_emissions)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("20/minute")
async def create_company(request: Request, company: CompanyCreate, db: AsyncSession = Depends(get_db)):
    # Check for duplicate name
    existing = await db.execute(select(Company).where(Company.name == company.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Company with this name already exists")
    db_company = Company(id=str(uuid.uuid4()), **company.model_dump())
    db.add(db_company)
    await db.commit()
    await db.refresh(db_company)
    return db_company


@router.get("/{company_id}", response_model=CompanyResponse)
@limiter.limit("100/minute")
async def get_company(request: Request, company_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.put("/{company_id}", response_model=CompanyResponse)
@limiter.limit("20/minute")
async def update_company(request: Request, company_id: str, company_data: CompanyUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    for key, value in company_data.model_dump().items():
        setattr(company, key, value)
    await db.commit()
    await db.refresh(company)
    return company


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("20/minute")
async def delete_company(request: Request, company_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    await db.delete(company)
    await db.commit()


@router.get("/{company_id}/threats", response_model=List[dict])
@limiter.limit("100/minute")
async def get_company_threats(request: Request, company_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Company).where(Company.id == company_id))
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    from app.models.threat_company import ThreatCompany
    from app.models.threat import Threat
    assoc_result = await db.execute(
        select(ThreatCompany, Threat)
        .join(Threat, ThreatCompany.threat_id == Threat.id)
        .where(ThreatCompany.company_id == company_id)
    )
    rows = assoc_result.all()
    return [
        {"role": row.ThreatCompany.role, "threat_id": row.Threat.id, "threat_name": row.Threat.name, "status": row.Threat.status}
        for row in rows
    ]