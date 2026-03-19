import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import AsyncSessionLocal
from app.models.threat import Threat, ThreatType, ThreatStatus
from app.models.company import Company, CompanySector
from app.models.organisation import Organisation, OrgType
from app.models.campaign import Campaign, CampaignType, CampaignStatus
from app.models.threat_company import ThreatCompany, CompanyRole
from app.models.user import User, UserRole
from app.core.security import hash_password
import uuid
from datetime import date


# ─────────────────────────────────────────
# DATA
# ─────────────────────────────────────────

THREATS = [
    {
        "id": str(uuid.uuid4()),
        "name": "Rosebank Oilfield Development",
        "threat_type": ThreatType.OFFSHORE_DRILLING,
        "status": ThreatStatus.APPROVED,
        "country": "United Kingdom",
        "region": "North Sea",
        "description": (
            "Rosebank is the largest undeveloped oilfield in the UK North Sea, "
            "located 130km north-west of Shetland. Approved by the UK government "
            "in 2023, it is projected to produce up to 500 million barrels of oil "
            "and gas over its lifetime."
        ),
        "estimated_co2_impact_tonnes": 200_000_000,
        "land_area_affected_km2": None,
        "latitude": 60.5,
        "longitude": 1.2,
        "source_url": "https://www.stoprosebank.org",
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Willow Project",
        "threat_type": ThreatType.OFFSHORE_DRILLING,
        "status": ThreatStatus.APPROVED,
        "country": "United States",
        "region": "Alaska",
        "description": (
            "The Willow Project is a major oil drilling venture on Alaska's "
            "North Slope in the National Petroleum Reserve. Approved by the Biden "
            "administration in 2023, it could produce up to 180,000 barrels per day "
            "and generate around 278 million metric tonnes of CO2 over its lifetime."
        ),
        "estimated_co2_impact_tonnes": 278_000_000,
        "land_area_affected_km2": 4047,
        "latitude": 70.3,
        "longitude": -152.8,
        "source_url": "https://www.nrdc.org/willow-project",
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Trans Mountain Pipeline Expansion",
        "threat_type": ThreatType.PIPELINE,
        "status": ThreatStatus.UNDER_CONSTRUCTION,
        "country": "Canada",
        "region": "British Columbia / Alberta",
        "description": (
            "The Trans Mountain Expansion Project triples the capacity of the existing "
            "Trans Mountain Pipeline, carrying oil sands crude from Edmonton, Alberta "
            "to Burnaby, British Columbia. It has faced sustained opposition from "
            "Indigenous communities and environmental groups."
        ),
        "estimated_co2_impact_tonnes": 86_000_000,
        "land_area_affected_km2": 1500,
        "latitude": 53.5,
        "longitude": -120.0,
        "source_url": "https://www.transmountain.com",
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Amazon Deforestation by JBS",
        "threat_type": ThreatType.DEFORESTATION,
        "status": ThreatStatus.OPERATIONAL,
        "country": "Brazil",
        "region": "Amazon Basin",
        "description": (
            "JBS, the world's largest meat processing company, has been repeatedly "
            "linked to Amazon deforestation through its supply chain. Cattle ranching "
            "is the leading driver of Amazon deforestation, accounting for around "
            "80% of forest loss in the region."
        ),
        "estimated_co2_impact_tonnes": 500_000_000,
        "land_area_affected_km2": 800_000,
        "latitude": -5.0,
        "longitude": -60.0,
        "source_url": "https://www.globalwitness.org/jbs",
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Drax Biomass Power Station",
        "threat_type": ThreatType.AIR_POLLUTION,
        "status": ThreatStatus.OPERATIONAL,
        "country": "United Kingdom",
        "region": "Yorkshire",
        "description": (
            "Drax Power Station in North Yorkshire burns wood pellets imported "
            "from North American and European forests, claiming it is carbon neutral. "
            "Critics including the RSPB and environmental groups argue this accounting "
            "masks significant emissions and destroys biodiverse forests."
        ),
        "estimated_co2_impact_tonnes": 12_800_000,
        "land_area_affected_km2": None,
        "latitude": 53.7,
        "longitude": -1.0,
        "source_url": "https://www.rspb.org.uk/drax",
    },
    {
        "id": str(uuid.uuid4()),
        "name": "East African Crude Oil Pipeline",
        "threat_type": ThreatType.PIPELINE,
        "status": ThreatStatus.UNDER_CONSTRUCTION,
        "country": "Uganda",
        "region": "East Africa",
        "description": (
            "The East African Crude Oil Pipeline (EACOP) is a 1,443km heated pipeline "
            "being built by TotalEnergies from Uganda to Tanzania. It will pass through "
            "ecologically sensitive areas and has displaced thousands of people from "
            "their land."
        ),
        "estimated_co2_impact_tonnes": 379_000_000,
        "land_area_affected_km2": 2000,
        "latitude": 1.3,
        "longitude": 32.0,
        "source_url": "https://www.stopeacop.net",
    },
]

COMPANIES = [
    {
        "id": str(uuid.uuid4()),
        "name": "Equinor",
        "sector": CompanySector.OIL_GAS,
        "country_of_registration": "Norway",
        "description": "Norwegian state-owned energy company and primary operator of the Rosebank oilfield.",
        "esg_score": 42.0,
        "annual_emissions_mtonnes": 14.0,
        "is_paris_signatory": True,
        "website": "https://www.equinor.com",
    },
    {
        "id": str(uuid.uuid4()),
        "name": "ConocoPhillips",
        "sector": CompanySector.OIL_GAS,
        "country_of_registration": "United States",
        "description": "American multinational energy corporation and operator of the Willow Project in Alaska.",
        "esg_score": 38.0,
        "annual_emissions_mtonnes": 21.0,
        "is_paris_signatory": False,
        "website": "https://www.conocophillips.com",
    },
    {
        "id": str(uuid.uuid4()),
        "name": "JBS",
        "sector": CompanySector.AGRICULTURE,
        "country_of_registration": "Brazil",
        "description": "World's largest meat processing company, repeatedly linked to Amazon deforestation through its cattle supply chain.",
        "esg_score": 18.0,
        "annual_emissions_mtonnes": 51.0,
        "is_paris_signatory": False,
        "website": "https://www.jbs.com.br",
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Drax Group",
        "sector": CompanySector.ENERGY,
        "country_of_registration": "United Kingdom",
        "description": "Operator of Drax Power Station in Yorkshire, the UK's largest power station by output, burning imported biomass.",
        "esg_score": 29.0,
        "annual_emissions_mtonnes": 12.8,
        "is_paris_signatory": True,
        "website": "https://www.drax.com",
    },
    {
        "id": str(uuid.uuid4()),
        "name": "TotalEnergies",
        "sector": CompanySector.OIL_GAS,
        "country_of_registration": "France",
        "description": "French multinational and key developer of the East African Crude Oil Pipeline.",
        "esg_score": 35.0,
        "annual_emissions_mtonnes": 45.0,
        "is_paris_signatory": True,
        "website": "https://www.totalenergies.com",
    },
]

ORGANISATIONS = [
    {
        "id": str(uuid.uuid4()),
        "name": "Stop Rosebank",
        "org_type": OrgType.GRASSROOTS,
        "country": "United Kingdom",
        "description": "UK-based coalition of environmental groups campaigning to stop the Rosebank oilfield development in the North Sea.",
        "founding_date": date(2022, 6, 1),
        "website": "https://www.stoprosebank.org",
        "member_count": 50000,
        "is_active": True,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "ClientEarth",
        "org_type": OrgType.LEGAL_COALITION,
        "country": "United Kingdom",
        "description": "Environmental law charity that uses the law to protect the planet, pursuing legal action against governments and corporations.",
        "founding_date": date(2008, 1, 1),
        "website": "https://www.clientearth.org",
        "member_count": None,
        "is_active": True,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Global Witness",
        "org_type": OrgType.NGO,
        "country": "United Kingdom",
        "description": "International NGO investigating and campaigning against natural resource exploitation and environmental abuse.",
        "founding_date": date(1993, 1, 1),
        "website": "https://www.globalwitness.org",
        "member_count": None,
        "is_active": True,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Stop EACOP",
        "org_type": OrgType.INTERNATIONAL,
        "country": "Uganda",
        "description": "International campaign opposing the East African Crude Oil Pipeline, coordinating resistance across Uganda, Tanzania and globally.",
        "founding_date": date(2020, 3, 1),
        "website": "https://www.stopeacop.net",
        "member_count": 260000,
        "is_active": True,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Amazon Watch",
        "org_type": OrgType.NGO,
        "country": "United States",
        "description": "Nonprofit organisation protecting the Amazon rainforest and advancing the rights of indigenous peoples.",
        "founding_date": date(1996, 1, 1),
        "website": "https://www.amazonwatch.org",
        "member_count": None,
        "is_active": True,
    },
    {
        "id": str(uuid.uuid4()),
        "name": "Extinction Rebellion UK",
        "org_type": OrgType.GRASSROOTS,
        "country": "United Kingdom",
        "description": "UK branch of the international movement using nonviolent civil disobedience to compel government action on climate change.",
        "founding_date": date(2018, 10, 31),
        "website": "https://www.extinctionrebellion.uk",
        "member_count": 100000,
        "is_active": True,
    },
]


# ─────────────────────────────────────────
# SEED FUNCTION
# ─────────────────────────────────────────

async def seed():
    admin_email = os.getenv("ADMIN_EMAIL", "admin@climateview.dev")
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD")
    
    if not admin_password:
        raise ValueError("ADMIN_PASSWORD environment variable must be set before seeding")

    async with AsyncSessionLocal() as db:
        print("seeding database...")

        # --- Threats ---
        print("  Adding threats...")
        threat_map = {}  # name → id, for linking later
        for t in THREATS:
            existing = await db.get(Threat, t["id"])
            if not existing:
                db.add(Threat(**t))
            threat_map[t["name"]] = t["id"]

        # --- Companies ---
        print("  Adding companies...")
        company_map = {}  # name → id
        for c in COMPANIES:
            existing = await db.get(Company, c["id"])
            if not existing:
                db.add(Company(**c))
            company_map[c["name"]] = c["id"]

        await db.commit()

        # --- ThreatCompany links ---
        print("  Linking companies to threats...")
        links = [
            (threat_map["Rosebank Oilfield Development"], company_map["Equinor"], CompanyRole.OPERATOR),
            (threat_map["Willow Project"], company_map["ConocoPhillips"], CompanyRole.OPERATOR),
            (threat_map["Amazon Deforestation by JBS"], company_map["JBS"], CompanyRole.OPERATOR),
            (threat_map["Drax Biomass Power Station"], company_map["Drax Group"], CompanyRole.OPERATOR),
            (threat_map["East African Crude Oil Pipeline"], company_map["TotalEnergies"], CompanyRole.OPERATOR),
        ]
        for threat_id, company_id, role in links:
            from sqlalchemy import select
            existing = await db.execute(
                select(ThreatCompany).where(
                    ThreatCompany.threat_id == threat_id,
                    ThreatCompany.company_id == company_id
                )
            )
            if not existing.scalar_one_or_none():
                db.add(ThreatCompany(threat_id=threat_id, company_id=company_id, role=role))

        # --- Organisations ---
        print("  Adding organisations...")
        org_map = {}  # name → id
        for o in ORGANISATIONS:
            existing = await db.get(Organisation, o["id"])
            if not existing:
                db.add(Organisation(**o))
            org_map[o["name"]] = o["id"]

        await db.commit()

        # --- Campaigns ---
        print("  Adding campaigns...")
        campaigns = [
            {
                "id": str(uuid.uuid4()),
                "campaign_name": "Stop Rosebank Legal Challenge",
                "campaign_type": CampaignType.LEGAL_CHALLENGE,
                "status": CampaignStatus.ACTIVE,
                "organisation_id": org_map["Stop Rosebank"],
                "threat_id": threat_map["Rosebank Oilfield Development"],
                "start_date": date(2023, 9, 1),
                "outcome_summary": "Legal challenge filed in the Court of Session in Edinburgh arguing the approval was unlawful.",
                "signatures_count": None,
            },
            {
                "id": str(uuid.uuid4()),
                "campaign_name": "Rosebank Mass Petition",
                "campaign_type": CampaignType.PETITION,
                "status": CampaignStatus.ACTIVE,
                "organisation_id": org_map["Stop Rosebank"],
                "threat_id": threat_map["Rosebank Oilfield Development"],
                "start_date": date(2023, 1, 1),
                "outcome_summary": None,
                "signatures_count": 120000,
            },
            {
                "id": str(uuid.uuid4()),
                "campaign_name": "Stop Willow Project Protest Campaign",
                "campaign_type": CampaignType.PROTEST,
                "status": CampaignStatus.LOST,
                "organisation_id": org_map["Amazon Watch"],
                "threat_id": threat_map["Willow Project"],
                "start_date": date(2023, 1, 1),
                "end_date": date(2023, 6, 1),
                "outcome_summary": "Despite widespread protests and over 5 million public comments, the Biden administration approved the project in March 2023.",
                "signatures_count": 5_000_000,
            },
            {
                "id": str(uuid.uuid4()),
                "campaign_name": "Stop EACOP Global Divestment Campaign",
                "campaign_type": CampaignType.LOBBYING,
                "status": CampaignStatus.ACTIVE,
                "organisation_id": org_map["Stop EACOP"],
                "threat_id": threat_map["East African Crude Oil Pipeline"],
                "start_date": date(2021, 1, 1),
                "outcome_summary": "Campaign has successfully pressured over 25 banks and insurers to withdraw from financing the pipeline.",
                "signatures_count": 260000,
            },
            {
                "id": str(uuid.uuid4()),
                "campaign_name": "JBS Amazon Deforestation Exposure",
                "campaign_type": CampaignType.MEDIA_CAMPAIGN,
                "status": CampaignStatus.ONGOING,
                "organisation_id": org_map["Global Witness"],
                "threat_id": threat_map["Amazon Deforestation by JBS"],
                "start_date": date(2020, 1, 1),
                "outcome_summary": "Ongoing investigative reporting linking JBS supply chains to illegally deforested land in the Amazon.",
                "signatures_count": None,
            },
            {
                "id": str(uuid.uuid4()),
                "campaign_name": "Drax Biomass Legal Action",
                "campaign_type": CampaignType.LEGAL_CHALLENGE,
                "status": CampaignStatus.ACTIVE,
                "organisation_id": org_map["ClientEarth"],
                "threat_id": threat_map["Drax Biomass Power Station"],
                "start_date": date(2022, 3, 1),
                "outcome_summary": "ClientEarth challenging the basis on which Drax receives government subsidies for burning biomass.",
                "signatures_count": None,
            },
        ]
        for c in campaigns:
            existing = await db.get(Campaign, c["id"])
            if not existing:
                db.add(Campaign(**c))

        # --- Admin user ---
        existing_admin = await db.execute(
            select(User).where(User.username == admin_username)
        )
        if not existing_admin.scalar_one_or_none():
            db.add(User(
                id=str(uuid.uuid4()),
                email=admin_email,
                username=admin_username,
                hashed_password=hash_password(admin_password),
                role=UserRole.ADMIN,
                is_active=True,
            ))
            print(f"  Admin user '{admin_username}' created")
        else:
            print(f"  Admin user '{admin_username}' already exists, skipping")


if __name__ == "__main__":
    asyncio.run(seed())