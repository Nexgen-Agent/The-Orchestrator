import argparse
import asyncio
import json
import os
import sys

# Add the parent directory to sys.path to allow imports from fog and agents
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from agents.website_insight_scout.scout import WebsiteScout
from agents.website_insight_scout.connector import MockAIInsightConnector

async def main():
    parser = argparse.ArgumentParser(description="Website Insight Scout Agent")
    parser.add_argument("urls", nargs="+", help="One or more URLs of the websites to analyze")
    parser.add_argument("--analyze-ui", action="store_true", default=True, help="Extract UI hierarchy")
    parser.add_argument("--analyze-ux", action="store_true", default=True, help="Analyze UX and marketing patterns")
    parser.add_argument("--generate-report", action="store_true", help="Generate a summary report")
    parser.add_argument("--output", help="Output JSON file path", default=None)
    parser.add_argument("--indent", help="JSON indentation", type=int, default=2)

    args = parser.parse_args()

    # Use Mock connector for CLI
    connector = MockAIInsightConnector()
    scout = WebsiteScout(connector)

    for url in args.urls:
        print(f"Scouting website: {url}...")
        try:
            result = await scout.analyze(
                url,
                analyze_ui=args.analyze_ui,
                analyze_ux=args.analyze_ux
            )

            output_data = result.model_dump(mode='json')

            if args.output:
                output_file = args.output if len(args.urls) == 1 else f"{args.output.split('.')[0]}_{url.replace('://', '_').replace('/', '_')}.json"
                with open(output_file, "w") as f:
                    json.dump(output_data, f, indent=args.indent)
                print(f"Analysis saved to {output_file}")
            else:
                if args.generate_report:
                    print("\n--- WEBSITE INSIGHT REPORT ---")
                    print(f"URL: {result.url}")
                    print(f"Timestamp: {result.timestamp}")

                    if result.design_patterns:
                        print("\n[Design Patterns]")
                        print(f"  Colors: {', '.join(result.design_patterns.colors)}")
                        print(f"  Typography: {', '.join(result.design_patterns.typography)}")

                    if result.marketing_psychology:
                        print("\n[Marketing & Psychology]")
                        print(f"  CTAs: {', '.join(result.marketing_psychology.ctas)}")
                        print(f"  Techniques: {', '.join(result.marketing_psychology.persuasion_techniques)}")

                    if result.architectural_insights:
                        print("\n[Architectural Insights]")
                        print(f"  Patterns: {', '.join(result.architectural_insights.logic_patterns)}")
                        print(f"  Optimizations: {', '.join(result.architectural_insights.optimizations)}")

                    if result.screenshots:
                        print(f"\nScreenshot saved at: {result.screenshots[0]}")
                    print("------------------------------\n")
                else:
                    print(json.dumps(output_data, indent=args.indent))

        except Exception as e:
            print(f"An error occurred while scouting {url}: {e}")
            # Continue with other URLs if any

if __name__ == "__main__":
    asyncio.run(main())
