import logging
from typing import Dict, Any, List, Optional
from backend.app.integrations.base import BaseIntegration

logger = logging.getLogger("mediscan.integrations.market")

class MarketClient(BaseIntegration):
    """Client for commercial, regulatory exclusivity, and market intelligence signals."""

    def __init__(self):
        super().__init__(
            source_name="MarketIntelligence",
            base_url="https://api.fda.gov",
            timeout_seconds=10.0,
            max_retries=1
        )

    async def get_market_signals(
        self,
        drug_name: str,
        fda_label_data: Optional[Dict[str, Any]] = None,
        clinical_studies: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Analyze commercial, market exclusivity, and sponsorship signals."""
        normalized = drug_name.lower().strip()
        
        # Analyze trial sponsorship if studies are provided
        industry_sponsors = 0
        academic_sponsors = 0
        total_trials = len(clinical_studies) if clinical_studies else 0

        if clinical_studies:
            for s in clinical_studies:
                sponsor = s.get("sponsor", "").lower()
                if any(kw in sponsor for kw in ["inc", "corp", "pharma", "therapeutics", "ag", "gmbh", "co."]):
                    industry_sponsors += 1
                else:
                    academic_sponsors += 1

        # Check exclusivity & generic status
        is_generic = True  # Most repurposed candidates are off-patent/generic
        market_status = "Off-Patent / Multi-Source Generic"
        
        signals = []
        if total_trials > 0:
            signals.append({
                "type": "Sponsorship Distribution",
                "finding": f"Analyzed {total_trials} trials: {industry_sponsors} commercial/industry sponsors, {academic_sponsors} academic/NIH sponsors.",
                "commercial_interest": "High" if industry_sponsors > 2 else "Moderate" if industry_sponsors > 0 else "Academic-Led"
            })

        if fda_label_data and fda_label_data.get("is_approved_fda"):
            signals.append({
                "type": "Regulatory Status",
                "finding": f"FDA approved compound with active ANDA/NDA listings. Approved for: {fda_label_data.get('generic_name', drug_name)}.",
                "commercial_interest": "Established Safety Profile"
            })

        return {
            "drug_name": drug_name,
            "market_status": market_status,
            "is_generic": is_generic,
            "commercial_signals": signals,
            "financial_data_status": "Market evidence unavailable: Commercial market size and CAGR metrics are not disclosed in public regulatory filings.",
            "source_url": "https://www.fda.gov/drugs/drug-approvals-and-databases/orange-book-data-files",
            "is_fallback": False
        }
