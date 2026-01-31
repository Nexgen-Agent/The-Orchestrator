import argparse
import asyncio
import json
import os
import sys

# Add the parent directory to sys.path to allow imports from agents.structure_analyzer
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from agents.structure_analyzer.handler import analyze_project

async def main():
    parser = argparse.ArgumentParser(description="Code Structure Analyzer Agent")
    parser.add_argument("path", help="Path to the Python project or folder to analyze")
    parser.add_argument("--output", help="Output JSON file path", default=None)
    parser.add_argument("--indent", help="JSON indentation", type=int, default=2)

    args = parser.parse_args()

    if not os.path.exists(args.path):
        print(f"Error: Path {args.path} does not exist.")
        sys.exit(1)

    print(f"Analyzing structure for: {args.path}...")
    try:
        analysis = await analyze_project(args.path)
        output_data = analysis.model_dump(mode='json')

        if args.output:
            with open(args.output, "w") as f:
                json.dump(output_data, f, indent=args.indent)
            print(f"Analysis saved to {args.output}")
        else:
            print(json.dumps(output_data, indent=args.indent))

    except Exception as e:
        print(f"An error occurred during analysis: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
