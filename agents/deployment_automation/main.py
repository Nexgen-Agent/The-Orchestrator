import argparse
import asyncio
import json
import os
from agents.deployment_automation.automation import DeploymentAutomation

async def main():
    parser = argparse.ArgumentParser(description="Deployment Automation CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    deploy_parser = subparsers.add_parser("deploy", help="Run a deployment")
    deploy_parser.add_argument("--project", required=True, help="Path to project")
    deploy_parser.add_argument("--service", required=True, help="Service name")
    deploy_parser.add_argument("--tag", default="latest", help="Image tag")
    deploy_parser.add_argument("--env", help="JSON string of env vars")

    rollback_parser = subparsers.add_parser("rollback", help="Rollback a deployment")
    rollback_parser.add_argument("--project", required=True)
    rollback_parser.add_argument("--id", required=True, help="Deployment ID")

    args = parser.parse_args()

    if args.command == "deploy":
        automation = DeploymentAutomation(args.project)
        manifest = automation.generate_manifest(args.service, args.tag)
        if args.env:
            manifest.env_vars.update(json.loads(args.env))

        report = await automation.run_deployment(manifest)
        print(json.dumps(report.model_dump(mode='json'), indent=2))

    elif args.command == "rollback":
        automation = DeploymentAutomation(args.project)
        try:
            report = await automation.rollback(args.id)
            print(json.dumps(report.model_dump(mode='json'), indent=2))
        except Exception as e:
            print(f"Error: {e}")

    elif not args.command:
        parser.print_help()

if __name__ == "__main__":
    asyncio.run(main())
