from sqlalchemy import String, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base
import enum


class CompanyRole(str, enum.Enum):
    OPERATOR = "OPERATOR"
    INVESTOR = "INVESTOR"
    CONTRACTOR = "CONTRACTOR"
    FINANCIER = "FINANCIER"


class ThreatCompany(Base):
    __tablename__ = "threat_companies"

    threat_id: Mapped[str] = mapped_column(String, ForeignKey("threats.id"), primary_key=True)
    company_id: Mapped[str] = mapped_column(String, ForeignKey("companies.id"), primary_key=True)
    role: Mapped[CompanyRole] = mapped_column(SAEnum(CompanyRole), nullable=False)

    # Relationships
    threat: Mapped["Threat"] = relationship("Threat", back_populates="company_associations")
    company: Mapped["Company"] = relationship("Company", back_populates="threat_associations")