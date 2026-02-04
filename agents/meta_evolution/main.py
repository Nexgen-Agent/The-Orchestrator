import argparse
import sys
import json
from agents.meta_evolution.analyzer import MetaEvolutionAnalyzer

def main():
    parser = argparse.ArgumentParser(description="Meta-System Evolution CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    subparsers.add_parser("analyze", help="Analyze ecosystem and propose evolution strategy")
    subparsers.add_parser("snapshot", help="Take a current snapshot of the ecosystem")
    subparsers.add_parser("trends", help="Analyze historical trends")

    args = parser.parse_args()
    analyzer = MetaEvolutionAnalyzer()

    if args.command == "analyze":
        strategy = analyzer.propose_evolution()
        print(json.dumps(strategy.model_dump(mode='json'), indent=2))

    elif args.command == "snapshot":
        snapshot = analyzer.take_snapshot()
        print(f"Snapshot taken: {snapshot.snapshot_id} at {snapshot.timestamp}")
        print(json.dumps(snapshot.model_dump(mode='json'), indent=2))

    elif args.command == "trends":
        trends = analyzer.analyze_trends()
        for trend in trends:
            print(f"Metric: {trend.metric} | Trend: {trend.trend_direction} ({trend.growth_rate:+.1%})")
            print(f"  Observation: {trend.observation}")

    elif not args.command:
        parser.print_help()

if __name__ == "__main__":
    main()
