import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from agents.orchestration_optimizer.models import (
    AgentPerformance, FailurePattern, OptimizationSuggestion, OptimizationReport
)

class OrchestrationOptimizer:
    def __init__(self, log_file_path: str = "storage/audit.log"):
        self.log_file_path = log_file_path

    def analyze(self) -> OptimizationReport:
        logs = self._parse_logs()

        # task_id -> {start_time, end_time, agent, status, error}
        task_data = self._process_logs(logs)

        # agent_name -> [durations]
        agent_durations = {}
        agent_success_count = {}
        agent_fail_count = {}
        failure_reasons = {} # error -> [agents, task_ids]

        for tid, data in task_data.items():
            agent = data.get("agent")
            if not agent: continue

            start = data.get("start")
            end = data.get("end")
            status = data.get("status")

            if start and end:
                duration = (end - start).total_seconds()
                agent_durations.setdefault(agent, []).append(duration)

            if status == "completed":
                agent_success_count[agent] = agent_success_count.get(agent, 0) + 1
            elif status == "failed":
                agent_fail_count[agent] = agent_fail_count.get(agent, 0) + 1
                error = data.get("error", "Unknown Error")
                failure_reasons.setdefault(error, {"agents": set(), "tids": []})
                failure_reasons[error]["agents"].add(agent)
                failure_reasons[error]["tids"].append(tid)

        # 1. Agent Performance
        perf_list = []
        for agent in set(list(agent_durations.keys()) + list(agent_success_count.keys()) + list(agent_fail_count.keys())):
            durations = agent_durations.get(agent, [0])
            success = agent_success_count.get(agent, 0)
            fail = agent_fail_count.get(agent, 0)
            total = success + fail

            perf_list.append(AgentPerformance(
                agent_name=agent,
                avg_execution_time_seconds=sum(durations) / len(durations) if durations else 0,
                max_execution_time_seconds=max(durations) if durations else 0,
                total_tasks_handled=total,
                success_rate=success / total if total > 0 else 1.0
            ))

        # 2. Failure Patterns
        patterns = []
        for error, info in failure_reasons.items():
            patterns.append(FailurePattern(
                error_type=error,
                occurrence_count=len(info["tids"]),
                affected_agents=list(info["agents"]),
                sample_task_ids=info["tids"][:5]
            ))

        # 3. Optimization Suggestions
        suggestions = self._generate_suggestions(perf_list, patterns)

        # 4. Overall Efficiency Score (arbitrary logic)
        score = 100
        if perf_list:
            avg_success = sum(a.success_rate for a in perf_list) / len(perf_list)
            score = int(avg_success * 100)

        return OptimizationReport(
            agent_performance=perf_list,
            failure_patterns=patterns,
            suggestions=suggestions,
            overall_efficiency_score=score
        )

    def _parse_logs(self) -> List[Dict[str, Any]]:
        logs = []
        if not os.path.exists(self.log_file_path):
            return []

        with open(self.log_file_path, "r") as f:
            for line in f:
                try:
                    # Logs are structured JSON per line
                    logs.append(json.loads(line))
                except Exception:
                    continue
        return logs

    def _process_logs(self, logs: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        task_data = {}
        for entry in logs:
            event = entry.get("event")
            data = entry.get("data", {})
            tid = data.get("task_id")
            ts = datetime.fromisoformat(entry.get("timestamp"))

            if not tid: continue

            if tid not in task_data:
                task_data[tid] = {}

            if event == "PROCESSING_TASK":
                task_data[tid]["start"] = ts
                task_data[tid]["agent"] = data.get("agent")
            elif event == "TASK_FINISHED":
                task_data[tid]["end"] = ts
                task_data[tid]["status"] = data.get("status")
            elif event == "TASK_COMPLETED_MOCK":
                # Some events might redundant or more specific
                task_data[tid]["status"] = "completed"
            elif event == "TASK_MAX_RETRIES_REACHED":
                task_data[tid]["status"] = "failed"
                task_data[tid]["error"] = data.get("error")

        return task_data

    def _generate_suggestions(self, perfs: List[AgentPerformance], patterns: List[FailurePattern]) -> List[OptimizationSuggestion]:
        suggestions = []

        # Detect slow agents
        if perfs:
            avg_all = sum(p.avg_execution_time_seconds for p in perfs) / len(perfs)
            for p in perfs:
                if p.avg_execution_time_seconds > avg_all * 1.5:
                    suggestions.append(OptimizationSuggestion(
                        type="Agent",
                        target=p.agent_name,
                        reason=f"Average execution time ({p.avg_execution_time_seconds:.2f}s) is significantly higher than system average ({avg_all:.2f}s).",
                        recommendation="Consider optimizing the agent logic or increasing its resource allocation."
                    ))

        # Detect high failure rates
        for p in perfs:
            if p.success_rate < 0.8 and p.total_tasks_handled > 2:
                suggestions.append(OptimizationSuggestion(
                    type="Retries",
                    target=p.agent_name,
                    reason=f"High failure rate ({ (1-p.success_rate)*100 :.1f}%) detected.",
                    recommendation="Review the error patterns and consider increasing the maximum retries for this agent."
                ))

        # Timeout suggestion
        for p in perfs:
            if p.max_execution_time_seconds > 200: # Near current 300s timeout
                suggestions.append(OptimizationSuggestion(
                    type="Timeout",
                    target=p.agent_name,
                    reason=f"Max execution time ({p.max_execution_time_seconds:.2f}s) is close to the system timeout.",
                    recommendation="Consider increasing the orchestration timeout for this agent to avoid unnecessary failures."
                ))

        return suggestions
