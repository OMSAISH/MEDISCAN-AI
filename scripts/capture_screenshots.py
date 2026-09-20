import asyncio
import os
import subprocess
from backend.app.database.session import AsyncSessionLocal
from backend.app.models.user import User
from backend.app.auth.jwt import create_access_token
from sqlalchemy import select

CHROME_BIN = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT_DIR = "/Users/omsaishdhokchaule/.gemini/antigravity/brain/aeea39ca-d2bf-42b0-b6dc-682fe1ff841c/scratch/steps"

async def get_token():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(User).where(User.email == "researcher@mediscan.ai"))
        user = res.scalar_one()
        return create_access_token({"sub": user.id, "email": user.email, "role": user.role.value})

def capture_page(name, url, window_size="1280,850", budget="4000"):
    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, f"{name}.png")
    cmd = [
        CHROME_BIN,
        "--headless=new",
        "--disable-gpu",
        f"--window-size={window_size}",
        f"--virtual-time-budget={budget}",
        f"--screenshot={out_path}",
        url
    ]
    print(f"Capturing {name} from {url}...")
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Saved {out_path} ({os.path.getsize(out_path)} bytes)")
    return out_path

async def main():
    token = await get_token()
    query_id = "05272b5e-9e1e-468f-91a4-63801f8f4565"

    steps = [
        ("step1_login", "http://localhost:5173/?view=login", "1280,850", "2000"),
        ("step2_search", f"http://localhost:5173/?token={token}&view=new-analysis&drug=Metformin", "1280,850", "3000"),
        ("step3_processing", f"http://localhost:5173/?token={token}&view=live-analysis&id={query_id}", "1280,850", "3000"),
        ("step4_results", f"http://localhost:5173/?token={token}&view=results&id={query_id}", "1280,850", "4000"),
        ("step5_evidence", f"http://localhost:5173/?token={token}&view=results&id={query_id}&modal=evidence", "1280,850", "4500"),
        ("step6_report", f"http://localhost:5173/?token={token}&view=results&id={query_id}&modal=report", "1280,850", "4000"),
        ("step7_dashboard", f"http://localhost:5173/?token={token}&view=dashboard", "1280,850", "3000")
    ]

    for name, url, win, bud in steps:
        capture_page(name, url, win, bud)

    print("All 7 screenshots captured successfully!")

if __name__ == "__main__":
    asyncio.run(main())
