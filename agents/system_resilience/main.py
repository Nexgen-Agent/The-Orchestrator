import argparse
import sys
import json
import asyncio
from agents.system_resilience.resilience import ResilienceManager

def main():
    parser = argparse.ArgumentParser(description="System Resilience CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    subparsers.add_parser("analyze", help="Detect failing patterns and attempt fixes")
    subparsers.add_parser("history", help="View resilience action history")

    safe_mode_parser = subparsers.add_parser("safe-mode", help="Enable or disable safe mode")
    safe_mode_parser.add_argument("status", choices=["on", "off"], help="Set safe mode on or off")

    args = parser.parse_args()
    resilience = ResilienceManager()

    if args.command == "analyze":
        report = asyncio.run(resilience.detect_and_fix())
        print(json.dumps(report.model_dump(mode='json'), indent=2))

    elif args.command == "history":
        history = resilience.get_resilience_history()
        for action in history:
            print(f"[{action.timestamp}] {action.action_type} on {action.target} | Status: {action.status}")
            print(f"  Reason: {action.reason}")

    elif args.command == "safe-mode":
        active = args.status == "on"
        resilience.set_safe_mode(active)
        print(f"Safe mode turned {args.status}.")

    elif not args.command:
        parser.print_help()

if __name__ == "__main__":
    main()
