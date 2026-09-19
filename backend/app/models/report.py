import enum
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, Integer, Enum, ForeignKey, JSON, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database.base import Base, TimestampMixin

class ReportFormat(str, enum.Enum):
    PDF = "PDF"
    HTML = "HTML"
    JSON = "JSON"
    CSV = "CSV"

class Report(Base, TimestampMixin):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    query_id: Mapped[str] = mapped_column(String(36), ForeignKey("research_queries.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    report_format: Mapped[ReportFormat] = mapped_column(Enum(ReportFormat), default=ReportFormat.PDF, nullable=False)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), nullable=False)
    
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    query = relationship("ResearchQuery", back_populates="reports")
