from typing import List, Dict, Any

class ExplainabilityEngine:
    """Provides transparent evidence contribution breakdowns and research limitations."""

    def explain(
        self,
        indication_name: str,
        trials: List[Dict[str, Any]],
        publications: List[Dict[str, Any]],
        patents: List[Dict[str, Any]],
        scores: Dict[str, Any]
    ) -> Dict[str, Any]:
        positive_factors = []
        limitations = []

        # 1. Clinical Trial Factors
        if trials:
            phase3_trials = [t for t in trials if "PHASE3" in t.get("phases", []) or "PHASE4" in t.get("phases", [])]
            phase2_trials = [t for t in trials if "PHASE2" in t.get("phases", [])]
            completed = [t for t in trials if t.get("status") == "COMPLETED"]
            total_enrollment = sum(t.get("enrollment", 0) or 0 for t in trials)

            if phase3_trials:
                positive_factors.append(f"Supported by {len(phase3_trials)} late-stage (Phase 3/4) clinical study records.")
            elif phase2_trials:
                positive_factors.append(f"Demonstrated mid-stage clinical activity in {len(phase2_trials)} Phase 2 trials.")

            if completed:
                positive_factors.append(f"{len(completed)} trials reached formal completion status.")

            if total_enrollment >= 500:
                positive_factors.append(f"Substantial clinical trial cohort: aggregated enrollment of {total_enrollment:,} participants.")
            elif total_enrollment > 0:
                positive_factors.append(f"Enrolled {total_enrollment:,} participants across active/completed trials.")
        else:
            limitations.append("No dedicated interventional clinical trials identified in public registries.")

        # 2. Literature Factors
        if publications:
            meta_analyses = [p for p in publications if p.get("study_type") in ["Meta-Analysis", "Systematic Review"]]
            rcts = [p for p in publications if p.get("study_type") == "Randomized Controlled Trial"]

            if meta_analyses:
                positive_factors.append(f"{len(meta_analyses)} peer-reviewed systematic reviews or meta-analyses identified.")
            if rcts:
                positive_factors.append(f"Supported by {len(rcts)} published randomized controlled trial reports.")
            if not meta_analyses and not rcts:
                limitations.append("Literature evidence is currently limited to observational or preclinical reports.")
        else:
            limitations.append("Sparse scientific literature indexed in PubMed for this specific indication pairing.")

        # 3. Patent Factors
        if patents:
            granted = [p for p in patents if p.get("patent_number", "").endswith("B2") or p.get("patent_number", "").endswith("B1")]
            if granted:
                positive_factors.append(f"{len(granted)} granted patents protecting therapeutic compositions or methods.")
            else:
                positive_factors.append(f"{len(patents)} published patent applications in national/international jurisdictions.")
        else:
            limitations.append("No active patent landscape signals identified (open white-space or unpatented use).")

        # 4. Market & General Limitations
        limitations.append("Evidence scoring represents public research density and does not establish regulatory efficacy or safety.")

        # Narrative explanation
        evidence_score = scores.get("evidence_score", 0.0)
        strength = scores.get("evidence_strength", "Limited")
        
        narrative = (
            f"{indication_name} received an Evidence Score of {evidence_score}/100 ({strength}). "
            f"The primary score drivers are {len(trials)} clinical trials and {len(publications)} scientific publications. "
        )
        if limitations:
            narrative += f"Key research limitations include: {limitations[0].lower()}"

        return {
            "positive_factors": positive_factors,
            "limitations": limitations,
            "narrative_explanation": narrative
        }

explainability_engine = ExplainabilityEngine()
