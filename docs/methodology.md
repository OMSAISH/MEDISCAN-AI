# MediScan AI Scoring & Research Methodology

MediScan AI employs an evidence-first, mathematically transparent scoring and ranking methodology to evaluate drug repurposing opportunities. Unlike opaque generative AI systems that synthesize unsubstantiated claims, MediScan AI bases all evaluations on verifiable public records (clinical trials, scientific publications, patent filings, and regulatory labels).

---

## 1. Multi-Domain Composite Scoring Model

Each discovered repurposing indication receives a **Composite Repurposing Score ($S_{\text{composite}}$)** scaled continuously from **0.0 to 100.0**. The composite score is a weighted linear combination of four domain-specific evidence engines:

$$S_{\text{composite}} = 0.40 \cdot S_{\text{clinical}} + 0.30 \cdot S_{\text{patent}} + 0.20 \cdot S_{\text{literature}} + 0.10 \cdot S_{\text{market}}$$

```
+-----------------------------------------------------------------------+
|                       COMPOSITE SCORE (0 - 100)                       |
+-------------------+-------------------+---------------+---------------+
|  Clinical (40%)   |   Patent (30%)    | Literature(20%)| Market (10%) |
|  - Study Phase    |   - Claim Types   | - Evidence    | - Unmet Need  |
|  - Trial Status   |   - Expiry Term   |   Hierarchy   | - Exclusivity |
|  - Enrollment     |   - Jurisdictions | - Recency     | - Competition |
+-------------------+-------------------+---------------+---------------+
```

---

## 2. Domain Scoring Formulations

### 2.1 Clinical Evidence Score ($S_{\text{clinical}}$, Weight: 0.40)
Clinical trials constitute the highest-order evidentiary basis for drug repositioning. The clinical score evaluates trial maturity, completion status, cohort scale, and primary endpoint definition:

$$S_{\text{clinical}} = \min\left(100.0, \; \sum_{t \in \text{Trials}} \left( W_{\text{phase}}(t) \cdot W_{\text{status}}(t) \cdot \ln(1 + N_{\text{enrollment}}(t)) \cdot W_{\text{endpoints}}(t) \right)\right)$$

#### Phase Weights ($W_{\text{phase}}$)
| Trial Phase | Weight | Rationale |
|-------------|--------|-----------|
| Phase 4 (Post-Marketing) | 1.00 | Confirmed real-world clinical effectiveness |
| Phase 3 (Confirmatory) | 0.85 | Large-scale randomized comparative efficacy |
| Phase 2 (Exploratory) | 0.60 | Proof of concept and therapeutic efficacy |
| Phase 1 / Early Phase 1 | 0.30 | Safety, pharmacokinetics, and tolerability |
| Observational / Not Applicable | 0.20 | Associative real-world evidence |

#### Trial Status Multipliers ($W_{\text{status}}$)
| Status | Multiplier | Rationale |
|--------|------------|-----------|
| `COMPLETED` | 1.00 | Full protocol executed; data evaluable |
| `ACTIVE_NOT_RECRUITING` | 0.75 | Enrollment completed; follow-up ongoing |
| `RECRUITING` / `ENROLLING` | 0.50 | Trial underway; efficacy pending |
| `TERMINATED` (Efficacy Failure) | 0.05 | Severe negative signal |
| `WITHDRAWN` / `SUSPENDED` | 0.10 | Discontinued prior to primary endpoint |

---

### 2.2 Patent & Exclusivity Score ($S_{\text{patent}}$, Weight: 0.30)
Evaluates intellectual property protection and method-of-use landscape for the repurposing indication:

$$S_{\text{patent}} = \min\left(100.0, \; S_{\text{claims}} + S_{\text{term}} + S_{\text{jurisdiction}}\right)$$

1. **Claim Specificity ($S_{\text{claims}}$)**:
   - Method-of-Use Claim for Target Indication: Up to **40 points**.
   - Formulation / Combination Claim: Up to **25 points**.
   - Broad Mechanism / Derivative Claim: Up to **15 points**.
2. **Remaining Exclusivity Term ($S_{\text{term}}$)**:
   - Expiration > 10 years: **30 points** (High commercial runway).
   - Expiration 5–10 years: **20 points**.
   - Expiration < 5 years or Expired: **10 points** (Generic repurposing or freedom-to-operate).
3. **Jurisdictional Coverage ($S_{\text{jurisdiction}}$)**:
   - Granted in US, EPO, and WIPO: **30 points**.
   - Granted in single major jurisdiction: **15 points**.
   - Application pending: **10 points**.

---

### 2.3 Scientific Literature Score ($S_{\text{literature}}$, Weight: 0.20)
Assesses the quality, methodological rigor, and scientific consensus in peer-reviewed biomedical publications:

$$S_{\text{literature}} = \min\left(100.0, \; \sum_{p \in \text{Papers}} W_{\text{type}}(p) \cdot W_{\text{recency}}(p)\right)$$

#### Evidence Hierarchy Weights ($W_{\text{type}}$)
| Study Design Class | Base Score |
|--------------------|------------|
| Systematic Review & Meta-Analysis | 35.0 |
| Randomized Controlled Trial (RCT) | 28.0 |
| Prospective Cohort / Observational Study | 18.0 |
| In Vivo Animal Model / Preclinical | 12.0 |
| In Vitro Cell Culture / Mechanism Study | 6.0 |
| Case Report / Letter | 3.0 |

#### Recency Multiplier ($W_{\text{recency}}$)
- Published within last 3 years: $1.00$
- Published 4–7 years ago: $0.80$
- Published 8–12 years ago: $0.60$
- Published > 12 years ago: $0.40$

---

### 2.4 Market & Clinical Need Score ($S_{\text{market}}$, Weight: 0.10)
Quantifies unmet medical need, regulatory acceleration incentives, and commercial feasibility:

1. **Orphan Drug / Expedited Pathway**: Indications with Orphan Drug Designation or Breakthrough Therapy status receive up to **40 points**.
2. **Disease Burden / Unmet Need**: High-mortality or refractory indications lacking approved standard-of-care receive up to **35 points**.
3. **Competitive Density**: Uncrowded drug classes receive up to **25 points**.

---

## 3. Evidence Confidence Tiers

Indications are categorized into three distinct confidence tiers based on their composite scores:

```
[0.0 ---------------- 45.0 ---------------- 70.0 ---------------- 100.0]
     EXPLORATORY             MODERATE                  HIGH
   PRECLINICAL ONLY         EARLY CLINICAL           CONFIRMATORY
```

- **High Confidence ($\ge 70.0$)**: Supported by Phase 2/3 interventional trials, peer-reviewed clinical studies, and clear patent/regulatory positioning.
- **Moderate Confidence ($45.0 - 69.9$)**: Supported by early Phase 1 trials, mechanistic preclinical models, and emerging observational evidence.
- **Exploratory ($< 45.0$)**: Supported primarily by in vitro assays, retrospective cohort associations, or speculative patent filings.

---

## 4. Machine Learning Subsystem (`/ml`)

In addition to the deterministic scoring engine, MediScan AI trains an ensemble model to estimate the empirical probability of repositioning success:

- **Model**: `RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)`
- **Feature Vector (15 dimensions)**:
  1. `clinical_trials_count`: Total number of identified trials
  2. `has_phase_3`: Boolean indicator (1/0)
  3. `has_phase_2`: Boolean indicator (1/0)
  4. `has_phase_1`: Boolean indicator (1/0)
  5. `total_enrollment`: Total patient cohort across all trials
  6. `completed_trials_count`: Number of trials marked COMPLETED
  7. `literature_count`: Total peer-reviewed publications
  8. `meta_analysis_count`: Count of systematic reviews/meta-analyses
  9. `in_vivo_count`: Count of animal model studies
  10. `patent_count`: Total patent filings
  11. `has_active_method_of_use`: Boolean indicator (1/0)
  12. `years_to_patent_expiry`: Remaining patent protection duration
  13. `orphan_designation`: Boolean indicator (1/0)
  14. `has_fda_approved_precedent`: Boolean indicator (1/0)
  15. `mechanistic_overlap_score`: Target-pathway similarity index (0.0–1.0)

- **Performance**:
  - ROC-AUC: **~0.80**
  - Calibrated probability output (`ml_predicted_probability`) provided alongside deterministic scores for multi-dimensional decision support.

---

## 5. Grounded Extractive Synthesis & Hallucination Mitigation

MediScan AI strictly enforces **Grounded Extractive Synthesis**:
1. **Zero Fabricated Citations**: No trial ID (NCT), paper ID (PMID), or patent number may be generated by language models. Every citation links directly to a verifiable public record.
2. **Provenance Tracking**: Every fact extracted is tied to an immutable `EvidenceItem` record containing its raw payload, retrieval timestamp, and source URL.
3. **Negative Evidence Accounting**: Terminated trials, failed efficacy endpoints, and adverse safety signals directly penalize the scores and are prominently featured in the limitations summary.

---

## 6. Mandatory Scientific & Regulatory Disclaimer

> **IMPORTANT SCIENTIFIC DISCLAIMER**
> MediScan AI is an automated computational research intelligence tool designed exclusively to support hypothesis generation, preclinical planning, and literature aggregation for qualified pharmaceutical, biomedical, and academic researchers.
> 
> MediScan AI **does not** provide medical advice, diagnosis, treatment recommendations, or prescribing guidance. Findings generated by this platform do not establish clinical efficacy or safety and must never be used as a substitute for formal preclinical toxicology, controlled clinical trials, or regulatory approval from health authorities (such as the US FDA, EMA, or PMDA).
