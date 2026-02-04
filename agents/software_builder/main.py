import argparse
import asyncio
import json
import os
from agents.software_builder.builder import SoftwareBuilder
from agents.software_builder.models import BuildRequest

async def main():
    parser = argparse.ArgumentParser(description="Software Builder CLI")
    parser.add_argument("project_path", help="Path to the project to build")
    parser.add_argument("--iterations", type=int, default=5, help="Max improvement iterations per module")
    parser.add_argument("--modules", help="Comma-separated list of target modules")
    parser.add_argument("--output", help="Path to save build report")

    args = parser.parse_args()

    if not os.path.exists(args.project_path):
        print(f"Error: Path {args.project_path} does not exist.")
        return

    target_modules = args.modules.split(",") if args.modules else None

    request = BuildRequest(
        project_path=args.project_path,
        max_iterations=args.iterations,
        target_modules=target_modules
    )

    builder = SoftwareBuilder(args.project_path)
    print(f"Starting build for {args.project_path}...")
    report = await builder.run_build(request)

    output_json = json.dumps(report.model_dump(mode='json'), indent=2)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(output_json)
        print(f"Build report saved to {args.output}")
    else:
        print(output_json)

if __name__ == "__main__":
    asyncio.run(main())
