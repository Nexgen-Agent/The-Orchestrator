import argparse
import json
import os
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from agents.orchestration_optimizer.optimizer import OrchestrationOptimizer

def main():
    parser = argparse.ArgumentParser(description="Orchestration Optimization Agent")
    parser.add_argument("--logs", help="Path to the audit log file", default="storage/audit.log")
    parser.add_argument("--output", help="Output JSON file path", default=None)
    parser.add_argument("--indent", help="JSON indentation", type=int, default=2)

    args = parser.parse_args()

    if not os.path.exists(args.logs):
        print(f"Error: Log file {args.logs} does not exist.")
        sys.exit(1)

    try:
        print(f"Analyzing orchestration logs from: {args.logs}...")
        optimizer = OrchestrationOptimizer(args.logs)
        report = optimizer.analyze()
        output_data = report.model_dump(mode='json')

        if args.output:
            with open(args.output, "w") as f:
                json.dump(output_data, f, indent=args.indent)
            print(f"Optimization report saved to {args.output}")
        else:
            print(json.dumps(output_data, indent=args.indent))

    except Exception as e:
        print(f"An error occurred during analysis: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
