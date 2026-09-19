import os
import csv
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.report import Report, ReportFormat
from backend.app.reports.pdf_builder import pdf_builder

REPORTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/reports"))

class ReportGenerator:
    """Generates and manages research reports in PDF, HTML, JSON, and CSV formats."""

    def __init__(self):
        os.makedirs(REPORTS_DIR, exist_ok=True)

    async def generate_report(
        self,
        db: AsyncSession,
        query_id: str,
        user_id: str,
        report_format: ReportFormat,
        data: Dict[str, Any]
    ) -> Report:
        report_id = str(uuid.uuid4())
        drug_name = data.get("drug_name", "Drug").replace(" ", "_").lower()
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"mediscan_{drug_name}_{timestamp}.{report_format.value.lower()}"
        file_path = os.path.join(REPORTS_DIR, filename)

        if report_format == ReportFormat.PDF:
            pdf_builder.build_pdf(file_path, data)
        elif report_format == ReportFormat.JSON:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
        elif report_format == ReportFormat.CSV:
            self._generate_csv(file_path, data)
        elif report_format == ReportFormat.HTML:
            self._generate_html(file_path, data)
        else:
            raise ValueError(f"Unsupported report format: {report_format}")

        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0

        report = Report(
            id=report_id,
            query_id=query_id,
            user_id=user_id,
            title=f"MediScan Research Report - {data.get('drug_name', 'Drug')} ({report_format.value})",
            report_format=report_format,
            file_path=file_path,
            file_size_bytes=file_size,
            metadata_json={
                "indications_count": len(data.get("indications", [])),
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
        )
        db.add(report)
        await db.commit()
        return report

    def _generate_csv(self, file_path: str, data: Dict[str, Any]):
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Indication Name", "Evidence Score", "Evidence Strength", 
                "Clinical Score", "Literature Score", "Patent Score", "Market Score",
                "Clinical Trials Count", "Literature Count", "Patent Count", "Market Signal Count",
                "Key Explanation"
            ])
            for ind in data.get("indications", []):
                writer.writerow([
                    ind.get("indication_name"),
                    ind.get("evidence_score"),
                    ind.get("evidence_strength"),
                    ind.get("clinical_score"),
                    ind.get("literature_score"),
                    ind.get("patent_score"),
                    ind.get("market_score"),
                    ind.get("clinical_trial_count"),
                    ind.get("literature_count"),
                    ind.get("patent_count"),
                    ind.get("market_signal_count"),
                    ind.get("explanation")
                ])

    def _generate_html(self, file_path: str, data: Dict[str, Any]):
        drug = data.get("drug_name", "Drug")
        summary = data.get("executive_summary", "").replace("\n", "<br/>")
        
        rows = ""
        for ind in data.get("indications", []):
            rows += f"""
            <tr>
                <td style="padding:10px; border:1px solid #e2e8f0; font-weight:600;">{ind.get('indication_name')}</td>
                <td style="padding:10px; border:1px solid #e2e8f0; text-align:center; font-weight:bold; color:#0d9488;">{ind.get('evidence_score')} / 100</td>
                <td style="padding:10px; border:1px solid #e2e8f0; text-align:center;">{ind.get('evidence_strength')}</td>
                <td style="padding:10px; border:1px solid #e2e8f0; text-align:center;">{ind.get('clinical_trial_count')}</td>
                <td style="padding:10px; border:1px solid #e2e8f0; text-align:center;">{ind.get('literature_count')}</td>
                <td style="padding:10px; border:1px solid #e2e8f0; text-align:center;">{ind.get('patent_count')}</td>
            </tr>
            """

        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"/>
    <title>MediScan AI Research Dossier - {drug}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 40px; color: #1e293b; line-height: 1.6; background-color: #f8fafc; }}
        .container {{ max-width: 900px; margin: auto; background: white; padding: 32px; border-radius: 8px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }}
        h1 {{ color: #0f172a; margin-bottom: 4px; }}
        .badge {{ background: #0d9488; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th {{ background: #0f172a; color: white; padding: 10px; text-align: left; font-size: 13px; }}
        .disclaimer {{ background: #fef2f2; border: 1px solid #f87171; padding: 16px; border-radius: 6px; font-size: 12px; color: #991b1b; margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>MEDISCAN AI</h1>
        <span class="badge">DRUG REPURPOSING RESEARCH DOSSIER</span>
        <hr style="margin: 20px 0; border: 0; border-top: 2px solid #0d9488;"/>
        
        <h2>Investigated Drug: {drug}</h2>
        <p><strong>Canonical Entity:</strong> {data.get('normalized_drug_name', drug)}</p>
        <p><strong>Analysis Status:</strong> {data.get('status')}</p>

        <h3>Executive Research Summary</h3>
        <p>{summary}</p>

        <h3>Discovered Indications & Evidence</h3>
        <table>
            <thead>
                <tr>
                    <th>Indication</th>
                    <th>Evidence Score</th>
                    <th>Strength</th>
                    <th>Trials</th>
                    <th>Publications</th>
                    <th>Patents</th>
                </tr>
            </thead>
            <tbody>
                {rows}
            </tbody>
        </table>

        <div class="disclaimer">
            <strong>MANDATORY SCIENTIFIC DISCLAIMER:</strong> MediScan AI is a research intelligence and evidence-synthesis platform. 
            Its outputs are intended solely to support scientific research and hypothesis generation. They do not constitute 
            medical advice, clinical diagnosis, treatment recommendations, or regulatory approval.
        </div>
    </div>
</body>
</html>"""
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)

report_generator = ReportGenerator()
