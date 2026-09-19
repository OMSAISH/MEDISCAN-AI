import pytest
from httpx import AsyncClient, ASGITransport
from backend.app.main import app
from backend.app.services.drug_normalizer import drug_normalizer

@pytest.mark.asyncio
async def test_drug_normalization_service():
    # Test canonical resolution for brand name "Glucophage"
    res = await drug_normalizer.normalize("Glucophage")
    assert res["is_valid"] is True
    assert res["normalized_name"] == "Metformin"
    assert "Type 2 Diabetes Mellitus" in res["known_indications"]
    assert res["canonical_smiles"] is not None

    # Test resolution for "Aspirin"
    res_asp = await drug_normalizer.normalize("Aspirin")
    assert res_asp["is_valid"] is True
    assert res_asp["normalized_name"] == "Aspirin"

@pytest.mark.asyncio
async def test_drug_api_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/v1/drugs/validate?name=Metformin")
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_valid"] is True
        assert data["normalized_name"] == "Metformin"

        # Search autocomplete
        search_resp = await ac.get("/api/v1/drugs/search?q=met")
        assert search_resp.status_code == 200
        assert len(search_resp.json()) > 0
