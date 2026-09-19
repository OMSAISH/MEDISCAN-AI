# MediScan AI Architecture Specification

## 1. System Overview

MediScan AI is an evidence-driven, multi-agent pharmaceutical research intelligence platform. Its primary objective is to systematically investigate existing approved or experimental compounds for potential drug repurposing opportunities across clinical, scientific literature, patent, and market intelligence domains.

```mermaid
flowchart TD
    Researcher([Pharmaceutical Researcher]) --> Frontend[React 18 + TypeScript + Tailwind CSS]
    Frontend -->|JWT Auth / REST APIs| Gateway[FastAPI Backend Application]
    Frontend <-->|Server-Sent Events (SSE)| EventStream[EventStreamManager]

    subgraph Backend Services
        AuthService[Auth & RBAC Service]
        DrugNorm[Drug Normalizer (PubChem / RxNorm)]
        MasterAgent[Master Orchestrator Agent]
        
        subgraph Parallel Specialized Agents
            ClinicalAgent[Clinical Agent\nClinicalTrials.gov v2]
            LiteratureAgent[Literature Agent\nNCBI PubMed & Europe PMC]
            PatentAgent[Patent Agent\nUSPTO / PatentsView]
            MarketAgent[Market Agent\nOpenFDA & Commercial Signals]
        end

        EvidenceEngine[Evidence Aggregation Engine]
        ScoringEngine[Transparent Scoring Engine]
        ExplainEngine[Explainability Engine]
        ReportEngine[Report Generation Engine\nPDF / HTML / JSON / CSV]
    end

    subgraph Persistence Layer
        DB[(PostgreSQL / SQLite Database)]
        ReportStorage[File Storage /data/reports]
    end

    subgraph Machine Learning Subsystem [/ml]
        MLModel[RandomForestClassifier\n15 Extracted Features]
    end

    Gateway --> AuthService
    Gateway --> MasterAgent
    MasterAgent --> DrugNorm
    MasterAgent --> ParallelAgents
    ParallelAgents --> EvidenceEngine
    EvidenceEngine --> ScoringEngine
    ScoringEngine --> ExplainEngine
    ExplainEngine --> ReportEngine
    ReportEngine --> ReportStorage
    Gateway --> DB
    Gateway --> MLModel
```

---

## 2. Multi-Agent Orchestration

The platform implements a Master Agent that delegates research tasks to four specialized domain agents running concurrently via `asyncio.gather(..., return_exceptions=True)`:

1. **Clinical Agent**: Queries ClinicalTrials.gov API v2 to retrieve interventional and observational studies. Extracts study phases, enrollment cohorts, primary outcome measures, and trial completion statuses.
2. **Literature Agent**: Queries NCBI PubMed E-Utilities and Europe PMC. Analyzes study design classifications (Meta-Analyses, RCTs, Observational studies, Preclinical experiments).
3. **Patent Agent**: Queries PatentsView and Google Patents. Extracts active patent families, granted methods of use, filing dates, and institutional assignees.
4. **Market Agent**: Queries OpenFDA drug labeling and Orange Book exclusivity records. Synthesizes commercial trial sponsorship signals and generic multi-source availability.

### Fault Tolerance & Partial Failure Handling
If an external API experiences rate limiting or network downtime, the Master Agent captures the exception, flags the partial failure, and synthesizes the final report using the remaining successful domains. The final report clearly marks unavailable domains rather than failing the entire analysis.

---

## 3. Database Schema

The persistence layer uses SQLAlchemy 2.0 with async engine support (`asyncpg` for PostgreSQL, `aiosqlite` for SQLite):

- `users`: User accounts with role-based access (`RESEARCHER`, `ADMIN`).
- `research_queries`: Individual drug research runs with query parameters, status, execution timing, and executive synthesis.
- `agent_runs`: Audit records for each specialized agent's execution, record counts, and latencies.
- `discovered_indications`: Clustered therapeutic indications with composite and component evidence scores.
- `evidence_items`: Granular evidence records maintaining source IDs (NCT ID, PMID, Patent Number) and clickable URLs.
- `reports`: Metadata for generated reports in PDF, HTML, JSON, and CSV formats.
- `audit_logs`: Immutable security audit trail tracking user authentication, queries, and exports.
