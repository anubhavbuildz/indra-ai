"""PERFORMANCE-001: 100 in-process health requests, 8 workers, p95 <500ms, total <10s."""

import json
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


def test_health_concurrent_latency(client):
    def request(_):
        start = time.perf_counter()
        assert client.get("/health").status_code == 200
        return (time.perf_counter() - start) * 1000

    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=8) as pool:
        durations = sorted(pool.map(request, range(100)))
    elapsed = time.perf_counter() - start
    output = {
        "requests": 100,
        "workers": 8,
        "p95_ms": durations[94],
        "total_seconds": elapsed,
        "transport": "in-process ASGI TestClient",
        "scope": "health endpoint only; excludes real network, cloud, inference and retrieval",
    }
    path = Path("design/qa/evidence/performance.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, indent=2))
    assert durations[94] < 500
    assert elapsed < 10
