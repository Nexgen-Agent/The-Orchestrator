import asyncio
import os
import shutil
from fog.models.task import TaskPacket, TaskType
from fog.core.engine import orchestration_engine
from fog.core.connector import MockAgentConnector, agent_registry
from fog.core.state import state_store

async def run_workflow():
    # 1. Setup Environment
    project_path = "examples/large_project_demo"
    if os.path.exists(project_path):
        shutil.rmtree(project_path)
    os.makedirs(project_path, exist_ok=True)

    with open(os.path.join(project_path, "base.py"), "w") as f:
        f.write("def core(): return True")
    with open(os.path.join(project_path, "app.py"), "w") as f:
        f.write("import base\ndef run():\n    eval('print(\"unsafe\")')\n    return base.core()")

    print(f"Created demo project at {project_path}")

    # 2. Register Agents
    agent_registry.register_agent(MockAgentConnector("software_builder", "http://localhost:8001"))
    agent_registry.register_agent(MockAgentConnector("debugger", "http://localhost:8002"))

    # 3. Start Engine
    await orchestration_engine.start(num_workers=2)

    # 4. Sequential Workflow: Build -> Debug
    print("\n--- Submitting Build Task ---")
    build_task = TaskPacket(
        system_name="software_builder",
        module_name="all",
        task_type=TaskType.ANALYSIS,
        payload={"project_path": project_path, "max_iterations": 3}
    )
    await orchestration_engine.submit_task(build_task)

    # Wait for build completion
    while True:
        status = state_store.get_task(build_task.task_id).get("status")
        if status in ["completed", "failed"]:
            print(f"Build Task finished with status: {status}")
            break
        await asyncio.sleep(1)

    print("\n--- Submitting Debug Task ---")
    debug_task = TaskPacket(
        system_name="debugger",
        module_name="all",
        task_type=TaskType.ANALYSIS,
        payload={"project_path": project_path, "auto_fix": True}
    )
    await orchestration_engine.submit_task(debug_task)

    # Wait for debug completion
    while True:
        status = state_store.get_task(debug_task.task_id).get("status")
        if status in ["completed", "failed"]:
            result = state_store.get_task(debug_task.task_id).get("result")
            print(f"Debug Task finished with status: {status}")
            print(f"Summary: {result.get('summary')}")
            break
        await asyncio.sleep(1)

    # 5. Stop Engine
    await orchestration_engine.stop()
    print("\nWorkflow demonstration complete.")

if __name__ == "__main__":
    # Ensure PYTHONPATH is set
    import sys
    sys.path.append(os.getcwd())
    asyncio.run(run_workflow())
