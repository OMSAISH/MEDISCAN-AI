import time
import asyncio
import statistics
from httpx import AsyncClient, ASGITransport
from backend.app.main import app, init_database

async def benchmark_endpoint(client: AsyncClient, method: str, url: str, headers=None, json=None, iterations=5):
    latencies = []
    for _ in range(iterations):
        start = time.perf_counter()
        if method == "GET":
            resp = await client.get(url, headers=headers)
        elif method == "POST":
            resp = await client.post(url, headers=headers, json=json)
        latency_ms = (time.perf_counter() - start) * 1000
        latencies.append(latency_ms)
    return {
        "mean_ms": round(statistics.mean(latencies), 2),
        "median_ms": round(statistics.median(latencies), 2),
        "min_ms": round(min(latencies), 2),
        "max_ms": round(max(latencies), 2),
    }

async def run_benchmarks():
    print("============================================================")
    print(" MEDISCAN AI - PERFORMANCE BENCHMARK SUITE")
    print("============================================================")
    
    # Initialize DB and seed demo users
    await init_database()

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Health check latency
        health_bench = await benchmark_endpoint(client, "GET", "/api/v1/health", iterations=10)
        print(f"Healthcheck Latency: Mean={health_bench['mean_ms']}ms, Median={health_bench['median_ms']}ms")

        # 2. Drug validation latency
        drug_bench = await benchmark_endpoint(client, "GET", "/api/v1/drugs/validate?name=Metformin", iterations=5)
        print(f"Drug Normalization Latency: Mean={drug_bench['mean_ms']}ms, Median={drug_bench['median_ms']}ms")

        # 3. Authentication login latency
        login_bench = await benchmark_endpoint(
            client, "POST", "/api/v1/auth/login",
            json={"email": "researcher@mediscan.ai", "password": "Researcher12345!"},
            iterations=5
        )
        print(f"Auth / Login (bcrypt verify): Mean={login_bench['mean_ms']}ms, Median={login_bench['median_ms']}ms")

        # Get token
        login_res = await client.post(
            "/api/v1/auth/login",
            json={"email": "researcher@mediscan.ai", "password": "Researcher12345!"}
        )
        token = login_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 4. History retrieval latency
        history_bench = await benchmark_endpoint(client, "GET", "/api/v1/research/history", headers=headers, iterations=5)
        print(f"Research History Query: Mean={history_bench['mean_ms']}ms, Median={history_bench['median_ms']}ms")

    print("============================================================")
    print(" Benchmarking completed successfully.")
    print("============================================================")

if __name__ == "__main__":
    asyncio.run(run_benchmarks())
