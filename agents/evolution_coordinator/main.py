import argparse
import asyncio
import json
import os
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from agents.evolution_coordinator.coordinator import EvolutionCoordinator

async def main():
    parser = argparse.ArgumentParser(description="Autonomous Evolution Coordinator")
    parser.add_argument("--action", choices=["monitor", "trigger", "apply"], default="monitor")
    parser.add_argument("--project", help="Path to the project for apply action", default=None)
    parser.add_argument("--step-json", help="JSON string of the evolution step to apply", default=None)
    parser.add_argument("--output", help="Output JSON file path", default=None)
    parser.add_argument("--indent", help="JSON indentation", type=int, default=2)

    args = parser.parse_args()

    coordinator = EvolutionCoordinator()

    try:
        if args.action == "monitor":
            print("Monitoring agent performance...")
            metrics = coordinator.monitor_agent_performance()
            output_data = metrics
        elif args.action == "trigger":
            print("Triggering improvement cycle...")
            cycle = coordinator.trigger_improvement_cycle()
            if cycle:
                output_data = cycle.model_dump(mode='json')
            else:
                output_data = {"message": "No improvements needed."}
        elif args.action == "apply":
            if not args.project or not args.step_json:
                print("Error: --project and --step-json are required for apply action.")
                sys.exit(1)

            from agents.evolution_coordinator.models import EvolutionStep
            step = EvolutionStep(**json.loads(args.step_json))
            print(f"Applying evolution step for {step.target_agent}...")
            await coordinator.apply_evolution_step(step, args.project)
            output_data = step.model_dump(mode='json')

        if args.output:
            with open(args.output, "w") as f:
                json.dump(output_data, f, indent=args.indent)
            print(f"Result saved to {args.output}")
        else:
            print(json.dumps(output_data, indent=args.indent))

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
