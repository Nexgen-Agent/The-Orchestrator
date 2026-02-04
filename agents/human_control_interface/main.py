import argparse
import sys
import json
from agents.human_control_interface.control import HumanControlInterface

def main():
    parser = argparse.ArgumentParser(description="Human Control Interface CLI for FOG")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Approvals
    subparsers.add_parser("list-approvals", help="List pending approvals")

    approve_parser = subparsers.add_parser("approve", help="Approve a request")
    approve_parser.add_argument("request_id", help="ID of the approval request")
    approve_parser.add_argument("--approver", default="admin", help="Name of the approver")
    approve_parser.add_argument("--reason", help="Reason for approval")

    reject_parser = subparsers.add_parser("reject", help="Reject a request")
    reject_parser.add_argument("request_id", help="ID of the approval request")
    reject_parser.add_argument("--approver", default="admin", help="Name of the approver")
    reject_parser.add_argument("--reason", help="Reason for rejection")

    # Orchestration Control
    subparsers.add_parser("pause", help="Pause orchestration")
    subparsers.add_parser("resume", help="Resume orchestration")
    subparsers.add_parser("stop", help="Emergency stop")

    # Agent Control
    toggle_parser = subparsers.add_parser("toggle-agent", help="Enable/Disable an agent")
    toggle_parser.add_argument("agent_name", help="Name of the agent")
    toggle_parser.add_argument("--disable", action="store_true", help="Disable the agent (default is enable)")

    # Rollback
    rollback_parser = subparsers.add_parser("rollback", help="Trigger manual rollback")
    rollback_parser.add_argument("backup_id", help="ID of the backup to rollback to")

    args = parser.parse_args()
    control = HumanControlInterface()

    if args.command == "list-approvals":
        approvals = control.get_pending_approvals()
        if not approvals:
            print("No pending approvals.")
        for app in approvals:
            print(f"ID: {app.request_id} | Task: {app.task_id} | Requester: {app.requester} | Time: {app.timestamp}")
            print(f"  Details: {json.dumps(app.details, indent=2)}")

    elif args.command == "approve":
        try:
            request = control.approve_request(args.request_id, args.approver, args.reason)
            print(f"Request {args.request_id} approved.")
        except Exception as e:
            print(f"Error: {e}")

    elif args.command == "reject":
        try:
            request = control.reject_request(args.request_id, args.approver, args.reason)
            print(f"Request {args.request_id} rejected.")
        except Exception as e:
            print(f"Error: {e}")

    elif args.command == "pause":
        control.set_pause(True)
        print("Orchestration paused.")

    elif args.command == "resume":
        control.set_pause(False)
        print("Orchestration resumed.")

    elif args.command == "stop":
        control.set_emergency_stop(True)
        print("Emergency stop activated.")

    elif args.command == "toggle-agent":
        enabled = not args.disable
        control.toggle_agent(args.agent_name, enabled)
        print(f"Agent {args.agent_name} {'enabled' if enabled else 'disabled'}.")

    elif args.command == "rollback":
        from fog.core.backup import backup_manager
        try:
            backup_manager.rollback(args.backup_id)
            print(f"Successfully rolled back to {args.backup_id}")
        except Exception as e:
            print(f"Error during rollback: {e}")

    elif not args.command:
        parser.print_help()

if __name__ == "__main__":
    main()
