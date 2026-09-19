import time
import logging
from typing import Dict, Any, List, Optional
from backend.app.integrations.openfda import OpenFDAClient
from backend.app.integrations.market import MarketClient
from backend.app.services.event_stream import event_stream_manager

logger = logging.getLogger("mediscan.agents.market")

class MarketAgent:
    """Specialized agent for commercial, regulatory, and market signals."""

    def __init__(self):
        self.fda_client = OpenFDAClient()
        self.market_client = MarketClient()

    async def run(
        self,
        query_id: str,
        drug_name: str,
        clinical_trials: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        start_time = time.time()
        await event_stream_manager.publish(query_id, "agent_started", {
            "agent_name": "Market Agent",
            "message": f"Analyzing FDA regulatory status and market signals for '{drug_name}'..."
        })

        try:
            fda_data = await self.fda_client.get_drug_label(drug_name)
            market_signals = await self.market_client.get_market_signals(
                drug_name=drug_name,
                fda_label_data=fda_data,
                clinical_studies=clinical_trials
            )

            elapsed_ms = int((time.time() - start_time) * 1000)
            items_found = len(market_signals.get("commercial_signals", []))
            if fda_data:
                items_found += 1

            await event_stream_manager.publish(query_id, "agent_completed", {
                "agent_name": "Market Agent",
                "items_found": items_found,
                "execution_time_ms": elapsed_ms
            })

            return {
                "status": "COMPLETED",
                "fda_data": fda_data,
                "market_data": market_signals,
                "execution_time_ms": elapsed_ms,
                "error": None
            }

        except Exception as e:
            logger.error(f"MarketAgent failed for query {query_id}: {e}")
            elapsed_ms = int((time.time() - start_time) * 1000)
            await event_stream_manager.publish(query_id, "agent_failed", {
                "agent_name": "Market Agent",
                "error": str(e),
                "execution_time_ms": elapsed_ms
            })
            return {
                "status": "FAILED",
                "fda_data": None,
                "market_data": {},
                "execution_time_ms": elapsed_ms,
                "error": str(e)
            }
