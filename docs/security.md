# MediScan AI Security Architecture & Governance Specification

MediScan AI is designed to meet rigorous enterprise pharmaceutical security, confidentiality, and data integrity requirements.

---

## 1. Threat Model & Security Posture

In pharmaceutical and biomedical environments, research queries regarding drug repositioning constitute sensitive intellectual property and proprietary trade intelligence. MediScan AI addresses the following primary threat vectors:

1. **Confidentiality of Research Queries**: Ensuring proprietary drug investigations and therapeutic hypotheses cannot be intercepted or accessed by unauthorized tenants.
2. **Data Integrity & Traceability**: Guaranteeing that clinical trial numbers, PubMed IDs, and patent citations are authentic and unmanipulated.
3. **Accountability & Non-Repudiation**: Enforcing tamper-evident audit logging for all authentication attempts, data queries, and report exports.

---

## 2. Authentication & Credential Security

### 2.1 Native Bcrypt Password Hashing
Password hashing is implemented using native `bcrypt` with salt rounds configured to balance cryptographic resistance against timing attacks:

- **Salt Rounds**: 12 iterations.
- **72-Byte Boundary Handling**: The standard bcrypt specification truncates passwords at 72 bytes. MediScan AI explicitly handles UTF-8 byte conversion and length boundaries to prevent wrap-around collision vulnerabilities.
- **Timing Protection**: Password verification uses constant-time byte comparisons (`bcrypt.checkpw`) to prevent timing side-channel attacks.

### 2.2 Stateless JWT Token Architecture
Session state is managed via cryptographically signed JSON Web Tokens (JWT):

- **Algorithm**: `HMAC-SHA256` (`HS256`)
- **Key Storage**: Secure server-side `SECRET_KEY` loaded via environment variables; never hardcoded or committed to version control.
- **Token Expiry**: Default access token lifespan is 60 minutes (`ACCESS_TOKEN_EXPIRE_MINUTES=60`).
- **Payload Schema**:
  ```json
  {
    "sub": "user-uuid",
    "email": "researcher@mediscan.ai",
    "role": "RESEARCHER",
    "exp": 1758330000,
    "iat": 1758326400
  }
  ```

---

## 3. Role-Based Access Control (RBAC)

MediScan AI enforces strict principle-of-least-privilege access controls via FastAPI dependency injection:

| Role | Permissions |
|------|-------------|
| `RESEARCHER` | - Search and normalize compounds<br>- Launch multi-agent repurposing analyses<br>- Stream real-time agent execution events<br>- View own research query results and evidence details<br>- Export reports in PDF, HTML, JSON, and CSV |
| `ADMIN` | - All `RESEARCHER` privileges<br>- View all organization research queries<br>- Access immutable security audit logs (`/api/v1/admin/audit-logs`)<br>- Inspect platform performance and latency metrics (`/api/v1/admin/metrics`)<br>- Manage and deactivate user accounts |

### Enforcement Pattern
```python
@router.get("/admin/audit-logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    ...
```

---

## 4. Input Validation & Injection Defenses

### 4.1 SQL Injection Prevention
The persistence layer utilizes **SQLAlchemy 2.0 ORM** with asynchronous drivers (`asyncpg` for PostgreSQL, `aiosqlite` for SQLite).
- Zero raw string concatenation or interpolation in SQL queries.
- All database operations use strictly parameterized statements and ORM filter expressions.

### 4.2 Cross-Site Scripting (XSS) & Content Security Policy
- **React Frontend**: Automatic JSX context-aware escaping prevents inline HTML/JavaScript injection.
- **API Payloads**: Strictly validated through **Pydantic v2** models with regex constraints and type enforcement.
- **CORS**: Cross-Origin Resource Sharing is locked down to explicit whitelist domains defined via `CORS_ORIGINS`.

---

## 5. Security Audit Logging

MediScan AI records an immutable audit trail in the `audit_logs` table for all security-relevant and research events:

```
+-----------------------------------------------------------------------------------+
|                                 AUDIT LOG RECORD                                  |
+-------------+-------------+----------------------+--------------------+-----------+
| timestamp   | actor_user  | action               | target_resource    | client_ip |
+-------------+-------------+----------------------+--------------------+-----------+
| 2026-09-20  | usr-1234    | AUTH_LOGIN_SUCCESS   | /api/v1/auth/login | 10.0.0.1  |
| 2026-09-20  | usr-1234    | RESEARCH_QUERY_START | query-7c9e6679     | 10.0.0.1  |
| 2026-09-20  | usr-1234    | REPORT_EXPORT_PDF    | rep-998877         | 10.0.0.1  |
+-------------+-------------+----------------------+--------------------+-----------+
```

---

## 6. External API Integration Security

MediScan AI interacts with public scientific repositories (ClinicalTrials.gov, NCBI PubMed, PatentsView, OpenFDA).
- **HTTP Client**: Asynchronous requests managed via `httpx.AsyncClient` with explicit timeouts (10s connect, 30s read).
- **Rate Limiting & Retries**: Built-in exponential backoff with jitter avoids triggering external IP rate limits.
- **Fail-Safe Degradation**: If an external service returns an HTTP 429 (Too Many Requests) or 5xx, the Master Agent isolates the failure and marks the domain as unavailable without crashing or leaking stack traces.
