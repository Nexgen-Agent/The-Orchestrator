import argparse
import asyncio
import json
import os
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from agents.code_quality.handler import analyze_project_quality
from agents.code_quality.evaluator import CodeQualityEvaluator

async def main():
    parser = argparse.ArgumentParser(description="Code Quality Evaluation Agent")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--path", help="Path to the Python project to evaluate")
    group.add_argument("--file", help="Path to a single Python file to evaluate")
    parser.add_argument("--output", help="Output JSON file path", default=None)
    parser.add_argument("--indent", help="JSON indentation", type=int, default=2)

    args = parser.parse_args()

    try:
        if args.path:
            print(f"Evaluating project quality at: {args.path}...")
            report = await analyze_project_quality(args.path)
            output_data = report.model_dump(mode='json')
        else:
            print(f"Evaluating file quality: {args.file}...")
            evaluator = CodeQualityEvaluator(args.file)
            report = evaluator.evaluate()
            output_data = report.model_dump(mode='json')

        if args.output:
            with open(args.output, "w") as f:
                json.dump(output_data, f, indent=args.indent)
            print(f"Quality report saved to {args.output}")
        else:
            print(json.dumps(output_data, indent=args.indent))

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
