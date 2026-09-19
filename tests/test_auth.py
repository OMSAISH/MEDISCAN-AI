import pytest
import uuid
from httpx import AsyncClient, ASGITransport
from backend.app.main import app

@pytest.mark.asyncio
async def test_register_and_login_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        unique_email = f"test_{uuid.uuid4().hex[:8]}@mediscan.ai"
        
        # 1. Register new user
        reg_resp = await ac.post("/api/v1/auth/register", json={
            "email": unique_email,
            "password": "StrongPassword123!",
            "full_name": "Test Researcher",
            "organization": "Pharma R&D Institute"
        })
        assert reg_resp.status_code == 201
        reg_data = reg_resp.json()
        assert reg_data["email"] == unique_email
        assert reg_data["role"] == "RESEARCHER"

        # 2. Duplicate registration should fail
        dup_resp = await ac.post("/api/v1/auth/register", json={
            "email": unique_email,
            "password": "StrongPassword123!",
            "full_name": "Duplicate User"
        })
        assert dup_resp.status_code == 400

        # 3. Login with correct credentials
        login_resp = await ac.post("/api/v1/auth/login", json={
            "email": unique_email,
            "password": "StrongPassword123!"
        })
        assert login_resp.status_code == 200
        login_data = login_resp.json()
        assert "access_token" in login_data
        token = login_data["access_token"]

        # 4. Login with incorrect password
        bad_login = await ac.post("/api/v1/auth/login", json={
            "email": unique_email,
            "password": "WrongPassword!"
        })
        assert bad_login.status_code == 401

        # 5. Access protected /auth/me
        me_resp = await ac.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert me_resp.status_code == 200
        assert me_resp.json()["email"] == unique_email
