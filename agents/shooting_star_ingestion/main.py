import argparse
import asyncio
import json
import os
from agents.shooting_star_ingestion.ingestion import ShootingStarIngestion

async def main():
    parser = argparse.ArgumentParser(description="Shooting Star Intelligence Ingestion CLI")
    parser.add_argument("project_path", help="Path to the system to ingest")
    parser.add_argument("--output", help="Path to save the ingestion report")

    args = parser.parse_args()

    if not os.path.exists(args.project_path):
        print(f"Error: Path {args.project_path} does not exist.")
        return

    ingestion = ShootingStarIngestion(args.project_path)
    report = await ingestion.ingest()

    output_json = json.dumps(report.model_dump(mode='json'), indent=2)

    if args.output:
        with open(args.output, 'w') as f:
            f.write(output_json)
        print(f"Ingestion report saved to {args.output}")
    else:
        print(output_json)

if __name__ == "__main__":
    asyncio.run(main())
