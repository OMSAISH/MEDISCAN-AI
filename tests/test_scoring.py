from backend.app.scoring.clinical_scorer import clinical_scorer
from backend.app.scoring.scoring_engine import scoring_engine
from backend.app.models.research import EvidenceStrength

def test_clinical_scorer_weights():
    # Empty trials should give 0.0
    assert clinical_scorer.score_trials([]) == 0.0

    # Phase 3 completed trial should score significantly higher than Phase 1 terminated
    phase3_trial = [{
        "phases": ["PHASE3"],
        "status": "COMPLETED",
        "enrollment": 800,
        "primary_outcomes": ["Overall Survival"]
    }]
    phase1_trial = [{
        "phases": ["PHASE1"],
        "status": "TERMINATED",
        "enrollment": 15,
        "primary_outcomes": []
    }]

    score_p3 = clinical_scorer.score_trials(phase3_trial)
    score_p1 = clinical_scorer.score_trials(phase1_trial)
    assert score_p3 > score_p1
    assert 0.0 <= score_p3 <= 1.0

def test_scoring_engine_composite():
    sample_trials = [
        {"phases": ["PHASE3"], "status": "COMPLETED", "enrollment": 500, "primary_outcomes": ["Recurrence Rate"]},
        {"phases": ["PHASE2"], "status": "COMPLETED", "enrollment": 120, "primary_outcomes": ["Safety"]}
    ]
    sample_pubs = [
        {"study_type": "Meta-Analysis"},
        {"study_type": "Randomized Controlled Trial"},
        {"study_type": "Systematic Review"}
    ]
    sample_patents = [
        {"patent_number": "US10485782B2"},
        {"patent_number": "US9980931B2"}
    ]
    sample_market = {
        "is_generic": True,
        "commercial_signals": [{"type": "Sponsorship", "commercial_interest": "High"}]
    }

    result = scoring_engine.score_indication(
        trials=sample_trials,
        publications=sample_pubs,
        patents=sample_patents,
        market_data=sample_market
    )

    assert 0 <= result["evidence_score"] <= 100
    assert 0 <= result["clinical_score"] <= 100
    assert 0 <= result["literature_score"] <= 100
    assert 0 <= result["patent_score"] <= 100
    assert 0 <= result["market_score"] <= 100
    assert result["evidence_strength"] in [EvidenceStrength.STRONG, EvidenceStrength.MODERATE]
