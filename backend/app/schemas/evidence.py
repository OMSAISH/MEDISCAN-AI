from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict
from backend.app.models.evidence import SourceType

class EvidenceItemResponse(BaseModel):
    id: str
    query_id: str
    indication_id: Optional[str] = None
    source_type: SourceType
    source_id: str
    source_url: str
    title: str
    publication_date: Optional[str] = None
    evidence_type: str
    evidence_strength: str
    extracted_facts: Optional[Dict[str, Any]] = None
    provenance: Optional[Dict[str, Any]] = None
    confidence: float

    model_config = ConfigDict(from_attributes=True)

class IndicationEvidenceListResponse(BaseModel):
    indication_id: str
    indication_name: str
    evidence_score: float
    evidence_strength: str
    clinical_trials: List[EvidenceItemResponse] = []
    literature: List[EvidenceItemResponse] = []
    patents: List[EvidenceItemResponse] = []
    market_signals: List[EvidenceItemResponse] = []
