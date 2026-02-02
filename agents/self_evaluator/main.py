import argparse
import json
import sys
import os
from agents.self_evaluator.evaluator import SelfEvaluator

def main():
    parser = argparse.ArgumentParser(description="Agent Self-Evaluator CLI")
    parser.add_argument("--agent", required=True, help="Name of the agent to evaluate")
    parser.add_argument("--output", help="Path to save evaluation report JSON")

    args = parser.parse_args()

    try:
        evaluator = SelfEvaluator()
        report = evaluator.evaluate_agent(args.agent)

        if not report:
            print(f"No performance data found for agent '{args.agent}'.")
            sys.exit(0)

        output_data = report.model_dump(mode='json')
        output_json = json.dumps(output_data, indent=2)

        if args.output:
            with open(args.output, 'w') as f:
                f.write(output_json)
            print(f"Evaluation report for '{args.agent}' saved to {args.output}")
        else:
            print(f"\n--- Self-Evaluation Report: {args.agent} ---")
            print(f"Performance Score: {report.performance_score}/100")
            print(f"Success Rate: {report.metrics.success_rate:.2%}")
            print(f"Avg Execution Time: {report.metrics.avg_execution_time:.2f}s")
            print(f"History Depth: {report.history_depth} tasks")

            if report.metrics.failure_patterns:
                print("\nFailure Patterns Detected:")
                for p in report.metrics.failure_patterns:
                    print(f" - {p}")

            print("\nImprovement Suggestions:")
            for s in report.improvement_suggestions:
                print(f" - {s}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
