import argparse
import asyncio
import json
import os
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from agents.logic_summarizer.summarizer import LogicSummarizer
from agents.logic_summarizer.connector import MockLLMConnector

async def main():
    parser = argparse.ArgumentParser(description="Logic Summarizer Agent")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", help="Path to the Python file to summarize")
    group.add_argument("--text", help="Direct text input to summarize")
    parser.add_argument("--output", help="Output JSON file path", default=None)
    parser.add_argument("--indent", help="JSON indentation", type=int, default=2)

    args = parser.parse_args()

    # Using Mock connector for CLI
    connector = MockLLMConnector()
    summarizer = LogicSummarizer(connector)

    try:
        if args.file:
            print(f"Summarizing file: {args.file}...")
            result = await summarizer.summarize_file(args.file)
        else:
            print("Summarizing text input...")
            result = await summarizer.summarize_text(args.text)

        output_data = result.model_dump(mode='json')

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
    asyncio.run(main())
