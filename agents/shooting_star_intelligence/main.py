import asyncio
import argparse
import sys
import json
from agents.shooting_star_intelligence.intelligence import ShootingStarIntelligence

async def main():
    parser = argparse.ArgumentParser(description="Shooting Star Intelligence (SSI) CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Track command
    track_parser = subparsers.add_parser("track", help="Track agent capability")
    track_parser.add_argument("--name", required=True, help="Agent name")
    track_parser.add_argument("--cap", type=float, required=True, help="Capability percentage")

    # Audit command
    audit_parser = subparsers.add_parser("audit", help="Perform readiness audit")
    audit_parser.add_argument("--name", required=True, help="Agent name")
    audit_parser.add_argument("--project", required=True, help="Project path for simulation")

    # Dashboard command
    subparsers.add_parser("dashboard", help="View readiness dashboard")

    args = parser.parse_args()
    engine = ShootingStarIntelligence()

    try:
        if args.command == "track":
            progress = await engine.track_progress(args.name, args.cap)
            print(f"Tracking updated for {args.name}: {progress.capability_percentage}% capability.")

        elif args.command == "audit":
            print(f"Starting readiness audit for {args.name}...")
            report = await engine.perform_readiness_audit(args.name, args.project)
            print(json.dumps(report.model_dump(mode='json'), indent=2))

        elif args.command == "dashboard":
            print("=== SHOOTING STAR READINESS DASHBOARD ===")
            print(f"Overall System Readiness: {engine.readiness.overall_readiness:.2f}%")
            print("-" * 40)
            for p in engine.readiness.module_progress:
                status = "READY" if p.capability_percentage >= 98.0 else "IN PROGRESS"
                print(f"[{status}] {p.agent_name:20} | Cap: {p.capability_percentage:5.1f}% | Prob: {p.deployment_probability:.2f}")

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
