import uuid
from datetime import datetime
from sqlalchemy import String, Float, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
import enum

class ThreatType(str, enum.Enum):
    PIPELINE = "PIPELINE"
    DEFORESTATION = "DEFORESTATION"
    AIR_POLLUTION = "AIR_POLLUTION"
    MINING = "MINING"
    OFFSHORE_DRILLING = "OFFSHORE_DRILLING"

class ThreatStatus(str, enum.Enum):
    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    UNDER_CONSTRUCTION = "UNDER_CONSTRUCTION"
    OPERATIONAL = "OPERATIONAL"
    SUSPENDED = "SUSPENDED"
    CANCELLED = "CANCELLED"

class Threat(Base):
    __tablename__ = "threats"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String, nullable=False)
    threat_type: Mapped[ThreatType] = mapped_column(SAEnum(ThreatType), nullable=False)
    status: Mapped[ThreatStatus] = mapped_column(SAEnum(ThreatStatus), nullable=False)
    country: Mapped[str] = mapped_column(String, nullable=False)
    region: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    estimated_co2_impact_tonnes: Mapped[float | None] = mapped_column(Float, nullable=True)
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    source_url: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)