import numpy as np
from typing import Dict, Any, List

FEATURE_NAMES = [
    "clinical_trial_count",
    "phase1_count",
    "phase2_count",
    "phase3_count",
    "phase4_count",
    "completed_trials_count",
    "total_enrollment_log",
    "literature_count",
    "meta_analysis_count",
    "rct_count",
    "observational_count",
    "patent_count",
    "granted_patent_count",
    "market_signal_count",
    "is_fda_approved_compound"
]

class FeaturePipeline:
    """Transforms raw multi-domain evidence records into numeric feature vectors for ML models."""

    def extract_features(
        self,
        trials: List[Dict[str, Any]],
        publications: List[Dict[str, Any]],
        patents: List[Dict[str, Any]],
        market_data: Dict[str, Any]
    ) -> np.ndarray:
        # Clinical features
        trial_count = len(trials)
        p1 = sum(1 for t in trials if "PHASE1" in t.get("phases", []))
        p2 = sum(1 for t in trials if "PHASE2" in t.get("phases", []))
        p3 = sum(1 for t in trials if "PHASE3" in t.get("phases", []))
        p4 = sum(1 for t in trials if "PHASE4" in t.get("phases", []))
        completed = sum(1 for t in trials if t.get("status") == "COMPLETED")
        enrollment = sum(t.get("enrollment", 0) or 0 for t in trials)
        enrollment_log = float(np.log1p(enrollment))

        # Literature features
        lit_count = len(publications)
        meta = sum(1 for p in publications if p.get("study_type") in ["Meta-Analysis", "Systematic Review"])
        rct = sum(1 for p in publications if p.get("study_type") == "Randomized Controlled Trial")
        obs = sum(1 for p in publications if p.get("study_type") == "Observational Study")

        # Patent features
        patent_count = len(patents)
        granted = sum(1 for p in patents if p.get("patent_number", "").endswith("B2") or p.get("patent_number", "").endswith("B1"))

        # Market features
        market_count = len(market_data.get("commercial_signals", []))
        is_approved = 1.0 if market_data.get("is_approved_fda") or market_data.get("is_generic") else 0.0

        feature_vector = [
            float(trial_count),
            float(p1),
            float(p2),
            float(p3),
            float(p4),
            float(completed),
            enrollment_log,
            float(lit_count),
            float(meta),
            float(rct),
            float(obs),
            float(patent_count),
            float(granted),
            float(market_count),
            is_approved
        ]

        return np.array(feature_vector, dtype=np.float32)

feature_pipeline = FeaturePipeline()
