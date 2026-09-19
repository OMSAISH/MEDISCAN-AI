import os
from datetime import datetime, timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)

class PDFReportBuilder:
    """Builds professional pharmaceutical research PDF dossiers using ReportLab."""

    def build_pdf(self, file_path: str, data: dict):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        doc = SimpleDocTemplate(
            file_path,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )

        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#0f172a"),
            fontName="Helvetica-Bold",
            spaceAfter=4
        )

        subtitle_style = ParagraphStyle(
            'DocSubtitle',
            parent=styles['Normal'],
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#0d9488"),
            fontName="Helvetica-Bold",
            spaceAfter=15
        )

        h2_style = ParagraphStyle(
            'Heading2',
            parent=styles['Heading2'],
            fontSize=14,
            leading=18,
            textColor=colors.HexColor("#1e293b"),
            fontName="Helvetica-Bold",
            spaceBefore=14,
            spaceAfter=6
        )

        body_style = ParagraphStyle(
            'Body',
            parent=styles['Normal'],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#334155")
        )

        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Normal'],
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#64748b"),
            fontName="Helvetica-Oblique"
        )

        elements = []

        # 1. Header Banner
        elements.append(Paragraph("MEDISCAN AI", title_style))
        elements.append(Paragraph("AI-POWERED DRUG REPURPOSING RESEARCH INTELLIGENCE", subtitle_style))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#0d9488"), spaceAfter=12))

        # 2. Metadata Grid
        drug_name = data.get("drug_name", "Unknown Drug")
        norm_name = data.get("normalized_drug_name", drug_name)
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        meta_data = [
            [
                Paragraph(f"<b>Investigated Drug:</b> {drug_name}", body_style),
                Paragraph(f"<b>Canonical Entity:</b> {norm_name}", body_style)
            ],
            [
                Paragraph(f"<b>Report Generated:</b> {timestamp}", body_style),
                Paragraph(f"<b>Analysis Status:</b> {data.get('status', 'COMPLETED')}", body_style)
            ]
        ]
        if data.get("research_question"):
            meta_data.append([
                Paragraph(f"<b>Research Question:</b> {data.get('research_question')}", body_style),
                Paragraph("", body_style)
            ])

        meta_table = Table(meta_data, colWidths=[260, 270])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('VALIGN', (0, 0), (-1, -1), 'TOP')
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 14))

        # 3. Executive Summary
        elements.append(Paragraph("1. Executive Research Summary", h2_style))
        exec_summary = data.get("executive_summary", "No executive summary available.")
        elements.append(Paragraph(exec_summary.replace("\n", "<br/>"), body_style))
        elements.append(Spacer(1, 14))

        # 4. Discovered Indications Table
        elements.append(Paragraph("2. Discovered Therapeutic Indications & Evidence Scores", h2_style))
        indications = data.get("indications", [])
        
        if indications:
            table_header = ["Indication", "Evidence Score", "Strength", "Trials", "Pubs", "Patents"]
            table_rows = [table_header]
            for ind in indications:
                table_rows.append([
                    ind.get("indication_name", ""),
                    f"{ind.get('evidence_score', 0):.1f} / 100",
                    ind.get("evidence_strength", "Limited"),
                    str(ind.get("clinical_trial_count", 0)),
                    str(ind.get("literature_count", 0)),
                    str(ind.get("patent_count", 0))
                ])

            ind_table = Table(table_rows, colWidths=[180, 80, 70, 60, 60, 80])
            ind_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER')
            ]))
            elements.append(ind_table)
        else:
            elements.append(Paragraph("No distinct indications discovered from the retrieved evidence.", body_style))
        
        elements.append(Spacer(1, 14))

        # 5. Methodology & Weighting
        elements.append(Paragraph("3. Scoring Methodology & Transparency", h2_style))
        methodology_text = (
            "Evidence scores are computed using an open, multi-domain weighted formula:<br/>"
            "<b>Overall Score = (0.40 × Clinical) + (0.30 × Patent) + (0.20 × Literature) + (0.10 × Market)</b><br/>"
            "• <b>Clinical Evidence (40%):</b> Weights trial phase maturity (Phase 3/4 > Phase 2 > Phase 1), cohort sample size, and completion status.<br/>"
            "• <b>Patent Landscape (30%):</b> Measures granted patents, active families, and institutional/commercial assignee presence.<br/>"
            "• <b>Scientific Literature (20%):</b> Ranks study hierarchy (Meta-analyses > RCTs > Observational > Preclinical reports).<br/>"
            "• <b>Market Intelligence (10%):</b> Assesses regulatory approval history and commercial trial sponsorship signals."
        )
        elements.append(Paragraph(methodology_text, body_style))
        elements.append(Spacer(1, 14))

        # 6. Regulatory & Scientific Disclaimer
        elements.append(Paragraph("4. Scientific Traceability & Legal Disclaimer", h2_style))
        disclaimer_box = [
            [Paragraph(
                "<b>MANDATORY SCIENTIFIC DISCLAIMER:</b> MediScan AI is a research intelligence and evidence-synthesis platform. "
                "Its outputs are intended solely to support scientific research and hypothesis generation. They do not constitute "
                "medical advice, clinical diagnosis, treatment recommendations, or regulatory approval. All evidence items maintain "
                "provenance back to public repositories (ClinicalTrials.gov, NCBI PubMed, PatentsView, and OpenFDA).",
                disclaimer_style
            )]
        ]
        disc_table = Table(disclaimer_box, colWidths=[530])
        disc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#fef2f2")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#f87171")),
            ('PADDING', (0, 0), (-1, -1), 8)
        ]))
        elements.append(disc_table)

        doc.build(elements)

pdf_builder = PDFReportBuilder()
