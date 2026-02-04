import argparse
import asyncio
import json
import os
from agents.debugger.debugger import Debugger
from agents.debugger.models import DebugRequest

async def main():
    parser = argparse.ArgumentParser(description="Debugger Agent CLI")
    parser.add_argument("project_path", help="Path to the project to debug")
    parser.add_argument("--auto-fix", action="store_true", help="Apply fixes automatically")
    parser.add_argument("--validation-rounds", type=int, default=3)
    parser.add_argument("--simulation-id", help="ID of a previous simulation report")
    parser.add_argument("--output", help="Path to save debug report")

    args = parser.parse_args()

    if not os.path.exists(args.project_path):
        print(f"Error: Path {args.project_path} does not exist.")
        return

    request = DebugRequest(
        project_path=args.project_path,
        auto_fix=args.auto_fix,
        validation_rounds=args.validation_rounds,
        simulation_report_id=args.simulation_id
    )

    debugger = Debugger(args.project_path)
    print(f"Analyzing {args.project_path}...")
    report = await debugger.run_debug(request)

    output_json = json.dumps(report.model_dump(mode='json'), indent=2)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(output_json)
        print(f"Debug report saved to {args.output}")
    else:
        print(output_json)

if __name__ == "__main__":
    asyncio.run(main())
