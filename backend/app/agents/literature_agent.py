import time
import logging
from typing import List, Dict, Any
from backend.app.integrations.pubmed import PubMedClient
from backend.app.services.event_stream import event_stream_manager

logger = logging.getLogger("mediscan.agents.literature")

class LiteratureAgent:
    """Specialized agent for scientific literature and publication evidence."""

    def __init__(self):
        self.client = PubMedClient()

    async def run(self, query_id: str, drug_name: str) -> Dict[str, Any]:
        start_time = time.time()
        await event_stream_manager.publish(query_id, "agent_started", {
            "agent_name": "Literature Agent",
            "message": f"Searching PubMed & scientific repositories for '{drug_name}'..."
        })

        try:
            publications = await self.client.search_publications(drug_name=drug_name, max_results=30)
            
            # Map publications to indications based on title/abstract keywords
            indication_map: Dict[str, List[Dict[str, Any]]] = {}
            for pub in publications:
                title = pub.get("title", "").lower()
                matched = self._match_indication_from_text(title)
                for ind in matched:
                    if ind not in indication_map:
                        indication_map[ind] = []
                    indication_map[ind].append(pub)

            elapsed_ms = int((time.time() - start_time) * 1000)
            await event_stream_manager.publish(query_id, "agent_completed", {
                "agent_name": "Literature Agent",
                "items_found": len(publications),
                "indications_detected": len(indication_map),
                "execution_time_ms": elapsed_ms
            })

            return {
                "status": "COMPLETED",
                "publications": publications,
                "indication_map": indication_map,
                "execution_time_ms": elapsed_ms,
                "error": None
            }

        except Exception as e:
            logger.error(f"LiteratureAgent failed for query {query_id}: {e}")
            elapsed_ms = int((time.time() - start_time) * 1000)
            await event_stream_manager.publish(query_id, "agent_failed", {
                "agent_name": "Literature Agent",
                "error": str(e),
                "execution_time_ms": elapsed_ms
            })
            return {
                "status": "FAILED",
                "publications": [],
                "indication_map": {},
                "execution_time_ms": elapsed_ms,
                "error": str(e)
            }

    def _match_indication_from_text(self, text: str) -> List[str]:
        matched = []
        if "pancrea" in text:
            matched.append("Pancreatic Cancer")
        if "colorectal" in text or "colon" in text or "adenoma" in text:
            matched.append("Colorectal Neoplasms / Adenoma")
        if "cancer" in text or "neoplasm" in text or "tumor" in text:
            if "Pancreatic Cancer" not in matched and "Colorectal Neoplasms / Adenoma" not in matched:
                matched.append("Oncology (Broad)")
        if "aging" in text or "longevity" in text or "senescence" in text:
            matched.append("Aging & Age-Related Decline")
        if "alzheimer" in text or "cognitive" in text or "dementia" in text:
            matched.append("Cognitive Impairment & Alzheimer's Disease")
        if "liver" in text or "nash" in text or "nafld" in text or "steatohepatitis" in text:
            matched.append("Non-Alcoholic Fatty Liver Disease (NAFLD/NASH)")
        if "cardiac" in text or "heart failure" in text or "cardiovascular" in text:
            matched.append("Cardiovascular Remodeling & Heart Failure")
        if "diabetes" in text:
            matched.append("Type 2 Diabetes Mellitus")
        return matched if matched else ["General Biomedical Research"]
