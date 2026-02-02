import asyncio
import time
import uuid
import statistics
from datetime import datetime, timezone
from typing import List, Dict, Any
from agents.stress_test.models import (
    StressTestConfig, StressResult, PerformanceMetric, StressReport
)

class StressTester:
    def __init__(self, engine: Any = None):
        self.engine = engine # In a real system, this would be the OrchestrationEngine

    async def run_stress_test(self, config: StressTestConfig) -> StressReport:
        start_time = datetime.now(timezone.utc)
        metrics: List[PerformanceMetric] = []

        # Simulate concurrent tasks
        semaphore = asyncio.Semaphore(config.concurrency)

        async def execute_mock_task():
            async with semaphore:
                task_id = str(uuid.uuid4())
                task_start = time.perf_counter()

                # Simulate "work"
                # Heaviness based on payload size
                await asyncio.sleep(0.01 * config.payload_size_kb)

                duration_ms = (time.perf_counter() - task_start) * 1000
                metrics.append(PerformanceMetric(
                    task_id=task_id,
                    duration_ms=duration_ms,
                    status="completed"
                ))

        tasks = [execute_mock_task() for _ in range(config.num_tasks)]
        await asyncio.gather(*tasks)

        end_time = datetime.now(timezone.utc)
        result = self._calculate_result(metrics, start_time, end_time)

        return self._generate_report(config, result)

    def _calculate_result(self, metrics: List[PerformanceMetric], start_time: datetime, end_time: datetime) -> StressResult:
        total = len(metrics)
        successful = len([m for m in metrics if m.status == "completed"])
        failed = total - successful

        durations = [m.duration_ms for m in metrics]
        avg_latency = statistics.mean(durations) if durations else 0
        p95_latency = statistics.quantiles(durations, n=20)[18] if len(durations) >= 20 else max(durations) if durations else 0

        total_duration_s = (end_time - start_time).total_seconds()
        throughput = total / total_duration_s if total_duration_s > 0 else 0

        return StressResult(
            total_tasks=total,
            successful_tasks=successful,
            failed_tasks=failed,
            average_latency_ms=avg_latency,
            p95_latency_ms=p95_latency,
            throughput_tps=throughput,
            start_time=start_time,
            end_time=end_time,
            metrics=metrics
        )

    def _generate_report(self, config: StressTestConfig, result: StressResult) -> StressReport:
        bottlenecks = []
        suggestions = []
        stability = "Stable"

        if result.p95_latency_ms > 500:
            bottlenecks.append("High tail latency (P95 > 500ms)")
            suggestions.append("Consider horizontal scaling or optimized task routing.")
            stability = "Degraded"

        if result.failed_tasks > 0:
            bottlenecks.append(f"Task failures under load: {result.failed_tasks}")
            suggestions.append("Investigate error rates and resource constraints.")
            stability = "Unstable"

        if result.throughput_tps < (config.concurrency / 2) and config.num_tasks > 10:
             bottlenecks.append("Low throughput relative to concurrency")
             suggestions.append("Check for contention in task queue or worker pool.")

        if not bottlenecks:
            suggestions.append("System is performing well under current load configuration.")

        return StressReport(
            config=config,
            result=result,
            bottlenecks=bottlenecks,
            optimization_suggestions=suggestions,
            stability_rating=stability
        )
