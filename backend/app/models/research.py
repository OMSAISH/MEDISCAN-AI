import enum
from typing import List, Optional
from sqlalchemy import String, Text, Float, Integer, Boolean, Enum, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database.base import Base, TimestampMixin

class QueryStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    PARTIAL_FAILURE = "PARTIAL_FAILURE"
    FAILED = "FAILED"

class AgentStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class EvidenceStrength(str, enum.Enum):
    STRONG = "Strong"
    MODERATE = "Moderate"
    LIMITED = "Limited"
    INSUFFICIENT = "Insufficient"

class ResearchQuery(Base, TimestampMixin):
    __tablename__ = "research_queries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    drug_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    normalized_drug_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    canonical_smiles: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    chembl_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    pubchem_cid: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    research_question: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    enable_clinical: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    enable_literature: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    enable_patent: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    enable_market: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    status: Mapped[QueryStatus] = mapped_column(Enum(QueryStatus), default=QueryStatus.QUEUED, nullable=False, index=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    execution_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Executive synthesis and notes
    executive_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    synthesis_disclaimer: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="research_queries")
    agent_runs = relationship("AgentRun", back_populates="query", cascade="all, delete-orphan")
    indications = relationship("DiscoveredIndication", back_populates="query", cascade="all, delete-orphan")
    evidence_items = relationship("EvidenceItem", back_populates="query", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="query", cascade="all, delete-orphan")

class AgentRun(Base, TimestampMixin):
    __tablename__ = "agent_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    query_id: Mapped[str] = mapped_column(String(36), ForeignKey("research_queries.id", ondelete="CASCADE"), nullable=False, index=True)
    
    agent_name: Mapped[str] = mapped_column(String(50), nullable=False)  # Clinical, Literature, Patent, Market, Master
    status: Mapped[AgentStatus] = mapped_column(Enum(AgentStatus), default=AgentStatus.QUEUED, nullable=False)
    items_found: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    execution_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    details_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    query = relationship("ResearchQuery", back_populates="agent_runs")

class DiscoveredIndication(Base, TimestampMixin):
    __tablename__ = "discovered_indications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    query_id: Mapped[str] = mapped_column(String(36), ForeignKey("research_queries.id", ondelete="CASCADE"), nullable=False, index=True)
    
    indication_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    therapeutic_area: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Scores (0 - 100)
    evidence_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    clinical_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    literature_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    patent_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    market_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    
    evidence_strength: Mapped[EvidenceStrength] = mapped_column(Enum(EvidenceStrength), default=EvidenceStrength.INSUFFICIENT, nullable=False)
    
    clinical_trial_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    literature_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    patent_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    market_signal_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    phase_distribution_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # {"Phase 1": X, "Phase 2": Y, "Phase 3": Z}
    positive_factors_json: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    limitations_json: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    query = relationship("ResearchQuery", back_populates="indications")
    evidence_items = relationship("EvidenceItem", back_populates="indication", cascade="all, delete-orphan")
