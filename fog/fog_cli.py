#!/usr/bin/env python3
import sys
import os
import subprocess

def main():
    if len(sys.argv) < 2:
        print("Usage: fog <command> [args]")
        print("Available commands:")
        print("  scout-website <url> [options]  - Analyze a website for insights")
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[2:]

    if command == "scout-website":
        # Call the Website Insight Scout main.py
        agent_path = os.path.join(os.path.dirname(__file__), "agents", "website_insight_scout", "main.py")
        cmd = [sys.executable, agent_path] + args
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            sys.exit(e.returncode)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
