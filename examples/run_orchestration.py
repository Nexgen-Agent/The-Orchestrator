import asyncio
import httpx
import json
import time
import os
from multiprocessing import Process

def start_server():
    import uvicorn
    from fog.api.main import app
    uvicorn.run(app, host="127.0.0.1", port=8001)

async def run_demo():
    # Wait for server to start
    await asyncio.sleep(2)

    async with httpx.AsyncClient() as client:
        # 1. Register a mock agent
        print("--- Registering Agent ---")
        resp = await client.post("http://127.0.0.1:8001/register-agent", json={
            "name": "CoderAgent",
            "endpoint": "http://mock-coder:5000",
            "handler_type": "mock"
        })
        print(resp.json())

        # 2. Submit project
        print("\n--- Submitting Project ---")
        # Ensure we have a dummy project to backup
        os.makedirs("dummy_project", exist_ok=True)
        with open("dummy_project/hello.py", "w") as f:
            f.write("print('hello world')")

        resp = await client.post("http://127.0.0.1:8001/submit-project", json={
            "project_path": "dummy_project",
            "description": "My dummy project"
        })
        project_data = resp.json()
        print(project_data)
        initial_backup_id = project_data["backup_id"]

        # 3. Submit a modification task (should trigger auto-backup)
        print("\n--- Submitting Modification Task ---")
        resp = await client.post("http://127.0.0.1:8001/submit-task", json={
            "system_name": "CoderAgent",
            "module_name": "hello",
            "task_type": "modification",
            "payload": {"project_path": "dummy_project", "action": "add_comment"}
        })
        task_data = resp.json()
        print(task_data)
        task_id = task_data["task_id"]

        # 4. Wait and check status
        print("\n--- Checking Task Status ---")
        for _ in range(5):
            await asyncio.sleep(1)
            resp = await client.get(f"http://127.0.0.1:8001/task-status/{task_id}")
            status_data = resp.json()
            print(f"Task {task_id} status: {status_data['status']}")
            if status_data['status'] == 'completed':
                print(f"Result: {status_data['result']}")
                break

        # 5. Get system state
        print("\n--- System State ---")
        resp = await client.get("http://127.0.0.1:8001/system-state")
        print(json.dumps(resp.json(), indent=2))

        # 6. Rollback
        print("\n--- Rolling back to initial state ---")
        resp = await client.post(f"http://127.0.0.1:8001/rollback/{initial_backup_id}")
        print(resp.json())

if __name__ == "__main__":
    p = Process(target=start_server)
    p.start()
    try:
        asyncio.run(run_demo())
    finally:
        p.terminate()
        p.join()
