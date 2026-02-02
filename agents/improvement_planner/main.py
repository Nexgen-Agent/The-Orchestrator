import argparse
import json
import sys
import os
from agents.improvement_planner.planner import ImprovementPlanner

def main():
    parser = argparse.ArgumentParser(description="Agent Improvement Planner CLI")
    parser.add_argument("--report", required=True, help="Path to optimization report JSON")
    parser.add_argument("--output", help="Path to save improvement plan JSON")

    args = parser.parse_args()

    if not os.path.exists(args.report):
        print(f"Error: Report file {args.report} not found.")
        sys.exit(1)

    try:
        with open(args.report, 'r') as f:
            report_data = json.load(f)

        planner = ImprovementPlanner()
        plan = planner.generate_plan(report_data)

        output_json = json.dumps(plan.model_dump(mode='json'), indent=2)

        if args.output:
            with open(args.output, 'w') as f:
                f.write(output_json)
            print(f"Improvement plan saved to {args.output}")
        else:
            print("\n--- Agent Improvement Plan ---")
            print(f"Summary: {plan.summary}")

            if plan.weak_areas:
                print("\nWeak Areas Detected:")
                for wa in plan.weak_areas:
                    print(f" - [{wa.target_agent}] {wa.metric}: {wa.current_value} (Threshold: {wa.threshold})")

            if plan.strategies:
                print("\nSuggested Strategies:")
                for s in plan.strategies:
                    print(f" - [{s.type}] {s.description} (Priority: {s.priority})")

            if plan.suggested_upgrades:
                print("\nProposed Upgrades:")
                for u in plan.suggested_upgrades:
                    print(f" - Agent: {u.agent_name} -> {u.change_description}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
