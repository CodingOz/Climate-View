from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.database import get_db
from app.models.threat import Threat
from app.models.organisation import Organisation
from app.models.campaign import Campaign
from app.schemas.search import (
    SearchResponse,
    ThreatSearchResult,
    OrganisationSearchResult,
    CampaignSearchResult,
)
from app.schemas.error import ErrorResponse

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/search", tags=["Search"])


@router.get(
    "/",
    response_model=SearchResponse,
    responses={400: {"model": ErrorResponse}},
    summary="Full-text search across threats, organisations and campaigns",
    description=(
        "Search across all major entities in the database. "
        "Returns matching threats, organisations and campaigns "
        "for a given query string. Minimum 2 characters required."
    )
)
@limiter.limit("60/minute")
async def search(
    request: Request,
    q: str,
    db: AsyncSession = Depends(get_db)
):
    if len(q.strip()) < 2:
        raise HTTPException(
            status_code=400,
            detail="Search query must be at least 2 characters"
        )

    term = f"%{q.strip().lower()}%"

    # --- Search Threats ---
    threat_result = await db.execute(
        select(Threat).where(
            or_(
                Threat.name.ilike(term),
                Threat.description.ilike(term),
                Threat.country.ilike(term),
                Threat.region.ilike(term),
            )
        ).limit(20)
    )
    threats = threat_result.scalars().all()

    # --- Search Organisations ---
    org_result = await db.execute(
        select(Organisation).where(
            or_(
                Organisation.name.ilike(term),
                Organisation.description.ilike(term),
                Organisation.country.ilike(term),
            )
        ).limit(20)
    )
    organisations = org_result.scalars().all()

    # --- Search Campaigns ---
    campaign_result = await db.execute(
        select(Campaign).where(
            or_(
                Campaign.campaign_name.ilike(term),
                Campaign.outcome_summary.ilike(term),
            )
        ).limit(20)
    )
    campaigns = campaign_result.scalars().all()

    total = len(threats) + len(organisations) + len(campaigns)

    return SearchResponse(
        query=q.strip(),
        total_results=total,
        threats=[
            ThreatSearchResult(
                id=t.id,
                name=t.name,
                threat_type=t.threat_type,
                status=t.status,
                country=t.country,
                estimated_co2_impact_tonnes=t.estimated_co2_impact_tonnes,
            )
            for t in threats
        ],
        organisations=[
            OrganisationSearchResult(
                id=o.id,
                name=o.name,
                org_type=o.org_type,
                country=o.country,
                description=o.description,
            )
            for o in organisations
        ],
        campaigns=[
            CampaignSearchResult(
                id=c.id,
                campaign_name=c.campaign_name,
                campaign_type=c.campaign_type,
                status=c.status,
                outcome_summary=c.outcome_summary,
            )
            for c in campaigns
        ],
    )