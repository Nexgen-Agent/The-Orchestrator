import asyncio
import argparse
import sys
import json
from agents.self_evolution_engine.engine import SelfEvolutionEngine

async def main():
    parser = argparse.ArgumentParser(description="Self-Evolution Engine (SEE) Agent")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Run command
    run_parser = subparsers.add_parser("run", help="Run an optimization cycle")
    run_parser.add_argument("--project", required=True, help="Path to the project")

    # Audit command
    audit_parser = subparsers.add_parser("audit", help="Inspect evolution history")

    args = parser.parse_args()
    engine = SelfEvolutionEngine()

    if args.command == "run":
        print(f"Starting optimization cycle for {args.project}...")
        report = await engine.run_optimization_cycle(args.project)
        print(json.dumps(report.model_dump(mode='json'), indent=2))
    elif args.command == "audit":
        print("Evolution History Audit:")
        print(json.dumps(engine.history.model_dump(mode='json'), indent=2))
    else:
        parser.print_help()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
