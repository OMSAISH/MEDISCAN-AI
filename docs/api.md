# MediScan AI REST API Specification

MediScan AI exposes a high-performance, asynchronous REST API built with FastAPI and documented via OpenAPI (Swagger) specifications.

- **Base URL**: `http://localhost:8000/api/v1`
- **Interactive Documentation**: `http://localhost:8000/docs`
- **OpenAPI JSON Schema**: `http://localhost:8000/openapi.json`

---

## 1. Authentication & Security Headers

All protected endpoints require an HTTP `Authorization` header containing a valid Bearer JWT:

```http
Authorization: Bearer <jwt_access_token>
```

### Standard Error Responses

| Status Code | Description | Example Payload |
|-------------|-------------|-----------------|
| `400 Bad Request` | Invalid input or validation failure | `{"detail": "User already exists with this email"}` |
| `401 Unauthorized` | Missing, expired, or invalid token | `{"detail": "Could not validate credentials"}` |
| `403 Forbidden` | Insufficient role permissions | `{"detail": "Operation requires ADMIN role"}` |
| `404 Not Found` | Resource not found | `{"detail": "Research query not found"}` |
| `422 Unprocessable Entity` | Pydantic schema validation error | `{"detail": [{"loc": ["body", "email"], "msg": "value is not a valid email address"}]}` |
| `500 Internal Server Error` | Unhandled server exception | `{"detail": "Internal processing error occurred"}` |

---

## 2. Authentication Endpoints (`/api/v1/auth`)

### `POST /api/v1/auth/register`
Registers a new researcher or administrator account.

- **Access**: Public
- **Request Body**:
```json
{
  "email": "dr.smith@pharma-research.org",
  "password": "SecurePassword123!",
  "full_name": "Dr. Eleanor Smith",
  "organization": "Oncology Research Institute",
  "role": "RESEARCHER"
}
```
- **Response** (`201 Created`):
```json
{
  "id": "e4b3c2a1-0000-0000-0000-000000000001",
  "email": "dr.smith@pharma-research.org",
  "full_name": "Dr. Eleanor Smith",
  "organization": "Oncology Research Institute",
  "role": "RESEARCHER",
  "is_active": true,
  "created_at": "2026-09-20T00:00:00Z"
}
```

### `POST /api/v1/auth/login`
Authenticates a user and returns a JSON Web Token (JWT).

- **Access**: Public
- **Request Body**:
```json
{
  "email": "dr.smith@pharma-research.org",
  "password": "SecurePassword123!"
}
```
- **Response** (`200 OK`):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": "e4b3c2a1-0000-0000-0000-000000000001",
    "email": "dr.smith@pharma-research.org",
    "full_name": "Dr. Eleanor Smith",
    "role": "RESEARCHER"
  }
}
```

### `GET /api/v1/auth/me`
Retrieves the profile of the currently authenticated user.

- **Access**: Authenticated (`RESEARCHER` or `ADMIN`)
- **Response** (`200 OK`):
```json
{
  "id": "e4b3c2a1-0000-0000-0000-000000000001",
  "email": "dr.smith@pharma-research.org",
  "full_name": "Dr. Eleanor Smith",
  "organization": "Oncology Research Institute",
  "role": "RESEARCHER",
  "is_active": true,
  "created_at": "2026-09-20T00:00:00Z"
}
```

---

## 3. Drug Discovery & Normalization (`/api/v1/drugs`)

### `GET /api/v1/drugs/search?q={query}`
Autocompletes and searches standard drug names against PubChem and local curated dictionary.

- **Access**: Authenticated
- **Query Parameters**:
  - `q` (string, required): Drug name prefix or keyword (e.g., `metf`, `imatinib`).
- **Response** (`200 OK`):
```json
[
  {
    "name": "Metformin",
    "synonyms": ["Glucophage", "Fortamet", "Glumetza"],
    "pubchem_cid": "4091",
    "cas_number": "657-24-9",
    "molecular_formula": "C4H11N5",
    "smiles": "CN(C)C(=N)NC(=N)N",
    "primary_class": "Biguanide Antidiabetic"
  }
]
```

### `GET /api/v1/drugs/normalize?name={name}`
Normalizes a trade or generic name to standard chemical identifiers and known approved indications.

- **Access**: Authenticated
- **Query Parameters**:
  - `name` (string, required): Compound or trade name (e.g., `Glucophage`).
- **Response** (`200 OK`):
```json
{
  "query_name": "Glucophage",
  "normalized_name": "Metformin",
  "pubchem_cid": "4091",
  "smiles": "CN(C)C(=N)NC(=N)N",
  "approved_indications": ["Type 2 Diabetes Mellitus"],
  "mechanism_of_action": "AMPK activator; inhibits hepatic gluconeogenesis"
}
```

---

## 4. Research & Multi-Agent Orchestration (`/api/v1/research`)

### `POST /api/v1/research/analyze`
Submits a compound for full multi-agent repurposing analysis. Launches the Master Agent and spawns concurrent domain agents.

- **Access**: Authenticated
- **Request Body**:
```json
{
  "drug_name": "Metformin",
  "target_indication": null,
  "include_preclinical": true,
  "min_clinical_phase": "PHASE_1"
}
```
- **Response** (`202 Accepted`):
```json
{
  "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "drug_name": "Metformin",
  "status": "PROCESSING",
  "target_indication": null,
  "created_at": "2026-09-20T00:00:00Z"
}
```

### `GET /api/v1/research/{query_id}`
Fetches the full results and synthesized evidence for a completed or in-progress analysis.

- **Access**: Authenticated
- **Path Parameters**:
  - `query_id` (UUID, required): The ID of the research query.
- **Response** (`200 OK`):
```json
{
  "id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "drug_name": "Metformin",
  "status": "COMPLETED",
  "target_indication": null,
  "execution_time_ms": 4250,
  "executive_summary": "High repositioning signal detected for Oncology indications (Breast & Colorectal Cancer)...",
  "discovered_indications": [
    {
      "id": "ind-001",
      "indication_name": "Colorectal Cancer",
      "disease_mesh_id": "D015179",
      "composite_score": 78.4,
      "clinical_score": 82.5,
      "patent_score": 65.0,
      "literature_score": 88.0,
      "market_score": 72.0,
      "evidence_tier": "HIGH_CONFIDENCE",
      "key_findings": [
        "Multiple completed Phase 2 trials demonstrated reduced polyp recurrence.",
        "Method-of-use patent filings active across North America and Europe."
      ],
      "ml_predicted_probability": 0.824,
      "evidence_count": 14
    }
  ],
  "agent_runs": [
    {"agent_name": "ClinicalAgent", "status": "COMPLETED", "records_found": 12, "execution_time_ms": 1120},
    {"agent_name": "LiteratureAgent", "status": "COMPLETED", "records_found": 25, "execution_time_ms": 1340},
    {"agent_name": "PatentAgent", "status": "COMPLETED", "records_found": 8, "execution_time_ms": 980},
    {"agent_name": "MarketAgent", "status": "COMPLETED", "records_found": 6, "execution_time_ms": 610}
  ],
  "created_at": "2026-09-20T00:00:00Z",
  "completed_at": "2026-09-20T00:00:04Z"
}
```

### `GET /api/v1/research/{query_id}/stream`
Real-time Server-Sent Events (SSE) stream broadcasting live agent task execution and intermediate discovery events.

- **Access**: Authenticated (Token supplied via query param `?token=` or header)
- **Response Stream Event Format**:
```http
event: agent_start
data: {"agent": "ClinicalAgent", "message": "Initiating search on ClinicalTrials.gov v2..."}

event: agent_progress
data: {"agent": "ClinicalAgent", "progress": 50, "records_found": 8}

event: agent_complete
data: {"agent": "ClinicalAgent", "status": "COMPLETED", "records_found": 14, "duration_ms": 1120}

event: analysis_complete
data: {"query_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7", "status": "COMPLETED"}
```

### `GET /api/v1/research/history`
Lists past research queries executed by the user or organization.

- **Access**: Authenticated
- **Query Parameters**:
  - `limit` (integer, default: 20)
  - `offset` (integer, default: 0)
- **Response** (`200 OK`): Paginated array of research query summaries.

---

## 5. Evidence Engine (`/api/v1/evidence`)

### `GET /api/v1/evidence/indication/{indication_id}`
Retrieves all itemized evidence supporting a specific discovered indication.

- **Access**: Authenticated
- **Path Parameters**:
  - `indication_id` (UUID, required): The ID of the discovered indication.
- **Response** (`200 OK`):
```json
[
  {
    "id": "ev-001",
    "source_type": "CLINICAL_TRIAL",
    "source_id": "NCT01101438",
    "title": "Metformin in Patients With Early Breast Cancer",
    "url": "https://clinicaltrials.gov/study/NCT01101438",
    "phase": "Phase 2",
    "status": "COMPLETED",
    "enrollment": 120,
    "confidence_weight": 0.85,
    "extracted_facts": {
      "primary_outcomes": ["Ki-67 expression change"],
      "adverse_events_observed": false
    },
    "provenance_timestamp": "2026-09-20T00:00:00Z"
  },
  {
    "id": "ev-002",
    "source_type": "LITERATURE",
    "source_id": "PMID:29358241",
    "title": "AMPK activation by metformin suppresses colorectal cancer stem cells",
    "url": "https://pubmed.ncbi.nlm.nih.gov/29358241/",
    "confidence_weight": 0.78,
    "extracted_facts": {
      "study_type": "Preclinical in-vivo",
      "journal": "Cancer Research",
      "impact_factor": 11.2
    }
  }
]
```

---

## 6. Report Generation (`/api/v1/reports`)

### `POST /api/v1/reports/generate`
Compiles an evidence-backed intelligence dossier in PDF, HTML, JSON, or CSV.

- **Access**: Authenticated
- **Request Body**:
```json
{
  "query_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "format": "PDF"
}
```
- **Response** (`201 Created`):
```json
{
  "id": "rep-998877",
  "query_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "format": "PDF",
  "file_url": "/api/v1/reports/rep-998877/download",
  "generated_at": "2026-09-20T00:00:05Z"
}
```

### `GET /api/v1/reports/{report_id}/download`
Downloads the compiled binary report file.

- **Access**: Authenticated
- **Returns**: File attachment (`application/pdf`, `text/html`, `application/json`, or `text/csv`).

---

## 7. Administrative & Audit (`/api/v1/admin`)

### `GET /api/v1/admin/audit-logs`
Queries security and research audit logs.

- **Access**: `ADMIN` only
- **Query Parameters**:
  - `action` (optional string): Filter by action (e.g., `USER_LOGIN`, `RESEARCH_QUERY`).
  - `limit` (default: 50)
- **Response** (`200 OK`): Paginated audit records with client IP, timestamp, user ID, and resource IDs.

### `GET /api/v1/admin/metrics`
Returns system usage statistics, active users, total queries, and agent latency distributions.

---

## 8. Health & Observability (`/api/v1/health`)

### `GET /api/v1/health`
Returns liveness and readiness status of backend services and database connection.

- **Access**: Public
- **Response** (`200 OK`):
```json
{
  "status": "HEALTHY",
  "version": "1.0.0",
  "database": "CONNECTED",
  "timestamp": "2026-09-20T00:00:00Z"
}
```
