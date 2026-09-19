import time
import logging
from typing import List, Dict, Any
from backend.app.integrations.clinicaltrials import ClinicalTrialsClient
from backend.app.services.event_stream import event_stream_manager

logger = logging.getLogger("mediscan.agents.clinical")

class ClinicalAgent:
    """Specialized agent for clinical trial intelligence."""

    def __init__(self):
        self.client = ClinicalTrialsClient()

    async def run(self, query_id: str, drug_name: str) -> Dict[str, Any]:
        start_time = time.time()
        await event_stream_manager.publish(query_id, "agent_started", {
            "agent_name": "Clinical Agent",
            "message": f"Querying ClinicalTrials.gov for '{drug_name}'..."
        })

        try:
            # Query studies
            studies = await self.client.search_studies(drug_name=drug_name, page_size=40)
            
            # Map studies to candidate indication categories
            indication_groups: Dict[str, List[Dict[str, Any]]] = {}
            for s in studies:
                conditions = s.get("conditions", [])
                if not conditions:
                    conditions = ["Unspecified Condition"]
                
                for cond in conditions:
                    cleaned_cond = self._clean_condition_name(cond)
                    if cleaned_cond not in indication_groups:
                        indication_groups[cleaned_cond] = []
                    indication_groups[cleaned_cond].append(s)

            elapsed_ms = int((time.time() - start_time) * 1000)
            await event_stream_manager.publish(query_id, "agent_completed", {
                "agent_name": "Clinical Agent",
                "items_found": len(studies),
                "indications_detected": len(indication_groups),
                "execution_time_ms": elapsed_ms
            })

            return {
                "status": "COMPLETED",
                "trials": studies,
                "indication_groups": indication_groups,
                "execution_time_ms": elapsed_ms,
                "error": None
            }

        except Exception as e:
            logger.error(f"ClinicalAgent failed for query {query_id}: {e}")
            elapsed_ms = int((time.time() - start_time) * 1000)
            await event_stream_manager.publish(query_id, "agent_failed", {
                "agent_name": "Clinical Agent",
                "error": str(e),
                "execution_time_ms": elapsed_ms
            })
            return {
                "status": "FAILED",
                "trials": [],
                "indication_groups": {},
                "execution_time_ms": elapsed_ms,
                "error": str(e)
            }

    def _clean_condition_name(self, condition: str) -> str:
        """Standardize condition names for clean clustering."""
        cond_lower = condition.lower().strip()
        if "pancrea" in cond_lower:
            return "Pancreatic Cancer"
        if "colorectal" in cond_lower or "colon" in cond_lower or "rectal" in cond_lower or "adenoma" in cond_lower:
            return "Colorectal Neoplasms / Adenoma"
        if "aging" in cond_lower or "longevity" in cond_lower or "senescence" in cond_lower or "frailty" in cond_lower:
            return "Aging & Age-Related Decline"
        if "alzheimer" in cond_lower or "cognitive" in cond_lower or "dementia" in cond_lower:
            return "Cognitive Impairment & Alzheimer's Disease"
        if "fatty liver" in cond_lower or "nash" in cond_lower or "nafld" in cond_lower or "steatohepatitis" in cond_lower:
            return "Non-Alcoholic Fatty Liver Disease (NAFLD/NASH)"
        if "coronary" in cond_lower or "ventricular" in cond_lower or "heart failure" in cond_lower or "cardiac" in cond_lower:
            return "Cardiovascular Remodeling & Heart Failure"
        if "diabetes" in cond_lower or "glycemic" in cond_lower:
            return "Type 2 Diabetes Mellitus"
        return condition.title()
