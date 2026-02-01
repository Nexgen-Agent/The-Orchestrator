import argparse
import json
import os
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from agents.test_generator.generator import TestGenerator

def main():
    parser = argparse.ArgumentParser(description="Automated Test Generator Agent")
    parser.add_argument("input", help="Path to the analyzer JSON output file")
    parser.add_argument("--output", help="Output JSON file path for report", default=None)
    parser.add_argument("--write", help="Write generated tests to project tests/ directory", action="store_true")
    parser.add_argument("--indent", help="JSON indentation", type=int, default=2)

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file {args.input} does not exist.")
        sys.exit(1)

    try:
        with open(args.input, "r") as f:
            project_analysis = json.load(f)

        print(f"Generating tests from: {args.input}...")
        generator = TestGenerator()
        report = generator.run_full_report(project_analysis)
        output_data = report.model_dump(mode='json')

        if args.write:
            for test_file in report.generated_files:
                os.makedirs(os.path.dirname(test_file.file_path), exist_ok=True)
                with open(test_file.file_path, "w") as f:
                    f.write(test_file.content)
                print(f"Wrote test file: {test_file.file_path}")

        if args.output:
            with open(args.output, "w") as f:
                json.dump(output_data, f, indent=args.indent)
            print(f"Generation report saved to {args.output}")
        else:
            if not args.write:
                print(json.dumps(output_data, indent=args.indent))

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
