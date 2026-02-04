import argparse
import asyncio
import json
import os
import sys

# Add the parent directory to sys.path to allow imports from fog and agents
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from agents.website_insight_scout.scout import WebsiteScout
from agents.website_insight_scout.multi_scout import MultiWebsiteScout
from agents.website_insight_scout.connector import MockAIInsightConnector
from agents.website_insight_scout.scoring import compare_sites
from agents.website_insight_scout.replication import generate_replication_manifest

async def main():
    parser = argparse.ArgumentParser(description="Website Insight & Multi-Site Analyzer Scout")
    parser.add_argument("urls", nargs="+", help="One or more URLs of the websites to analyze")
    parser.add_argument("--analyze-ui", action="store_true", default=True, help="Extract UI hierarchy")
    parser.add_argument("--analyze-ux", action="store_true", default=True, help="Analyze UX and marketing patterns")
    parser.add_argument("--compare", action="store_true", help="Compare multiple sites and rank them")
    parser.add_argument("--replicate", action="store_true", help="Generate replication manifest for the first URL")
    parser.add_argument("--generate-report", action="store_true", help="Generate a summary report")
    parser.add_argument("--output", help="Output JSON file path", default=None)
    parser.add_argument("--indent", help="JSON indentation", type=int, default=2)

    args = parser.parse_args()

    # Use Mock connector for CLI
    connector = MockAIInsightConnector()
    scout = WebsiteScout(connector)

    if args.compare and len(args.urls) > 1:
        print(f"Comparing {len(args.urls)} websites...")
        multi_scout = MultiWebsiteScout(scout)
        results = await multi_scout.analyze_batch(args.urls)
        comparison = compare_sites(results)

        output_data = comparison.model_dump(mode='json')

        if args.output:
            with open(args.output, "w") as f:
                json.dump(output_data, f, indent=args.indent)
            print(f"Comparison saved to {args.output}")
        else:
            if args.generate_report:
                print("\n--- MULTI-SITE COMPARISON REPORT ---")
                print(f"Timestamp: {comparison.timestamp}")
                print("\n[Rankings]")
                for url, score in comparison.rankings.items():
                    print(f"  {url}: {score:.2f}")

                print("\n[Top Elements]")
                for i, el in enumerate(comparison.top_elements[:5]):
                    print(f"  {i+1}. {el.element.tag} (Priority: {el.priority}, Score: {el.score.overall:.2f})")
                    if el.element.text:
                        print(f"     Text: {el.element.text[:50]}")

                print("\n[Common Patterns]")
                print(f"  {', '.join(comparison.common_patterns)}")
                print("------------------------------------\n")
            else:
                print(json.dumps(output_data, indent=args.indent))

    elif args.replicate:
        url = args.urls[0]
        print(f"Generating replication manifest for {url}...")
        analysis = await scout.analyze(url)
        manifest = generate_replication_manifest(analysis)

        output_data = manifest.model_dump(mode='json')
        if args.output:
            with open(args.output, "w") as f:
                json.dump(output_data, f, indent=args.indent)
            print(f"Replication manifest saved to {args.output}")
        else:
            print(json.dumps(output_data, indent=args.indent))

    else:
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

if __name__ == "__main__":
    asyncio.run(main())
