import argparse
import json
import os
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from agents.backup_verifier.verifier import BackupVerifier

def main():
    parser = argparse.ArgumentParser(description="Backup Verification Agent")
    parser.add_argument("archive", help="Path to the backup zip archive")
    parser.add_argument("--project", help="Path to the original project for comparison", default=None)
    parser.add_argument("--id", help="Backup ID", default="cli-manual")
    parser.add_argument("--output", help="Output JSON file path", default=None)
    parser.add_argument("--indent", help="JSON indentation", type=int, default=2)

    args = parser.parse_args()

    if not os.path.exists(args.archive):
        print(f"Error: Archive {args.archive} does not exist.")
        sys.exit(1)

    verifier = BackupVerifier()

    try:
        if args.project:
            print(f"Comparing archive {args.archive} with project {args.project}...")
            report = verifier.compare_with_project(args.archive, args.project, args.id)
        else:
            print(f"Verifying integrity of archive {args.archive}...")
            report = verifier.verify_archive(args.archive, args.id)

        output_data = report.model_dump(mode='json')

        if args.output:
            with open(args.output, "w") as f:
                json.dump(output_data, f, indent=args.indent)
            print(f"Verification report saved to {args.output}")
        else:
            print(json.dumps(output_data, indent=args.indent))

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
