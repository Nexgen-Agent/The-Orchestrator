from typing import Dict, Any
from agents.stress_test.stresser import StressTester, StressTestConfig

async def handle_task(task_packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestration handler for FOG.
    Expects stress test configuration in payload.
    """
    payload = task_packet.get("payload", {})

    try:
        config = StressTestConfig(**payload)
        stresser = StressTester()
        report = await stresser.run_stress_test(config)

        return {
            "status": "success",
            "result": report.model_dump(mode='json')
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
