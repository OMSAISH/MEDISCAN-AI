import pytest
import uuid
import asyncio
from httpx import AsyncClient, ASGITransport
from backend.app.main import app

@pytest.mark.asyncio
async def test_full_analysis_workflow_e2e():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        user_email = f"pharma_researcher_{uuid.uuid4().hex[:6]}@mediscan.ai"
        
        # 1. Register
        reg_resp = await ac.post("/api/v1/auth/register", json={
            "email": user_email,
            "password": "ResearcherPassword123!",
            "full_name": "Dr. Sarah Lin",
            "organization": "Stanford Oncology Therapeutics"
        })
        assert reg_resp.status_code == 201

        # 2. Login
        login_resp = await ac.post("/api/v1/auth/login", json={
            "email": user_email,
            "password": "ResearcherPassword123!"
        })
        assert login_resp.status_code == 200
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 3. Start analysis for Metformin
        analysis_resp = await ac.post("/api/v1/research", headers=headers, json={
            "drug_name": "Metformin",
            "research_question": "Investigate oncology and neuroprotective indications beyond diabetes",
            "enable_clinical": True,
            "enable_literature": True,
            "enable_patent": True,
            "enable_market": True
        })
        assert analysis_resp.status_code == 202
        query_data = analysis_resp.json()
        query_id = query_data["id"]

        # 4. Wait briefly for background execution
        for _ in range(20):
            await asyncio.sleep(0.5)
            status_resp = await ac.get(f"/api/v1/research/{query_id}", headers=headers)
            assert status_resp.status_code == 200
            current_status = status_resp.json()["status"]
            if current_status in ["COMPLETED", "PARTIAL_FAILURE"]:
                break

        res_data = status_resp.json()
        assert res_data["status"] in ["COMPLETED", "PARTIAL_FAILURE"]
        assert len(res_data["indications"]) > 0
        assert res_data["executive_summary"] is not None
        assert "MediScan AI" in res_data["synthesis_disclaimer"]

        first_ind = res_data["indications"][0]
        assert first_ind["evidence_score"] > 0
        assert first_ind["evidence_strength"] in ["Strong", "Moderate", "Limited", "Insufficient"]
        assert len(first_ind["positive_factors"]) > 0

        # 5. Fetch evidence details
        ev_resp = await ac.get(f"/api/v1/evidence/{first_ind['id']}", headers=headers)
        assert ev_resp.status_code == 200
        ev_data = ev_resp.json()
        assert ev_data["indication_id"] == first_ind["id"]
        # Check source links presence
        all_items = ev_data["clinical_trials"] + ev_data["literature"] + ev_data["patents"]
        assert len(all_items) > 0
        for item in all_items:
            assert item["source_url"].startswith("http")

        # 6. Generate PDF report
        rep_resp = await ac.post(f"/api/v1/reports/{query_id}/generate", headers=headers, json={
            "report_format": "PDF"
        })
        assert rep_resp.status_code == 200
        rep_data = rep_resp.json()
        assert rep_data["report_format"] == "PDF"
        assert rep_data["file_size_bytes"] > 0

        # 7. Check research history
        hist_resp = await ac.get("/api/v1/research/history", headers=headers)
        assert hist_resp.status_code == 200
        history = hist_resp.json()
        assert len(history) >= 1
        assert history[0]["id"] == query_id
