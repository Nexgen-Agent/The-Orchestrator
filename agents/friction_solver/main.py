import asyncio
import json
import os
import argparse
import sys
from agents.friction_solver.solver import FrictionSolver
from agents.friction_solver.models import FrictionSolverConfig

async def monitor_loop(interval: int = 10):
    """
    Background loop monitoring storage/state.json for failed tasks.
    """
    state_path = "storage/state.json"
    solver = FrictionSolver()
    solved_tasks = set()

    print(f"Starting background friction monitor on {state_path}...")

    while True:
        if os.path.exists(state_path):
            try:
                with open(state_path, "r") as f:
                    state = json.load(f)

                tasks = state.get("tasks", {})
                for task_id, task in tasks.items():
                    if task.get("status") == "failed" and task_id not in solved_tasks:
                        error_msg = str(task.get("result", {}).get("error", "Unknown error"))
                        project_path = task.get("payload", {}).get("project_path")

                        if project_path:
                            print(f"Detected failure in task {task_id}. Attempting to solve friction...")
                            config = FrictionSolverConfig(
                                project_path=project_path,
                                error_message=error_msg
                            )
                            report = await solver.solve(config)
                            print(f"Friction Report for {task_id}: {report.model_dump_json(indent=2)}")
                            solved_tasks.add(task_id)
            except Exception as e:
                print(f"Monitor error: {e}")

        await asyncio.sleep(interval)

async def main():
    parser = argparse.ArgumentParser(description="Friction Solver Agent")
    parser.add_argument("--project", help="Path to the project")
    parser.add_argument("--error", help="Error message to solve")
    parser.add_argument("--monitor", action="store_true", help="Run in background monitor mode")

    args = parser.parse_args()

    if args.monitor:
        await monitor_loop()
    elif args.project and args.error:
        solver = FrictionSolver()
        config = FrictionSolverConfig(project_path=args.project, error_message=args.error)
        report = await solver.solve(config)
        print(json.dumps(report.model_dump(mode='json'), indent=2))
    else:
        parser.print_help()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
