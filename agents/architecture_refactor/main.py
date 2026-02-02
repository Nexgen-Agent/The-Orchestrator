import argparse
import json
import sys
from agents.architecture_refactor.refactorer import ArchitectureRefactorer

def main():
    parser = argparse.ArgumentParser(description="Architecture Refactor Agent CLI")
    parser.add_argument("--analysis", required=True, help="Path to project analysis JSON")
    parser.add_argument("--graph", required=True, help="Path to dependency graph JSON")
    parser.add_argument("--output", help="Path to save refactor plan JSON")

    args = parser.parse_args()

    try:
        with open(args.analysis, 'r') as f:
            analysis_data = json.load(f)
        with open(args.graph, 'r') as f:
            graph_data = json.load(f)

        refactorer = ArchitectureRefactorer()
        plan = refactorer.analyze_and_propose(analysis_data, graph_data)

        output_json = json.dumps(plan.model_dump(mode='json'), indent=2)

        if args.output:
            with open(args.output, 'w') as f:
                f.write(output_json)
            print(f"Refactor plan saved to {args.output}")
        else:
            print(output_json)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
