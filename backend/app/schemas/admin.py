from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from backend.app.schemas.auth import UserResponse

class SystemHealthResponse(BaseModel):
    status: str  # "healthy", "degraded", "down"
    database_connected: bool
    version: str
    uptime_seconds: float
    active_analyses: int

class AgentExecutionMetric(BaseModel):
    agent_name: str
    total_runs: int
    successful_runs: int
    failed_runs: int
    avg_execution_time_ms: float

class AdminOverviewResponse(BaseModel):
    system_health: SystemHealthResponse
    total_users: int
    total_analyses: int
    completed_analyses: int
    failed_analyses: int
    total_evidence_items: int
    total_indications_discovered: int
    agent_metrics: List[AgentExecutionMetric]
    api_integrations_status: Dict[str, Dict[str, Any]]

class AuditLogItemResponse(BaseModel):
    id: str
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    ip_address: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
