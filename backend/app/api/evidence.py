from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.models.research import DiscoveredIndication, ResearchQuery
from backend.app.models.evidence import EvidenceItem, SourceType
from backend.app.schemas.evidence import IndicationEvidenceListResponse, EvidenceItemResponse
from backend.app.security.rbac import get_current_active_user

router = APIRouter(prefix="/evidence", tags=["Evidence"])

@router.get("/{indication_id}", response_model=IndicationEvidenceListResponse)
async def get_indication_evidence(
    indication_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    # Fetch indication and verify ownership of parent query
    stmt = (
        select(DiscoveredIndication)
        .join(ResearchQuery, DiscoveredIndication.query_id == ResearchQuery.id)
        .where(
            DiscoveredIndication.id == indication_id,
            ResearchQuery.user_id == current_user.id
        )
    )
    result = await db.execute(stmt)
    indication = result.scalar_one_or_none()

    if not indication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Indication not found or unauthorized access."
        )

    # Fetch evidence items
    ev_stmt = select(EvidenceItem).where(EvidenceItem.indication_id == indication_id)
    ev_result = await db.execute(ev_stmt)
    items = ev_result.scalars().all()

    trials = []
    pubs = []
    patents = []
    market = []

    for item in items:
        resp_item = EvidenceItemResponse(
            id=item.id,
            query_id=item.query_id,
            indication_id=item.indication_id,
            source_type=item.source_type,
            source_id=item.source_id,
            source_url=item.source_url,
            title=item.title,
            publication_date=item.publication_date,
            evidence_type=item.evidence_type,
            evidence_strength=item.evidence_strength,
            extracted_facts=item.extracted_facts_json,
            provenance=item.provenance_json,
            confidence=item.confidence
        )
        if item.source_type == SourceType.CLINICAL:
            trials.append(resp_item)
        elif item.source_type == SourceType.LITERATURE:
            pubs.append(resp_item)
        elif item.source_type == SourceType.PATENT:
            patents.append(resp_item)
        elif item.source_type == SourceType.MARKET:
            market.append(resp_item)

    return IndicationEvidenceListResponse(
        indication_id=indication.id,
        indication_name=indication.indication_name,
        evidence_score=indication.evidence_score,
        evidence_strength=indication.evidence_strength.value,
        clinical_trials=trials,
        literature=pubs,
        patents=patents,
        market_signals=market
    )
