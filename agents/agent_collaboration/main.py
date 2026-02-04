import argparse
import sys
import json
from agents.agent_collaboration.collaboration import CollaborationManager

def main():
    parser = argparse.ArgumentParser(description="Agent Collaboration CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Help requests
    help_parser = subparsers.add_parser("request-help", help="Request help from another agent")
    help_parser.add_argument("--task-id", required=True)
    help_parser.add_argument("--requester", required=True)
    help_parser.add_argument("--target", required=True)
    help_parser.add_argument("--payload", default="{}")

    # Conflicts
    subparsers.add_parser("detect-conflicts", help="Detect task conflicts")

    # Workflows
    workflow_parser = subparsers.add_parser("create-workflow", help="Create a multi-agent workflow")
    workflow_parser.add_argument("--name", required=True)
    workflow_parser.add_argument("--tasks-file", required=True, help="JSON file containing list of task packets")

    # Merge
    merge_parser = subparsers.add_parser("merge", help="Merge outputs of multiple tasks")
    merge_parser.add_argument("--task-ids", required=True, help="Comma-separated task IDs")

    args = parser.parse_args()
    manager = CollaborationManager()

    if args.command == "request-help":
        payload = json.loads(args.payload)
        request = manager.request_help(args.task_id, args.requester, args.target, payload)
        print(json.dumps(request.model_dump(mode='json'), indent=2))

    elif args.command == "detect-conflicts":
        conflicts = manager.detect_conflicts()
        print(json.dumps([c.model_dump(mode='json') for c in conflicts], indent=2))

    elif args.command == "create-workflow":
        with open(args.tasks_file, 'r') as f:
            tasks_data = json.load(f)
        from fog.models.task import TaskPacket
        task_packets = [TaskPacket(**t) for t in tasks_data]
        workflow = manager.create_workflow(args.name, task_packets)
        print(json.dumps(workflow.model_dump(mode='json'), indent=2))

    elif args.command == "merge":
        tids = args.task_ids.split(",")
        merged = manager.merge_outputs(tids)
        print(json.dumps(merged, indent=2))

    elif not args.command:
        parser.print_help()

if __name__ == "__main__":
    main()
