import os
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.app.database.session import get_db
from backend.app.models.user import User
from backend.app.models.research import ResearchQuery
from backend.app.models.report import Report, ReportFormat
from backend.app.schemas.report import GenerateReportRequest, ReportResponse
from backend.app.security.rbac import get_current_active_user, record_audit_log
from backend.app.reports.generator import report_generator

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.post("/{query_id}/generate", response_model=ReportResponse)
async def generate_research_report(
    query_id: str,
    request_in: GenerateReportRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(ResearchQuery)
        .where(ResearchQuery.id == query_id, ResearchQuery.user_id == current_user.id)
        .options(selectinload(ResearchQuery.indications))
    )
    result = await db.execute(stmt)
    query = result.scalar_one_or_none()

    if not query:
        raise HTTPException(status_code=404, detail="Research query not found.")

    # Prepare report data
    report_data = {
        "drug_name": query.drug_name,
        "normalized_drug_name": query.normalized_drug_name,
        "research_question": query.research_question,
        "status": query.status.value,
        "executive_summary": query.executive_summary,
        "indications": [
            {
                "indication_name": ind.indication_name,
                "evidence_score": ind.evidence_score,
                "evidence_strength": ind.evidence_strength.value,
                "clinical_score": ind.clinical_score,
                "literature_score": ind.literature_score,
                "patent_score": ind.patent_score,
                "market_score": ind.market_score,
                "clinical_trial_count": ind.clinical_trial_count,
                "literature_count": ind.literature_count,
                "patent_count": ind.patent_count,
                "market_signal_count": ind.market_signal_count,
                "explanation": ind.explanation
            }
            for ind in query.indications
        ]
    }

    report = await report_generator.generate_report(
        db=db,
        query_id=query.id,
        user_id=current_user.id,
        report_format=request_in.report_format,
        data=report_data
    )

    client_ip = request.client.host if request.client else None
    await record_audit_log(
        db=db,
        user_id=current_user.id,
        action="GENERATE_REPORT",
        resource_type="REPORT",
        resource_id=report.id,
        ip_address=client_ip,
        details={"format": report.report_format.value, "file_path": report.file_path}
    )

    return report

@router.get("/{report_id}/download")
async def download_report(
    report_id: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Report).where(Report.id == report_id, Report.user_id == current_user.id)
    result = await db.execute(stmt)
    report = result.scalar_one_or_none()

    if not report or not os.path.exists(report.file_path):
        raise HTTPException(status_code=404, detail="Report file not found.")

    media_types = {
        ReportFormat.PDF: "application/pdf",
        ReportFormat.HTML: "text/html",
        ReportFormat.JSON: "application/json",
        ReportFormat.CSV: "text/csv"
    }

    media_type = media_types.get(report.report_format, "application/octet-stream")
    filename = os.path.basename(report.file_path)

    return FileResponse(
        path=report.file_path,
        media_type=media_type,
        filename=filename
    )
