from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from backend.app.models.research import QueryStatus, AgentStatus, EvidenceStrength

class DrugValidationRequest(BaseModel):
    drug_name: str = Field(min_length=1, max_length=150)

class DrugValidationResponse(BaseModel):
    is_valid: bool
    input_name: str
    normalized_name: str
    synonyms: List[str] = []
    chembl_id: Optional[str] = None
    pubchem_cid: Optional[str] = None
    canonical_smiles: Optional[str] = None
    known_indications: List[str] = []
    warnings: List[str] = []

class NewResearchRequest(BaseModel):
    drug_name: str = Field(min_length=1, max_length=150)
    research_question: Optional[str] = Field(default=None, max_length=1000)
    enable_clinical: bool = True
    enable_literature: bool = True
    enable_patent: bool = True
    enable_market: bool = True

class AgentStatusResponse(BaseModel):
    agent_name: str
    status: AgentStatus
    items_found: int = 0
    execution_time_ms: Optional[int] = None
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)

class IndicationResponse(BaseModel):
    id: str
    indication_name: str
    therapeutic_area: Optional[str] = None
    evidence_score: float
    clinical_score: float
    literature_score: float
    patent_score: float
    market_score: float
    evidence_strength: EvidenceStrength
    clinical_trial_count: int
    literature_count: int
    patent_count: int
    market_signal_count: int
    phase_distribution: Optional[Dict[str, int]] = None
    positive_factors: Optional[List[str]] = None
    limitations: Optional[List[str]] = None
    explanation: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ResearchSummaryResponse(BaseModel):
    id: str
    drug_name: str
    normalized_drug_name: str
    research_question: Optional[str]
    status: QueryStatus
    indication_count: int = 0
    clinical_trial_count: int = 0
    literature_count: int = 0
    patent_count: int = 0
    market_signal_count: int = 0
    created_at: datetime
    execution_time_ms: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class ResearchDetailResponse(BaseModel):
    id: str
    drug_name: str
    normalized_drug_name: str
    canonical_smiles: Optional[str] = None
    chembl_id: Optional[str] = None
    pubchem_cid: Optional[str] = None
    research_question: Optional[str] = None
    status: QueryStatus
    error_message: Optional[str] = None
    execution_time_ms: Optional[int] = None
    executive_summary: Optional[str] = None
    synthesis_disclaimer: Optional[str] = None
    created_at: datetime
    
    agent_runs: List[AgentStatusResponse] = []
    indications: List[IndicationResponse] = []

    model_config = ConfigDict(from_attributes=True)
