from typing import Dict, Any
from agents.sandbox_simulation.simulator import SandboxSimulator, SimulationConfig

async def handle_task(task_packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestration handler for FOG.
    Expects simulation configuration in payload.
    """
    payload = task_packet.get("payload", {})

    try:
        config = SimulationConfig(**payload)
        simulator = SandboxSimulator()
        report = simulator.simulate(config)

        return {
            "status": "success",
            "result": report.model_dump(mode='json')
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}
