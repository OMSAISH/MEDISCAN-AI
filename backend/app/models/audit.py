from typing import Optional
from sqlalchemy import String, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.database.base import Base, TimestampMixin

class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # "LOGIN", "CREATE_QUERY", "EXPORT_REPORT", "DELETE_QUERY"
    resource_type: Mapped[str] = mapped_column(String(50), nullable=False)  # "USER", "QUERY", "REPORT"
    resource_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    details_json: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    user = relationship("User", back_populates="audit_logs")
