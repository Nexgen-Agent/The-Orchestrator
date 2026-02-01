import argparse
import asyncio
import json
import os
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from agents.security_analyzer.handler import analyze_project_security
from agents.security_analyzer.analyzer import SecurityAnalyzer

async def main():
    parser = argparse.ArgumentParser(description="Security Analysis Agent")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--path", help="Path to the Python project to scan")
    group.add_argument("--file", help="Path to a single Python file to scan")
    parser.add_argument("--output", help="Output JSON file path", default=None)
    parser.add_argument("--indent", help="JSON indentation", type=int, default=2)

    args = parser.parse_args()

    try:
        if args.path:
            print(f"Scanning project security at: {args.path}...")
            report = await analyze_project_security(args.path)
            output_data = report.model_dump(mode='json')
        else:
            print(f"Scanning file security: {args.file}...")
            analyzer = SecurityAnalyzer()
            report = analyzer.scan_file(args.file)
            output_data = report.model_dump(mode='json')

        if args.output:
            with open(args.output, "w") as f:
                json.dump(output_data, f, indent=args.indent)
            print(f"Security report saved to {args.output}")
        else:
            print(json.dumps(output_data, indent=args.indent))

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
