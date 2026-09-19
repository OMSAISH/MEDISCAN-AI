import uuid
import asyncio
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from sqlalchemy.orm import selectinload

from backend.app.database.session import get_db, AsyncSessionLocal
from backend.app.models.user import User
from backend.app.models.research import ResearchQuery, QueryStatus, DiscoveredIndication, AgentRun
from backend.app.schemas.research import (
    NewResearchRequest, 
    ResearchDetailResponse, 
    ResearchSummaryResponse,
    IndicationResponse,
    AgentStatusResponse
)
from backend.app.security.rbac import get_current_active_user, record_audit_log
from backend.app.agents.master_agent import master_agent
from backend.app.services.event_stream import event_stream_manager

router = APIRouter(prefix="/research", tags=["Research"])

async def run_master_agent_background(
    query_id: str,
    drug_name: str,
    research_question: str,
    enable_clinical: bool,
    enable_literature: bool,
    enable_patent: bool,
    enable_market: bool
):
    """Background execution worker using a dedicated session."""
    async with AsyncSessionLocal() as db:
        try:
            await master_agent.execute_research(
                db=db,
                query_id=query_id,
                drug_name=drug_name,
                research_question=research_question,
                enable_clinical=enable_clinical,
                enable_literature=enable_literature,
                enable_patent=enable_patent,
                enable_market=enable_market
            )
        except Exception as e:
            # Catch any unexpected failure and mark query as FAILED
            stmt = select(ResearchQuery).where(ResearchQuery.id == query_id)
            res = await db.execute(stmt)
            q = res.scalar_one_or_none()
            if q:
                q.status = QueryStatus.FAILED
                q.error_message = str(e)
                await db.commit()

@router.post("", response_model=ResearchDetailResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_research_analysis(
    request_in: NewResearchRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    query_id = str(uuid.uuid4())
    
    new_query = ResearchQuery(
        id=query_id,
        user_id=current_user.id,
        drug_name=request_in.drug_name.strip(),
        normalized_drug_name=request_in.drug_name.strip().capitalize(),
        research_question=request_in.research_question,
        enable_clinical=request_in.enable_clinical,
        enable_literature=request_in.enable_literature,
        enable_patent=request_in.enable_patent,
        enable_market=request_in.enable_market,
        status=QueryStatus.QUEUED
    )
    db.add(new_query)
    await db.commit()
    await db.refresh(new_query)

    client_ip = request.client.host if request.client else None
    await record_audit_log(
        db=db,
        user_id=current_user.id,
        action="START_RESEARCH_ANALYSIS",
        resource_type="QUERY",
        resource_id=query_id,
        ip_address=client_ip,
        details={"drug_name": new_query.drug_name}
    )

    # Spawn Master Agent in background
    background_tasks.add_task(
        run_master_agent_background,
        query_id=query_id,
        drug_name=new_query.drug_name,
        research_question=new_query.research_question or "",
        enable_clinical=new_query.enable_clinical,
        enable_literature=new_query.enable_literature,
        enable_patent=new_query.enable_patent,
        enable_market=new_query.enable_market
    )

    return ResearchDetailResponse(
        id=new_query.id,
        drug_name=new_query.drug_name,
        normalized_drug_name=new_query.normalized_drug_name,
        research_question=new_query.research_question,
        status=new_query.status,
        created_at=new_query.created_at,
        agent_runs=[],
        indications=[]
    )

@router.get("/history", response_model=List[ResearchSummaryResponse])
async def get_research_history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(ResearchQuery)
        .where(ResearchQuery.user_id == current_user.id)
        .options(selectinload(ResearchQuery.indications))
        .order_by(desc(ResearchQuery.created_at))
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(stmt)
    queries = result.scalars().all()

    summary_list = []
    for q in queries:
        trials_count = sum(ind.clinical_trial_count for ind in q.indications)
        lit_count = sum(ind.literature_count for ind in q.indications)
        pat_count = sum(ind.patent_count for ind in q.indications)
        mkt_count = sum(ind.market_signal_count for ind in q.indications)

        summary_list.append(ResearchSummaryResponse(
            id=q.id,
            drug_name=q.drug_name,
            normalized_drug_name=q.normalized_drug_name,
            research_question=q.research_question,
            status=q.status,
            indication_count=len(q.indications),
            clinical_trial_count=trials_count,
            literature_count=lit_count,
            patent_count=pat_count,
            market_signal_count=mkt_count,
            created_at=q.created_at,
            execution_time_ms=q.execution_time_ms
        ))

    return summary_list

@router.get("/{id}", response_model=ResearchDetailResponse)
async def get_research_analysis(
    id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(ResearchQuery)
        .where(ResearchQuery.id == id, ResearchQuery.user_id == current_user.id)
        .options(
            selectinload(ResearchQuery.indications),
            selectinload(ResearchQuery.agent_runs)
        )
    )
    result = await db.execute(stmt)
    query = result.scalar_one_or_none()

    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Research analysis not found."
        )

    # Format indications
    indication_responses = []
    for ind in sorted(query.indications, key=lambda x: x.evidence_score, reverse=True):
        indication_responses.append(IndicationResponse(
            id=ind.id,
            indication_name=ind.indication_name,
            therapeutic_area=ind.therapeutic_area,
            evidence_score=ind.evidence_score,
            clinical_score=ind.clinical_score,
            literature_score=ind.literature_score,
            patent_score=ind.patent_score,
            market_score=ind.market_score,
            evidence_strength=ind.evidence_strength,
            clinical_trial_count=ind.clinical_trial_count,
            literature_count=ind.literature_count,
            patent_count=ind.patent_count,
            market_signal_count=ind.market_signal_count,
            phase_distribution=ind.phase_distribution_json,
            positive_factors=ind.positive_factors_json,
            limitations=ind.limitations_json,
            explanation=ind.explanation
        ))

    agent_responses = []
    for ar in query.agent_runs:
        agent_responses.append(AgentStatusResponse(
            agent_name=ar.agent_name,
            status=ar.status,
            items_found=ar.items_found,
            execution_time_ms=ar.execution_time_ms,
            error_message=ar.error_message,
            details=ar.details_json
        ))

    return ResearchDetailResponse(
        id=query.id,
        drug_name=query.drug_name,
        normalized_drug_name=query.normalized_drug_name,
        canonical_smiles=query.canonical_smiles,
        chembl_id=query.chembl_id,
        pubchem_cid=query.pubchem_cid,
        research_question=query.research_question,
        status=query.status,
        error_message=query.error_message,
        execution_time_ms=query.execution_time_ms,
        executive_summary=query.executive_summary,
        synthesis_disclaimer=query.synthesis_disclaimer,
        created_at=query.created_at,
        agent_runs=agent_responses,
        indications=indication_responses
    )

@router.get("/{id}/stream")
async def stream_research_events(
    id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Server-Sent Events (SSE) streaming endpoint for live analysis progress."""
    # Verify query ownership
    stmt = select(ResearchQuery).where(ResearchQuery.id == id, ResearchQuery.user_id == current_user.id)
    res = await db.execute(stmt)
    query = res.scalar_one_or_none()
    if not query:
        raise HTTPException(status_code=404, detail="Analysis not found")

    queue = event_stream_manager.subscribe(id)

    async def event_generator():
        try:
            # Yield initial status
            yield f"event: initial_state\ndata: {json.dumps({'status': query.status.value})}\n\n"
            
            while True:
                # Disconnect check
                if await request.is_disconnected():
                    break
                
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=1.0)
                    yield f"event: {event['event']}\ndata: {json.dumps(event['data'])}\n\n"
                    
                    if event['event'] in ["analysis_completed", "analysis_failed"]:
                        break
                except asyncio.TimeoutError:
                    # Keepalive ping
                    yield ": ping\n\n"
        finally:
            event_stream_manager.unsubscribe(id, queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )

@router.delete("/{id}")
async def delete_research_analysis(
    id: str,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(ResearchQuery).where(ResearchQuery.id == id, ResearchQuery.user_id == current_user.id)
    res = await db.execute(stmt)
    query = res.scalar_one_or_none()
    if not query:
        raise HTTPException(status_code=404, detail="Analysis not found")

    await db.delete(query)
    await db.commit()

    client_ip = request.client.host if request.client else None
    await record_audit_log(
        db=db,
        user_id=current_user.id,
        action="DELETE_RESEARCH_ANALYSIS",
        resource_type="QUERY",
        resource_id=id,
        ip_address=client_ip
    )

    return {"status": "success", "message": "Research analysis deleted."}
