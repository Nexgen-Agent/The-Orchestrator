from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from agents.system_monitor.models import AgentHealth, TaskMetrics, FailurePattern, SystemHealthReport

class SystemMonitor:
    def __init__(self, state_store: Any):
        self.state_store = state_store

    def get_health_report(self) -> SystemHealthReport:
        state = self.state_store.get_state()

        # 1. Analyze Agents
        agents_health = self._analyze_agents(state.get("agents", {}))

        # 2. Analyze Tasks
        task_metrics = self._analyze_tasks(state.get("tasks", {}))

        # 3. Detect Patterns
        patterns = self._detect_failure_patterns(state.get("tasks", {}))

        # 4. Determine overall status
        system_status = "Nominal"
        if task_metrics.success_rate < 0.5 or any(a.status == "Unhealthy" for a in agents_health):
            system_status = "Critical"
        elif task_metrics.success_rate < 0.8:
            system_status = "Degraded"

        return SystemHealthReport(
            agents=agents_health,
            overall_task_metrics=task_metrics,
            detected_patterns=patterns,
            system_status=system_status
        )

    def _analyze_agents(self, agents_data: Dict[str, Any]) -> List[AgentHealth]:
        health_list = []
        for name, config in agents_data.items():
            # In a real system, we'd check last heartbeat or ping the endpoint
            # Here we just assume they are healthy if registered
            health_list.append(AgentHealth(
                name=name,
                status="Healthy",
                uptime_seconds=3600.0 # Mock uptime
            ))
        return health_list

    def _analyze_tasks(self, tasks_data: Dict[str, Any]) -> TaskMetrics:
        total = len(tasks_data)
        if total == 0:
            return TaskMetrics(total_tasks=0, completed_tasks=0, failed_tasks=0, success_rate=1.0, average_retries=0.0)

        completed = len([t for t in tasks_data.values() if t.get("status") == "completed"])
        failed = len([t for t in tasks_data.values() if t.get("status") == "failed"])

        retries = [t.get("retries", 0) for t in tasks_data.values()]
        avg_retries = sum(retries) / total if total > 0 else 0

        success_rate = completed / (completed + failed) if (completed + failed) > 0 else 1.0

        return TaskMetrics(
            total_tasks=total,
            completed_tasks=completed,
            failed_tasks=failed,
            success_rate=success_rate,
            average_retries=avg_retries
        )

    def _detect_failure_patterns(self, tasks_data: Dict[str, Any]) -> List[FailurePattern]:
        patterns = []

        # Check for agents with high failure rates
        agent_failures = {}
        agent_successes = {}

        for task in tasks_data.values():
            agent = task.get("system_name")
            status = task.get("status")
            if status == "failed":
                agent_failures[agent] = agent_failures.get(agent, 0) + 1
            elif status == "completed":
                agent_successes[agent] = agent_successes.get(agent, 0) + 1

        for agent, failures in agent_failures.items():
            successes = agent_successes.get(agent, 0)
            if failures > 3 and failures > successes:
                patterns.append(FailurePattern(
                    pattern_type="Agent Instability",
                    description=f"Agent '{agent}' has a high failure count ({failures}) compared to successes ({successes}).",
                    affected_components=[agent],
                    occurrence_count=failures
                ))

        return patterns
