import argparse
import json
import os
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from agents.prompt_orchestrator.orchestrator import PromptOrchestrator

def main():
    parser = argparse.ArgumentParser(description="Prompt Orchestration Agent")
    parser.add_argument("input", help="Path to the architecture map JSON file")
    parser.add_argument("--output", help="Output JSON file path", default=None)
    parser.add_argument("--indent", help="JSON indentation", type=int, default=2)

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: Input file {args.input} does not exist.")
        sys.exit(1)

    try:
        with open(args.input, "r") as f:
            architecture_map = json.load(f)

        print(f"Orchestrating prompts from: {args.input}...")
        orchestrator = PromptOrchestrator()
        output = orchestrator.orchestrate(architecture_map)
        output_data = output.model_dump(mode='json')

        if args.output:
            with open(args.output, "w") as f:
                json.dump(output_data, f, indent=args.indent)
            print(f"Orchestration output saved to {args.output}")
        else:
            print(json.dumps(output_data, indent=args.indent))

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
