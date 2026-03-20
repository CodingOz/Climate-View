from fastapi import APIRouter, Depends, HTTPException, status, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.threat import Threat, ThreatStatus, ThreatType
from app.models.user import User
from app.schemas.threat import ThreatCreate, ThreatUpdate, ThreatResponse
from app.schemas.error import ErrorResponse
from app.dependencies import get_current_user
from typing import List, Optional
import uuid

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/threats", tags=["Threats"])


@router.get("/", response_model=List[ThreatResponse])
@limiter.limit("100/minute")
async def get_threats(
    request: Request,
    status: Optional[ThreatStatus] = None,
    country: Optional[str] = None,
    threat_type: Optional[ThreatType] = None,
    min_co2: Optional[float] = None,
    max_co2: Optional[float] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    query = select(Threat)

    if status:
        query = query.where(Threat.status == status)
    if country:
        query = query.where(Threat.country.ilike(f"%{country}%"))
    if threat_type:
        query = query.where(Threat.threat_type == threat_type)
    if min_co2 is not None:
        query = query.where(Threat.estimated_co2_impact_tonnes >= min_co2)
    if max_co2 is not None:
        query = query.where(Threat.estimated_co2_impact_tonnes <= max_co2)

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/", response_model=ThreatResponse, status_code=status.HTTP_201_CREATED, responses={401: {"model": ErrorResponse}})
@limiter.limit("20/minute")
async def create_threat(
    request: Request,
    threat: ThreatCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_threat = Threat(id=str(uuid.uuid4()), **threat.model_dump())
    db.add(db_threat)
    await db.commit()
    await db.refresh(db_threat)
    return db_threat


@router.get("/{threat_id}", response_model=ThreatResponse, responses={404: {"model": ErrorResponse}})
@limiter.limit("100/minute")
async def get_threat(request: Request, threat_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Threat).where(Threat.id == threat_id))
    threat = result.scalar_one_or_none()
    if not threat:
        raise HTTPException(status_code=404, detail="Threat not found")
    return threat


@router.put("/{threat_id}", response_model=ThreatResponse, responses={404: {"model": ErrorResponse}, 401: {"model": ErrorResponse}})
@limiter.limit("20/minute")
async def update_threat(
    request: Request,
    threat_id: str,
    threat_data: ThreatUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Threat).where(Threat.id == threat_id))
    threat = result.scalar_one_or_none()
    if not threat:
        raise HTTPException(status_code=404, detail="Threat not found")
    for key, value in threat_data.model_dump().items():
        setattr(threat, key, value)
    await db.commit()
    await db.refresh(threat)
    return threat


@router.delete("/{threat_id}", status_code=status.HTTP_204_NO_CONTENT, responses={404: {"model": ErrorResponse}, 401: {"model": ErrorResponse}})
@limiter.limit("20/minute")
async def delete_threat(
    request: Request,
    threat_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    result = await db.execute(select(Threat).where(Threat.id == threat_id))
    threat = result.scalar_one_or_none()
    if not threat:
        raise HTTPException(status_code=404, detail="Threat not found")
    await db.delete(threat)
    await db.commit()