import math
from typing import List, Dict, Any

class ClinicalScorer:
    """Calculates evidence metrics for clinical trials with transparent weights."""

    PHASE_WEIGHTS = {
        "PHASE4": 1.0,
        "PHASE3": 0.85,
        "PHASE2": 0.60,
        "PHASE1": 0.35,
        "EARLY_PHASE1": 0.20,
        "Not Specified": 0.20
    }

    STATUS_WEIGHTS = {
        "COMPLETED": 1.0,
        "RECRUITING": 0.75,
        "ACTIVE_NOT_RECRUITING": 0.70,
        "NOT_YET_RECRUITING": 0.50,
        "ENROLLING_BY_INVITATION": 0.60,
        "TERMINATED": 0.20,
        "SUSPENDED": 0.15,
        "WITHDRAWN": 0.10,
        "UNKNOWN": 0.30
    }

    def score_trials(self, trials: List[Dict[str, Any]]) -> float:
        """Calculate a normalized clinical score between 0.0 and 1.0."""
        if not trials:
            return 0.0

        total_weighted_points = 0.0
        max_possible_points = 0.0

        for trial in trials:
            phases = trial.get("phases", [])
            phase_weight = 0.2
            if phases:
                phase_weight = max([self.PHASE_WEIGHTS.get(p, 0.2) for p in phases])
            else:
                phase_weight = self.PHASE_WEIGHTS.get(trial.get("phase", ""), 0.2)

            status = trial.get("status", "UNKNOWN")
            status_weight = self.STATUS_WEIGHTS.get(status, 0.3)

            # Sample size weight using log scaling: log10(N + 1) / 4 capped at 1.0
            enrollment = trial.get("enrollment", 0) or 0
            size_weight = min(1.0, math.log10(enrollment + 1) / 3.5) if enrollment > 0 else 0.2

            # Outcomes bonus: 1.0 if primary outcomes are specified
            outcomes_weight = 1.0 if trial.get("primary_outcomes") else 0.5

            # Composite trial strength
            trial_score = (
                0.40 * phase_weight +
                0.25 * status_weight +
                0.20 * size_weight +
                0.15 * outcomes_weight
            )

            total_weighted_points += trial_score
            max_possible_points += 1.0

        # Diminishing returns scaling for multiple trials: 1 - exp(-0.35 * total_points)
        raw_scaled = 1.0 - math.exp(-0.35 * total_weighted_points)
        return min(1.0, max(0.0, raw_scaled))

clinical_scorer = ClinicalScorer()
