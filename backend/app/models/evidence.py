import enum
from typing import Optional
from sqlalchemy import String, Text, Float, Enum, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database.base import Base, TimestampMixin

class SourceType(str, enum.Enum):
    CLINICAL = "CLINICAL"
    LITERATURE = "LITERATURE"
    PATENT = "PATENT"
    MARKET = "MARKET"

class EvidenceItem(Base, TimestampMixin):
    __tablename__ = "evidence_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    query_id: Mapped[str] = mapped_column(String(36), ForeignKey("research_queries.id", ondelete="CASCADE"), nullable=False, index=True)
    indication_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("discovered_indications.id", ondelete="CASCADE"), nullable=True, index=True)
    
    source_type: Mapped[SourceType] = mapped_column(Enum(SourceType), nullable=False, index=True)
    source_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # e.g., NCT04886804, PMID:35113657, US10485782B2
    source_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    publication_date: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    evidence_type: Mapped[str] = mapped_column(String(100), nullable=False)  # "Phase 2 Clinical Trial", "Randomized Controlled Trial", "Patent Grant"
    evidence_strength: Mapped[str] = mapped_column(String(50), nullable=False, default="Moderate")
    
    # Structured data
    extracted_facts_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    provenance_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    
    # Relationships
    query = relationship("ResearchQuery", back_populates="evidence_items")
    indication = relationship("DiscoveredIndication", back_populates="evidence_items")
