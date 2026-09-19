import os
import pytest
from backend.app.reports.pdf_builder import pdf_builder
from backend.app.reports.generator import report_generator

def test_pdf_report_generation(tmp_path):
    test_pdf = str(tmp_path / "test_report.pdf")
    data = {
        "drug_name": "Metformin",
        "normalized_drug_name": "Metformin Hydrochloride",
        "research_question": "Investigate oncology and neuroprotective indications",
        "status": "COMPLETED",
        "executive_summary": "MediScan AI identified strong evidence for Metformin in oncological applications.",
        "indications": [
            {
                "indication_name": "Colorectal Neoplasms / Adenoma",
                "evidence_score": 82.5,
                "evidence_strength": "Strong",
                "clinical_trial_count": 6,
                "literature_count": 24,
                "patent_count": 4
            },
            {
                "indication_name": "Pancreatic Cancer",
                "evidence_score": 71.0,
                "evidence_strength": "Moderate",
                "clinical_trial_count": 4,
                "literature_count": 18,
                "patent_count": 2
            }
        ]
    }

    pdf_builder.build_pdf(test_pdf, data)
    assert os.path.exists(test_pdf)
    assert os.path.getsize(test_pdf) > 1000  # PDF generated with content
