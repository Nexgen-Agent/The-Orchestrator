import pytest
import asyncio
from agents.stress_test.stresser import StressTester
from agents.stress_test.models import StressTestConfig

@pytest.mark.asyncio
async def test_run_stress_test_basic():
    stresser = StressTester()
    config = StressTestConfig(num_tasks=5, concurrency=2)
    report = await stresser.run_stress_test(config)

    assert report.config.num_tasks == 5
    assert report.result.total_tasks == 5
    assert report.result.successful_tasks == 5
    assert report.result.average_latency_ms > 0
    assert report.stability_rating == "Stable"

@pytest.mark.asyncio
async def test_stress_test_bottleneck_detection():
    stresser = StressTester()
    # High payload size will increase latency in mock simulation
    config = StressTestConfig(num_tasks=10, concurrency=5, payload_size_kb=60)
    report = await stresser.run_stress_test(config)

    # Payload of 60KB * 0.01 = 0.6s = 600ms sleep.
    # This should trigger the > 500ms bottleneck.
    assert "High tail latency (P95 > 500ms)" in report.bottlenecks
    assert report.stability_rating == "Degraded"

@pytest.mark.asyncio
async def test_handler_integration():
    from agents.stress_test.handler import handle_task

    task = {
        "payload": {
            "num_tasks": 3,
            "concurrency": 1
        }
    }

    response = await handle_task(task)
    assert response["status"] == "success"
    assert response["result"]["result"]["total_tasks"] == 3
