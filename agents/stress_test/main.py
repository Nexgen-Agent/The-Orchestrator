import argparse
import asyncio
import json
import sys
from agents.stress_test.stresser import StressTester, StressTestConfig

async def async_main():
    parser = argparse.ArgumentParser(description="Stress Test Agent CLI")
    parser.add_argument("--tasks", type=int, default=10, help="Number of tasks")
    parser.add_argument("--concurrency", type=int, default=5, help="Concurrency level")
    parser.add_argument("--payload", type=int, default=1, help="Payload size in KB")
    parser.add_argument("--output", help="Save report to JSON file")

    args = parser.parse_args()

    config = StressTestConfig(
        num_tasks=args.tasks,
        concurrency=args.concurrency,
        payload_size_kb=args.payload
    )

    print(f"Starting stress test: {args.tasks} tasks, concurrency {args.concurrency}...")
    stresser = StressTester()
    report = await stresser.run_stress_test(config)

    output_data = report.model_dump(mode='json')

    if args.output:
        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)
        print(f"Report saved to {args.output}")
    else:
        # Print summary
        res = report.result
        print("\n--- Stress Test Result ---")
        print(f"Stability: {report.stability_rating}")
        print(f"Successful: {res.successful_tasks}/{res.total_tasks}")
        print(f"Avg Latency: {res.average_latency_ms:.2f}ms")
        print(f"P95 Latency: {res.p95_latency_ms:.2f}ms")
        print(f"Throughput: {res.throughput_tps:.2f} TPS")

        if report.bottlenecks:
            print("\nBottlenecks Detected:")
            for b in report.bottlenecks:
                print(f" - {b}")

        print("\nSuggestions:")
        for s in report.optimization_suggestions:
            print(f" - {s}")

def main():
    asyncio.run(async_main())

if __name__ == "__main__":
    main()
