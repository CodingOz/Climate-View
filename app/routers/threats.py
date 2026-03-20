from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.threat import Threat
from app.models.user import User
from app.schemas.threat import ThreatCreate, ThreatUpdate, ThreatResponse
from app.schemas.error import ErrorResponse
from app.dependencies import get_current_user
from typing import List
import uuid
    
router = APIRouter(prefix="/threats", tags=["Threats"])


@router.get("/", response_model=List[ThreatResponse])
async def get_threats(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Threat))
    return result.scalars().all()


@router.post("/", response_model=ThreatResponse, status_code=201, responses={401: {"model": ErrorResponse}})
async def create_threat(
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
async def get_threat(threat_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Threat).where(Threat.id == threat_id))
    threat = result.scalar_one_or_none()
    if not threat:
        raise HTTPException(status_code=404, detail="Threat not found")
    return threat


@router.put("/{threat_id}", response_model=ThreatResponse, responses={404: {"model": ErrorResponse}, 401: {"model": ErrorResponse}})
async def update_threat(
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


@router.delete("/{threat_id}", status_code=204, responses={404: {"model": ErrorResponse}, 401: {"model": ErrorResponse}})
async def delete_threat(
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