import argparse
import json
import sys
import os
from agents.sandbox_simulation.simulator import SandboxSimulator, SimulationConfig

def main():
    parser = argparse.ArgumentParser(description="Sandbox Simulation Agent CLI")
    parser.add_argument("project_path", help="Path to the project")
    parser.add_argument("task", help="Description of the task to simulate")
    parser.add_argument("--output", help="Save report to JSON file")

    args = parser.parse_args()

    if not os.path.exists(args.project_path):
        print(f"Error: Project path {args.project_path} not found.")
        sys.exit(1)

    config = SimulationConfig(
        project_path=args.project_path,
        task_description=args.task
    )

    print(f"Starting simulation for: {args.task}...")
    simulator = SandboxSimulator()
    report = simulator.simulate(config)

    output_json = json.dumps(report.model_dump(mode='json'), indent=2)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(output_json)
        print(f"Simulation report saved to {args.output}")
    else:
        print("\n--- Simulation Report ---")
        print(f"Verdict: {report.verdict}")
        print(f"Summary: {report.summary}")

        if report.result.conflicts:
            print("\nConflicts Detected:")
            for c in report.result.conflicts:
                print(f" - {c}")

        if report.result.side_effects:
            print("\nSide Effects Detected:")
            for s in report.result.side_effects:
                print(f" - {s}")

        print("\nSafety Checks:")
        for check in report.result.safety_checks:
            status = "PASSED" if check.passed else "FAILED"
            print(f" - [{status}] {check.check_name}: {check.details}")

if __name__ == "__main__":
    main()
