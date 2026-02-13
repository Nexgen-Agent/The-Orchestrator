import argparse
import asyncio
import json
import os
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from agents.personality_engine.analyzer import InteractionAnalyzer
from agents.personality_engine.engine import FingerprintManager, StyleAdaptor

async def main():
    parser = argparse.ArgumentParser(description="Personality & Adaptive Style Engine")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Analyze
    analyze_parser = subparsers.add_parser("analyze", help="Analyze text for style")
    analyze_parser.add_argument("--text", help="Direct text input")
    analyze_parser.add_argument("--file", help="Path to file containing text")
    analyze_parser.add_argument("--user", default="default_user", help="User ID to update profile for")

    # View Profile
    view_parser = subparsers.add_parser("view-profile", help="View a user's style fingerprint")
    view_parser.add_argument("--user", default="default_user", help="User ID to view")

    # Adapt
    adapt_parser = subparsers.add_parser("adapt", help="Generate adaptation parameters for a user")
    adapt_parser.add_argument("--user", default="default_user", help="User ID to generate for")

    args = parser.parse_args()
    manager = FingerprintManager()
    analyzer = InteractionAnalyzer()

    if args.command == "analyze":
        text = ""
        if args.text:
            text = args.text
        elif args.file:
            with open(args.file, "r") as f:
                text = f.read()

        if not text:
            print("Error: No text provided.")
            return

        analysis = analyzer.analyze_text(text)
        manager.update_profile(args.user, analysis)
        print(f"Analysis complete for user: {args.user}")
        print(json.dumps(analysis.model_dump(mode='json'), indent=2))

    elif args.command == "view-profile":
        profile = manager.get_profile(args.user)
        print(f"Style Fingerprint for user: {args.user}")
        print(json.dumps(profile.model_dump(mode='json'), indent=2))

    elif args.command == "adapt":
        profile = manager.get_profile(args.user)
        params = StyleAdaptor.generate_adaptation(profile)
        print(f"Adaptation Parameters for user: {args.user}")
        print(json.dumps(params.model_dump(mode='json'), indent=2))

    elif not args.command:
        parser.print_help()

if __name__ == "__main__":
    asyncio.run(main())
