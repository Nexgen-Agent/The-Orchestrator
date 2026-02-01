import argparse
import asyncio
import json
import os
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from agents.deployment_preparer.preparer import DeploymentPreparer

async def main():
    parser = argparse.ArgumentParser(description="Deployment Preparation Agent")
    parser.add_argument("path", help="Path to the Python project to prepare")
    parser.add_argument("--output", help="Output JSON file path", default=None)
    parser.add_argument("--indent", help="JSON indentation", type=int, default=2)
    parser.add_argument("--write", help="Write files to project directory", action="store_true")

    args = parser.parse_args()

    if not os.path.exists(args.path):
        print(f"Error: Path {args.path} does not exist.")
        sys.exit(1)

    try:
        print(f"Preparing deployment for: {args.path}...")
        preparer = DeploymentPreparer(args.path)
        report = preparer.prepare()
        output_data = report.model_dump(mode='json')

        if args.write:
            pkg = report.generated_package
            with open(os.path.join(args.path, "Dockerfile"), "w") as f:
                f.write(pkg.dockerfile_content)
            with open(os.path.join(args.path, "requirements.txt"), "w") as f:
                f.write(pkg.requirements_content)
            with open(os.path.join(args.path, "start.sh"), "w") as f:
                f.write(pkg.startup_script_content)
            print(f"Deployment files written to {args.path}")

        if args.output:
            with open(args.output, "w") as f:
                json.dump(output_data, f, indent=args.indent)
            print(f"Deployment report saved to {args.output}")
        else:
            print(json.dumps(output_data, indent=args.indent))

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
