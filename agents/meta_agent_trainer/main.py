import asyncio
import argparse
import sys
import json
from agents.meta_agent_trainer.engine import MetaAgentTrainerEngine
from agents.meta_agent_trainer.models import AgentBlueprint

async def main():
    parser = argparse.ArgumentParser(description="Meta-Agent Trainer Engine (MATE) CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate a new agent from blueprint")
    gen_parser.add_argument("--name", required=True, help="Agent name")
    gen_parser.add_argument("--base", default="generic_agent", help="Base module")

    # Train command
    train_parser = subparsers.add_parser("train", help="Simulate agent training")
    train_parser.add_argument("--name", required=True, help="Agent name")
    train_parser.add_argument("--project", required=True, help="Project path for sandbox")

    # Optimize command
    opt_parser = subparsers.add_parser("optimize", help="Optimize agent code")
    opt_parser.add_argument("--dir", required=True, help="Agent directory")

    # Evolve command
    subparsers.add_parser("evolve-self", help="Run MATE self-evolution")

    # Audit command
    subparsers.add_parser("audit", help="Inspect training and audit history")

    args = parser.parse_args()
    engine = MetaAgentTrainerEngine()

    try:
        if args.command == "generate":
            blueprint = AgentBlueprint(agent_name=args.name, base_module=args.base)
            path = engine.generate_agent_from_blueprint(blueprint)
            print(f"Agent generated at: {path}")

        elif args.command == "train":
            print(f"Starting training simulation for {args.name}...")
            report = await engine.simulate_training(args.name, args.project)
            print(json.dumps(report.model_dump(mode='json'), indent=2))

        elif args.command == "optimize":
            print(f"Optimizing code in {args.dir}...")
            actions = engine.optimize_agent_code(args.dir)
            print("Actions performed:")
            for action in actions:
                print(f" - {action}")

        elif args.command == "evolve-self":
            print("Running MATE self-evolution...")
            result = engine.evolve_trainer()
            print(json.dumps(result, indent=2))

        elif args.command == "audit":
            print("MATE History Audit:")
            print(json.dumps(engine.history.model_dump(mode='json'), indent=2))

        else:
            parser.print_help()

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
