import sys
import os
import subprocess

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 -m fog.cli <command> [args]")
        print("Available commands:")
        print("  scout-website <url> [options]  - Analyze a website for insights")
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[2:]

    if command == "scout-website":
        # Call the Website Insight Scout main.py
        # Get the root directory (one level up from fog/ directory)
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        agent_path = os.path.join(root_dir, "agents", "website_insight_scout", "main.py")
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
