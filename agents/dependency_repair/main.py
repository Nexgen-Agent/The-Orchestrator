import argparse
import json
import sys
import os
from agents.dependency_repair.repairer import DependencyRepairer

def main():
    parser = argparse.ArgumentParser(description="Dependency Repair Agent CLI")
    parser.add_argument("project_path", help="Path to the project to analyze/repair")
    parser.add_argument("--action", choices=["analyze", "repair"], default="analyze", help="Action to perform")
    parser.add_argument("--auto-install", action="store_true", help="Attempt to install missing packages (skipped in mock)")
    parser.add_argument("--output", help="Path to save the report JSON")

    args = parser.parse_args()

    if not os.path.exists(args.project_path):
        print(f"Error: Project path {args.project_path} does not exist.")
        sys.exit(1)

    try:
        repairer = DependencyRepairer(args.project_path)

        if args.action == "analyze":
            result = repairer.analyze()
            output_json = json.dumps(result, indent=2)
        else:
            report = repairer.repair(auto_install=args.auto_install)
            output_json = json.dumps(report.model_dump(mode='json'), indent=2)

        if args.output:
            with open(args.output, 'w') as f:
                f.write(output_json)
            print(f"Report saved to {args.output}")
        else:
            print(output_json)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
