import time
import logging
from typing import List, Dict, Any
from backend.app.integrations.patents import PatentClient
from backend.app.services.event_stream import event_stream_manager

logger = logging.getLogger("mediscan.agents.patent")

class PatentAgent:
    """Specialized agent for patent landscape and intellectual property intelligence."""

    def __init__(self):
        self.client = PatentClient()

    async def run(self, query_id: str, drug_name: str) -> Dict[str, Any]:
        start_time = time.time()
        await event_stream_manager.publish(query_id, "agent_started", {
            "agent_name": "Patent Agent",
            "message": f"Analyzing patent records and IP landscape for '{drug_name}'..."
        })

        try:
            patents = await self.client.search_patents(drug_name=drug_name, max_results=25)
            
            # Group patents by indication
            patent_map: Dict[str, List[Dict[str, Any]]] = {}
            for p in patents:
                combined_text = (p.get("title", "") + " " + p.get("abstract", "")).lower()
                matched = self._match_indication_from_text(combined_text)
                for ind in matched:
                    if ind not in patent_map:
                        patent_map[ind] = []
                    patent_map[ind].append(p)

            elapsed_ms = int((time.time() - start_time) * 1000)
            await event_stream_manager.publish(query_id, "agent_completed", {
                "agent_name": "Patent Agent",
                "items_found": len(patents),
                "indications_detected": len(patent_map),
                "execution_time_ms": elapsed_ms
            })

            return {
                "status": "COMPLETED",
                "patents": patents,
                "patent_map": patent_map,
                "execution_time_ms": elapsed_ms,
                "error": None
            }

        except Exception as e:
            logger.error(f"PatentAgent failed for query {query_id}: {e}")
            elapsed_ms = int((time.time() - start_time) * 1000)
            await event_stream_manager.publish(query_id, "agent_failed", {
                "agent_name": "Patent Agent",
                "error": str(e),
                "execution_time_ms": elapsed_ms
            })
            return {
                "status": "FAILED",
                "patents": [],
                "patent_map": {},
                "execution_time_ms": elapsed_ms,
                "error": str(e)
            }

    def _match_indication_from_text(self, text: str) -> List[str]:
        matched = []
        if "pancrea" in text or "colorectal" in text or "neoplasm" in text or "cancer" in text:
            matched.append("Pancreatic Cancer")
            matched.append("Colorectal Neoplasms / Adenoma")
        if "aging" in text or "senescence" in text or "longevity" in text:
            matched.append("Aging & Age-Related Decline")
        if "neuro" in text or "alzheimer" in text or "cognitive" in text:
            matched.append("Cognitive Impairment & Alzheimer's Disease")
        if "nash" in text or "nafld" in text or "steatohepatitis" in text or "liver" in text:
            matched.append("Non-Alcoholic Fatty Liver Disease (NAFLD/NASH)")
        if "cardiac" in text or "heart" in text or "cardiovascular" in text:
            matched.append("Cardiovascular Remodeling & Heart Failure")
        if "diabetes" in text:
            matched.append("Type 2 Diabetes Mellitus")
        return matched if matched else ["General Formulation / Drug Delivery"]
