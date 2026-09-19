from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from backend.app.models.report import ReportFormat

class GenerateReportRequest(BaseModel):
    report_format: ReportFormat = ReportFormat.PDF
    include_evidence_tables: bool = True
    include_methodology: bool = True

class ReportResponse(BaseModel):
    id: str
    query_id: str
    title: str
    report_format: ReportFormat
    file_path: str
    file_size_bytes: int
    generated_at: datetime
    metadata_json: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)
