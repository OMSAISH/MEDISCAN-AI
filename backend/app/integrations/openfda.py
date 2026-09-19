import logging
from typing import Dict, Any, Optional
from backend.app.integrations.base import BaseIntegration
from backend.app.config import settings

logger = logging.getLogger("mediscan.integrations.openfda")

class OpenFDAClient(BaseIntegration):
    """Client for OpenFDA drug labeling and regulatory data."""

    def __init__(self):
        super().__init__(
            source_name="OpenFDA",
            base_url="https://api.fda.gov",
            timeout_seconds=12.0,
            max_retries=2
        )

    async def get_drug_label(self, drug_name: str) -> Optional[Dict[str, Any]]:
        """Fetch FDA approved labeling and regulatory status for a drug."""
        # Clean drug name for search query
        clean_name = drug_name.replace('"', '').strip()
        search_query = f'openfda.generic_name:"{clean_name}" OR openfda.brand_name:"{clean_name}"'
        
        params: Dict[str, Any] = {
            "search": search_query,
            "limit": 1
        }
        if settings.FDA_API_KEY:
            params["api_key"] = settings.FDA_API_KEY

        data = await self._make_request("drug/label.json", params=params)
        
        if not data or "results" not in data or not data["results"]:
            logger.info(f"OpenFDA returned no label for {drug_name}. Checking fallback.")
            return self._get_controlled_fallback(drug_name)

        result = data["results"][0]
        openfda = result.get("openfda", {})
        
        indications = result.get("indications_and_usage", [""])[0] if result.get("indications_and_usage") else ""
        boxed_warning = result.get("boxed_warning", [""])[0] if result.get("boxed_warning") else ""
        brand_names = openfda.get("brand_name", [])
        generic_names = openfda.get("generic_name", [])
        app_numbers = openfda.get("application_number", [])
        substance_names = openfda.get("substance_name", [])

        return {
            "generic_name": generic_names[0] if generic_names else drug_name,
            "brand_names": brand_names,
            "substance_names": substance_names,
            "application_numbers": app_numbers,
            "indications_and_usage": indications[:1000],  # Truncate for summary
            "has_boxed_warning": bool(boxed_warning),
            "boxed_warning": boxed_warning[:500] if boxed_warning else None,
            "is_approved_fda": True,
            "source_url": f"https://labels.fda.gov",
            "is_fallback": False
        }

    def _get_controlled_fallback(self, drug_name: str) -> Optional[Dict[str, Any]]:
        normalized = drug_name.lower().strip()
        if "metformin" in normalized:
            return {
                "generic_name": "METFORMIN HYDROCHLORIDE",
                "brand_names": ["GLUCOPHAGE", "FORTAMET", "GLUMETZA"],
                "substance_names": ["METFORMIN HYDROCHLORIDE"],
                "application_numbers": ["NDA020357", "ANDA075990"],
                "indications_and_usage": "Indicated as an adjunct to diet and exercise to improve glycemic control in adults and pediatric patients 10 years of age and older with type 2 diabetes mellitus.",
                "has_boxed_warning": True,
                "boxed_warning": "WARNING: LACTIC ACIDOSIS. Postmarketing cases of metformin-associated lactic acidosis have resulted in death, hypothermia, hypotension, and resistant bradyarrhythmias.",
                "is_approved_fda": True,
                "source_url": "https://labels.fda.gov",
                "is_fallback": True
            }
        return None
