from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.organisation import Organisation
from app.schemas.organisation import OrganisationCreate, OrganisationUpdate, OrganisationResponse
from typing import List
import uuid

router = APIRouter(prefix="/organisations", tags=["Organisations"])


@router.get("/", response_model=List[OrganisationResponse])
async def get_organisations(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Organisation))
    return result.scalars().all()


@router.post("/", response_model=OrganisationResponse, status_code=status.HTTP_201_CREATED)
async def create_organisation(org: OrganisationCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Organisation).where(Organisation.name == org.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Organisation with this name already exists")
    db_org = Organisation(id=str(uuid.uuid4()), **org.model_dump())
    db.add(db_org)
    await db.commit()
    await db.refresh(db_org)
    return db_org


@router.get("/{org_id}", response_model=OrganisationResponse)
async def get_organisation(org_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Organisation).where(Organisation.id == org_id))
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organisation not found")
    return org


@router.put("/{org_id}", response_model=OrganisationResponse)
async def update_organisation(org_id: str, org_data: OrganisationUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Organisation).where(Organisation.id == org_id))
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organisation not found")
    for key, value in org_data.model_dump().items():
        setattr(org, key, value)
    await db.commit()
    await db.refresh(org)
    return org


@router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organisation(org_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Organisation).where(Organisation.id == org_id))
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organisation not found")
    await db.delete(org)
    await db.commit()


@router.get("/{org_id}/campaigns", response_model=List[dict])
async def get_organisation_campaigns(org_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Organisation).where(Organisation.id == org_id))
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organisation not found")
    from app.models.campaign import Campaign
    from app.models.threat import Threat
    camp_result = await db.execute(
        select(Campaign, Threat)
        .join(Threat, Campaign.threat_id == Threat.id)
        .where(Campaign.organisation_id == org_id)
    )
    rows = camp_result.all()
    return [
        {
            "campaign_id": row.Campaign.id,
            "campaign_name": row.Campaign.campaign_name,
            "campaign_type": row.Campaign.campaign_type,
            "status": row.Campaign.status,
            "threat_name": row.Threat.name
        }
        for row in rows
    ]