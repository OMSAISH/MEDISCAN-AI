import logging
from typing import Dict, Any, List, Optional
from backend.app.config import settings

logger = logging.getLogger("mediscan.services.llm_provider")

DISCLAIMER_TEXT = (
    "MediScan AI is a research intelligence and evidence-synthesis platform. "
    "Its outputs are intended to support scientific research and hypothesis generation. "
    "They do not constitute medical advice, clinical diagnosis, treatment recommendations, "
    "or regulatory approval."
)

class LLMProvider:
    """Pluggable LLM interface supporting OpenAI, Anthropic, and Grounded Extractive Synthesis."""

    def __init__(self):
        self.provider = settings.MODEL_PROVIDER
        self.model_name = settings.MODEL_NAME

    async def decompose_query(self, drug_name: str, question: Optional[str]) -> List[str]:
        """Decompose research question into focused therapeutic query hypotheses."""
        if not question:
            return [
                f"{drug_name} in oncology and neoplastic disease",
                f"{drug_name} in neurodegenerative and cognitive disorders",
                f"{drug_name} in cardiovascular and metabolic remodeling",
                f"{drug_name} in cellular senescence and longevity"
            ]
        
        # Simple extraction or query breakdown
        hypotheses = [
            f"Investigate {drug_name} evidence for: {question}",
            f"{drug_name} clinical trials related to target mechanisms",
            f"{drug_name} scientific publications on secondary pathways"
        ]
        return hypotheses

    async def synthesize_analysis(
        self,
        drug_name: str,
        research_question: Optional[str],
        indications: List[Dict[str, Any]],
        clinical_count: int,
        literature_count: int,
        patent_count: int,
        market_count: int
    ) -> Dict[str, str]:
        """Generate a grounded executive research summary strictly based on collected evidence."""
        
        top_indications = sorted(indications, key=lambda x: x.get("evidence_score", 0), reverse=True)[:3]
        indication_names = [ind.get("indication_name") for ind in top_indications if ind.get("indication_name")]
        
        summary_paragraphs = [
            f"MediScan AI completed a multi-domain research investigation for **{drug_name}**.",
            f"Evidence aggregation across public repositories identified **{len(indications)} distinct therapeutic indications** "
            f"supported by {clinical_count} clinical trial records, {literature_count} peer-reviewed scientific publications, "
            f"{patent_count} patent records, and {market_count} commercial/regulatory signals."
        ]

        if indication_names:
            summary_paragraphs.append(
                f"The highest-scoring investigated indications based on empirical evidence volume and phase maturity are: "
                f"**{', '.join(indication_names)}**."
            )
        else:
            summary_paragraphs.append(
                "Limited repurposing signals were identified across the queried therapeutic spaces."
            )

        summary_paragraphs.append(
            "Note: Evidence scores represent research density and clinical phase progression in public databases, "
            "not verified therapeutic efficacy or clinical approval."
        )

        return {
            "executive_summary": "\n\n".join(summary_paragraphs),
            "disclaimer": DISCLAIMER_TEXT
        }

llm_provider = LLMProvider()
