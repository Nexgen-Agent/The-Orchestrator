import sys
import os
import subprocess

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 -m fog.cli <command> [args]")
        print("Available commands:")
        print("  scout-website <url> [options]   - Analyze a website for insights")
        print("  multi-analyze <urls> [options]  - Compare multiple websites and rank elements")
        print("  personality <command> [args]    - Adaptive personality engine commands")
        print("  friction-solve [args]           - Technical friction solver agent")
        print("  self-evolve [args]              - Autonomous system evolution engine")
        print("  mate [args]                     - Meta-Agent Trainer Engine (MATE)")
        print("  shooting-star-intel [args]      - Shooting Star Intelligence Layer")
        sys.exit(1)

    command = sys.argv[1]
    args = sys.argv[2:]

    if command == "personality":
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        agent_path = os.path.join(root_dir, "agents", "personality_engine", "main.py")
        cmd = [sys.executable, agent_path] + args
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            sys.exit(e.returncode)
    elif command == "friction-solve":
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        agent_path = os.path.join(root_dir, "agents", "friction_solver", "main.py")
        cmd = [sys.executable, agent_path] + args
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            sys.exit(e.returncode)
    elif command == "self-evolve":
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        agent_path = os.path.join(root_dir, "agents", "self_evolution_engine", "main.py")
        cmd = [sys.executable, agent_path] + args
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            sys.exit(e.returncode)
    elif command == "mate":
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        agent_path = os.path.join(root_dir, "agents", "meta_agent_trainer", "main.py")
        cmd = [sys.executable, agent_path] + args
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            sys.exit(e.returncode)
    elif command == "shooting-star-intel":
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        agent_path = os.path.join(root_dir, "agents", "shooting_star_intelligence", "main.py")
        cmd = [sys.executable, agent_path] + args
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            sys.exit(e.returncode)
    elif command in ["scout-website", "multi-analyze"]:
        # Call the Website Insight Scout main.py
        # Get the root directory (one level up from fog/ directory)
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        agent_path = os.path.join(root_dir, "agents", "website_insight_scout", "main.py")

        extra_args = []
        if command == "multi-analyze":
            extra_args = ["--compare"]

        cmd = [sys.executable, agent_path] + extra_args + args
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            sys.exit(e.returncode)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
