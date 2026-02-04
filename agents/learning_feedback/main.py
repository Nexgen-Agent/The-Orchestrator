import argparse
import sys
import json
from agents.learning_feedback.feedback import LearningFeedbackAgent

def main():
    parser = argparse.ArgumentParser(description="Autonomous Learning Feedback CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    subparsers.add_parser("analyze", help="Analyze performance and generate insights")
    subparsers.add_parser("memory", help="View learning memory")
    subparsers.add_parser("proposals", help="View evolution proposals")

    args = parser.parse_args()
    agent = LearningFeedbackAgent()

    if args.command == "analyze":
        report = agent.analyze_performance()
        agent.feed_to_evolution_coordinator(report)
        print(json.dumps(report.model_dump(mode='json'), indent=2))

    elif args.command == "memory":
        print(json.dumps(agent.memory.model_dump(mode='json'), indent=2))

    elif args.command == "proposals":
        from fog.core.state import state_store
        state = state_store.get_state()
        print(json.dumps(state.get("evolution_proposals", []), indent=2))

    elif not args.command:
        parser.print_help()

if __name__ == "__main__":
    main()
