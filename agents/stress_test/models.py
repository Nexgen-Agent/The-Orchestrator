from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

class StressTestConfig(BaseModel):
    num_tasks: int = Field(default=10, description="Number of tasks to simulate")
    concurrency: int = Field(default=5, description="Number of concurrent tasks")
    task_type: str = Field(default="analysis", description="Type of task to simulate")
    payload_size_kb: int = Field(default=1, description="Size of dummy payload in KB")

class PerformanceMetric(BaseModel):
    task_id: str
    duration_ms: float
    status: str
    error: Optional[str] = None

class StressResult(BaseModel):
    total_tasks: int
    successful_tasks: int
    failed_tasks: int
    average_latency_ms: float
    p95_latency_ms: float
    throughput_tps: float
    start_time: datetime
    end_time: datetime
    metrics: List[PerformanceMetric]

class StressReport(BaseModel):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    config: StressTestConfig
    result: StressResult
    bottlenecks: List[str]
    optimization_suggestions: List[str]
    stability_rating: str # e.g. "Stable", "Degraded", "Unstable"
