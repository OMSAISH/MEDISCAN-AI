import time
from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc

from backend.app.config import settings
from backend.app.database.session import get_db
from backend.app.models.user import User, UserRole
from backend.app.models.research import ResearchQuery, QueryStatus, AgentRun, DiscoveredIndication
from backend.app.models.evidence import EvidenceItem
from backend.app.models.audit import AuditLog
from backend.app.schemas.admin import AdminOverviewResponse, SystemHealthResponse, AgentExecutionMetric, AuditLogItemResponse
from backend.app.security.rbac import require_role

router = APIRouter(prefix="/admin", tags=["Admin"])
START_TIME = time.time()

@router.get("/overview", response_model=AdminOverviewResponse)
async def get_admin_overview(
    admin_user: User = Depends(require_role([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    # User counts
    user_count_stmt = select(func.count(User.id))
    user_count = (await db.execute(user_count_stmt)).scalar() or 0

    # Query counts
    total_queries_stmt = select(func.count(ResearchQuery.id))
    total_queries = (await db.execute(total_queries_stmt)).scalar() or 0

    completed_queries_stmt = select(func.count(ResearchQuery.id)).where(ResearchQuery.status == QueryStatus.COMPLETED)
    completed_queries = (await db.execute(completed_queries_stmt)).scalar() or 0

    failed_queries_stmt = select(func.count(ResearchQuery.id)).where(ResearchQuery.status == QueryStatus.FAILED)
    failed_queries = (await db.execute(failed_queries_stmt)).scalar() or 0

    # Evidence items & indications
    evidence_count_stmt = select(func.count(EvidenceItem.id))
    evidence_count = (await db.execute(evidence_count_stmt)).scalar() or 0

    ind_count_stmt = select(func.count(DiscoveredIndication.id))
    ind_count = (await db.execute(ind_count_stmt)).scalar() or 0

    # Agent execution metrics
    agent_metrics = []
    agent_names = ["Clinical Agent", "Literature Agent", "Patent Agent", "Market Agent"]
    for aname in agent_names:
        total_stmt = select(func.count(AgentRun.id)).where(AgentRun.agent_name == aname)
        succ_stmt = select(func.count(AgentRun.id)).where(AgentRun.agent_name == aname, AgentRun.status == "COMPLETED")
        fail_stmt = select(func.count(AgentRun.id)).where(AgentRun.agent_name == aname, AgentRun.status == "FAILED")
        avg_time_stmt = select(func.avg(AgentRun.execution_time_ms)).where(AgentRun.agent_name == aname)

        tot = (await db.execute(total_stmt)).scalar() or 0
        succ = (await db.execute(succ_stmt)).scalar() or 0
        fail = (await db.execute(fail_stmt)).scalar() or 0
        avg_t = (await db.execute(avg_time_stmt)).scalar() or 0.0

        agent_metrics.append(AgentExecutionMetric(
            agent_name=aname,
            total_runs=tot,
            successful_runs=succ,
            failed_runs=fail,
            avg_execution_time_ms=round(float(avg_t), 1)
        ))

    # API Integration Statuses
    integration_status = {
        "clinicaltrials_v2": {"name": "ClinicalTrials.gov API v2", "status": "ONLINE", "auth_required": False},
        "ncbi_pubmed": {"name": "NCBI PubMed E-Utilities", "status": "ONLINE", "auth_required": bool(settings.NCBI_API_KEY)},
        "patentsview": {"name": "PatentsView API", "status": "ONLINE", "auth_required": False},
        "openfda": {"name": "OpenFDA Drug Label API", "status": "ONLINE", "auth_required": bool(settings.FDA_API_KEY)}
    }

    uptime = time.time() - START_TIME
    system_health = SystemHealthResponse(
        status="healthy",
        database_connected=True,
        version=settings.APP_VERSION,
        uptime_seconds=round(uptime, 1),
        active_analyses=0
    )

    return AdminOverviewResponse(
        system_health=system_health,
        total_users=user_count,
        total_analyses=total_queries,
        completed_analyses=completed_queries,
        failed_analyses=failed_queries,
        total_evidence_items=evidence_count,
        total_indications_discovered=ind_count,
        agent_metrics=agent_metrics,
        api_integrations_status=integration_status
    )

@router.get("/audit-logs", response_model=List[AuditLogItemResponse])
async def get_audit_logs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    admin_user: User = Depends(require_role([UserRole.ADMIN])),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(AuditLog, User.email)
        .outerjoin(User, AuditLog.user_id == User.id)
        .order_by(desc(AuditLog.created_at))
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    rows = result.all()

    logs = []
    for audit, user_email in rows:
        logs.append(AuditLogItemResponse(
            id=audit.id,
            user_id=audit.user_id,
            user_email=user_email,
            action=audit.action,
            resource_type=audit.resource_type,
            resource_id=audit.resource_id,
            ip_address=audit.ip_address,
            details=audit.details_json,
            created_at=audit.created_at
        ))
    return logs
