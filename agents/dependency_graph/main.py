import argparse
import json
import os
import sys

# Add the parent directory to sys.path to allow imports from agents.dependency_graph
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from agents.dependency_graph.graph import DependencyGraphAgent

def main():
    parser = argparse.ArgumentParser(description="Dependency Graph Agent")
    parser.add_argument("input", help="Path to the analyzer JSON output file")
    parser.add_argument("--output", help="Output JSON file path", default=None)
    parser.add_argument("--indent", help="JSON indentation", type=int, default=2)

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file {args.input} does not exist.")
        sys.exit(1)

    try:
        with open(args.input, "r") as f:
            analyzer_output = json.load(f)

        print(f"Building dependency graph from: {args.input}...")
        agent = DependencyGraphAgent()
        agent.build_graph(analyzer_output)
        analysis = agent.analyze()
        output_data = analysis.model_dump(mode='json')

        if args.output:
            with open(args.output, "w") as f:
                json.dump(output_data, f, indent=args.indent)
            print(f"Analysis saved to {args.output}")
        else:
            print(json.dumps(output_data, indent=args.indent))

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
