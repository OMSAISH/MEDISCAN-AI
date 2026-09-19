import math
from typing import Dict, Any, List, Optional
from backend.app.scoring.clinical_scorer import clinical_scorer
from backend.app.models.research import EvidenceStrength

class ScoringEngine:
    """Transparent multi-domain evidence scoring engine.
    
    Formula:
    Score = 100 * (0.40 * Clinical + 0.30 * Patent + 0.20 * Literature + 0.10 * Market)
    """

    STUDY_TYPE_WEIGHTS = {
        "Meta-Analysis": 1.0,
        "Systematic Review": 0.90,
        "Randomized Controlled Trial": 0.85,
        "Clinical Trial": 0.70,
        "Observational Study": 0.50,
        "Narrative Review": 0.40,
        "Preclinical / Mechanistic Study": 0.30,
        "Other": 0.25
    }

    def score_indication(
        self,
        trials: List[Dict[str, Any]],
        publications: List[Dict[str, Any]],
        patents: List[Dict[str, Any]],
        market_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Compute all component scores and overall evidence score."""
        
        # 1. Clinical Evidence Score (0.0 to 1.0)
        clinical_norm = clinical_scorer.score_trials(trials)

        # 2. Literature Score (0.0 to 1.0)
        lit_points = 0.0
        for pub in publications:
            stype = pub.get("study_type", "Other")
            weight = self.STUDY_TYPE_WEIGHTS.get(stype, 0.25)
            lit_points += weight
        literature_norm = 1.0 - math.exp(-0.40 * lit_points) if publications else 0.0

        # 3. Patent Score (0.0 to 1.0)
        patent_points = 0.0
        for p in patents:
            # Grant vs application
            pnum = p.get("patent_number", "")
            base = 1.0 if pnum.endswith("B2") or pnum.endswith("B1") else 0.7
            patent_points += base
        patent_norm = 1.0 - math.exp(-0.50 * patent_points) if patents else 0.0

        # 4. Market Score (0.0 to 1.0)
        market_norm = 0.0
        if market_data:
            signals = market_data.get("commercial_signals", [])
            # If FDA approved compound, baseline safety/market presence is established
            if market_data.get("is_generic"):
                market_norm += 0.4
            if len(signals) > 0:
                market_norm += min(0.6, len(signals) * 0.3)
        market_norm = min(1.0, market_norm)

        # 5. Composite Evidence Score
        composite_score = (
            0.40 * clinical_norm +
            0.30 * patent_norm +
            0.20 * literature_norm +
            0.10 * market_norm
        )
        
        # Scale to 0-100
        overall_score = round(composite_score * 100, 1)
        clinical_score_100 = round(clinical_norm * 100, 1)
        patent_score_100 = round(patent_norm * 100, 1)
        literature_score_100 = round(literature_norm * 100, 1)
        market_score_100 = round(market_norm * 100, 1)

        # Assign Evidence Strength category
        if overall_score >= 75.0:
            strength = EvidenceStrength.STRONG
        elif overall_score >= 50.0:
            strength = EvidenceStrength.MODERATE
        elif overall_score >= 25.0:
            strength = EvidenceStrength.LIMITED
        else:
            strength = EvidenceStrength.INSUFFICIENT

        return {
            "evidence_score": overall_score,
            "clinical_score": clinical_score_100,
            "patent_score": patent_score_100,
            "literature_score": literature_score_100,
            "market_score": market_score_100,
            "evidence_strength": strength,
            "methodology_note": (
                "Evidence score calculated using research prototype weighting: "
                "40% Clinical + 30% Patent + 20% Literature + 10% Market. "
                "This score reflects evidence volume and trial phase maturity, not a validated medical probability."
            )
        }

scoring_engine = ScoringEngine()
