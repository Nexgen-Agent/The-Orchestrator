import argparse
import json
import os
from agents.visualization.visualizer import VisualizationAgent
from agents.visualization.models import VisualizationRequest, GraphType

def main():
    parser = argparse.ArgumentParser(description="Visualization Agent CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    generate_parser = subparsers.add_parser("generate", help="Generate a graph visualization")
    generate_parser.add_argument("--type", choices=[t.value for t in GraphType], required=True, help="Type of graph")
    generate_parser.add_argument("--data", required=True, help="Path to JSON data file")
    generate_parser.add_argument("--format", default="png", choices=["png", "json", "both"], help="Output format")
    generate_parser.add_argument("--title", help="Diagram title")
    generate_parser.add_argument("--output-dir", default="storage/visualizations", help="Output directory")

    list_parser = subparsers.add_parser("list", help="List generated visualizations")

    args = parser.parse_args()
    agent = VisualizationAgent(output_dir=args.output_dir if hasattr(args, 'output_dir') else "storage/visualizations")

    if args.command == "generate":
        if not os.path.exists(args.data):
            print(f"Error: Data file {args.data} not found.")
            return

        with open(args.data, 'r') as f:
            data = json.load(f)

        request = VisualizationRequest(
            graph_type=GraphType(args.type),
            data=data,
            output_format=args.format,
            title=args.title
        )

        output = agent.generate_visualization(request)
        print(f"Visualization generated successfully!")
        print(f"ID: {output.visualization_id}")
        if output.png_path:
            print(f"PNG Path: {output.png_path}")
        if output.json_data:
            print(f"JSON Data generated.")

    elif args.command == "list":
        vis = agent.list_visualizations()
        if not vis:
            print("No visualizations found.")
        else:
            print("Generated Visualizations:")
            for v in vis:
                print(f"  - {v}")

    elif not args.command:
        parser.print_help()

if __name__ == "__main__":
    main()
