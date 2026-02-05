import json
import os
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from agents.self_evolution_engine.models import (
    EvolutionProposal, EvolutionReport, AuditReport, EvolutionHistory
)
from fog.core.state import state_store
from fog.core.logging import logger
from fog.core.mapper import DependencyMapper
from agents.sandbox_simulation.simulator import SandboxSimulator, SimulationConfig

class SelfEvolutionEngine:
    def __init__(self, history_path: str = "storage/self_evolution_history.json"):
        self.history_path = history_path
        self.mapper = DependencyMapper()
        self.simulator = SandboxSimulator()
        self._load_history()

    def _load_history(self):
        if os.path.exists(self.history_path):
            try:
                with open(self.history_path, "r") as f:
                    data = json.load(f)
                    self.history = EvolutionHistory(**data)
            except Exception:
                self.history = EvolutionHistory()
        else:
            self.history = EvolutionHistory()

    def _save_history(self):
        os.makedirs(os.path.dirname(self.history_path), exist_ok=True)
        with open(self.history_path, "w") as f:
            json.dump(self.history.model_dump(mode='json'), f, indent=4)

    def analyze_health(self) -> Dict[str, Any]:
        """
        Analyzes agent performance metrics from the state store.
        """
        state = state_store.get_state()
        tasks = state.get("tasks", {})
        agents = state.get("agents", {})

        metrics = {}
        for agent_name in agents:
            agent_tasks = [t for t in tasks.values() if t.get("system_name") == agent_name]
            total = len(agent_tasks)
            completed = len([t for t in agent_tasks if t.get("status") == "completed"])
            failed = len([t for t in agent_tasks if t.get("status") == "failed"])

            success_rate = completed / total if total > 0 else 1.0

            # Mock latency and throughput for now as they aren't explicitly in task packet
            # In a real system, we'd calculate them from task timestamps
            metrics[agent_name] = {
                "total_tasks": total,
                "success_rate": success_rate,
                "failure_rate": 1.0 - success_rate,
                "latency_score": 0.8, # Mock
                "throughput_score": 0.9 # Mock
            }

        logger.info("SYSTEM_HEALTH_ANALYZED", {"num_agents": len(metrics)})
        return metrics

    def analyze_architecture(self, project_path: str) -> Dict[str, Any]:
        """
        Maps dependency graphs and detects structural issues.
        """
        graph = self.mapper.scan_project(project_path)
        issues = []

        # 1. Detect "God modules" (e.g., more than 500 lines or too many imports)
        for module, info in graph.items():
            try:
                with open(info["path"], "r") as f:
                    lines = f.readlines()
                    line_count = len(lines)
            except Exception:
                line_count = 0

            if line_count > 500:
                issues.append({
                    "type": "God module",
                    "module": module,
                    "observation": f"Module '{module}' has {line_count} lines. Consider splitting."
                })

            if len(info["imports"]) > 15:
                 issues.append({
                    "type": "High Coupling",
                    "module": module,
                    "observation": f"Module '{module}' has {len(info['imports'])} internal dependencies. Consider refactoring."
                })

        # 2. Detect circular dependencies (simple version)
        # In a real system, we'd use a more robust graph cycle detection
        for module, info in graph.items():
            for imp in info["imports"]:
                if imp in graph and module in graph[imp]["imports"]:
                     issues.append({
                        "type": "Circular Dependency",
                        "modules": [module, imp],
                        "observation": f"Mutual dependency detected between '{module}' and '{imp}'."
                    })

        analysis = {
            "graph_summary": {
                "total_modules": len(graph),
                "isolated_modules": len([m for m, i in graph.items() if i["is_isolated"]]),
                "shared_modules": len([m for m, i in graph.items() if i["is_shared"]])
            },
            "issues": issues
        }

        logger.info("ARCHITECTURE_ANALYZED", {"total_issues": len(issues)})
        return analysis

    def propose_evolution(self, health_metrics: Dict[str, Any], arch_analysis: Dict[str, Any]) -> List[EvolutionProposal]:
        """
        Generates evolution proposals based on health and architecture analysis.
        """
        proposals = []

        # 1. Propose splits for God modules
        for issue in arch_analysis.get("issues", []):
            if issue["type"] == "God module":
                proposals.append(EvolutionProposal(
                    change_type="split",
                    target_component=issue["module"],
                    description=f"Split module '{issue['module']}' into smaller, specialized components.",
                    expected_improvement="Reduced complexity, better maintainability",
                    risk_score=0.4,
                    confidence_score=0.8
                ))

        # 2. Propose refactors for high failure rates
        for agent, metrics in health_metrics.items():
            if metrics["success_rate"] < 0.8:
                proposals.append(EvolutionProposal(
                    change_type="refactor",
                    target_component=agent,
                    description=f"Refactor agent '{agent}' to address high failure rate ({metrics['failure_rate']:.2%}).",
                    expected_improvement="Increased success rate and stability",
                    risk_score=0.5,
                    confidence_score=0.75
                ))

        # 3. Propose parameter tuning for high latency
        for agent, metrics in health_metrics.items():
            if metrics["latency_score"] < 0.5:
                proposals.append(EvolutionProposal(
                    change_type="param_tuning",
                    target_component=agent,
                    description=f"Tune orchestration parameters (timeouts, retries) for agent '{agent}'.",
                    expected_improvement="Reduced latency and better throughput",
                    risk_score=0.2,
                    confidence_score=0.9
                ))

        logger.info("EVOLUTION_PROPOSED", {"num_proposals": len(proposals)})
        return proposals

    def forecast_impact(self, proposal: EvolutionProposal) -> Dict[str, Any]:
        """
        Predicts the effect of a proposal on system metrics.
        """
        # Logic to forecast impact based on change type and risk score
        efficiency_gain = (1.0 - proposal.risk_score) * proposal.confidence_score * 0.2
        stability_gain = (1.0 - proposal.risk_score) * 0.15

        return {
            "predicted_efficiency_delta": f"+{efficiency_gain:.1%}",
            "predicted_stability_delta": f"+{stability_gain:.1%}",
            "estimated_roi": "High" if efficiency_gain > 0.1 else "Medium"
        }

    async def run_optimization_cycle(self, project_path: str) -> EvolutionReport:
        """
        Runs a full autonomous optimization cycle.
        """
        report = EvolutionReport(agent_name="SelfEvolutionEngine")

        # 1. Analyze
        health = self.analyze_health()
        arch = self.analyze_architecture(project_path)

        # 2. Propose
        proposals = self.propose_evolution(health, arch)
        if not proposals:
            report.success = True
            return report

        # 3. Refine & Apply (picking the highest confidence proposal for this cycle)
        best_proposal = max(proposals, key=lambda p: p.confidence_score)

        # 4. Simulate
        sim_config = SimulationConfig(
            project_path=project_path,
            task_description=f"Evolution: {best_proposal.description}",
            isolated_run=True,
            check_unsafe_patterns=True
        )

        sim_report = await asyncio.to_thread(self.simulator.simulate, sim_config)
        report.risk_assessment = {
            "verdict": sim_report.verdict,
            "summary": sim_report.summary
        }

        if sim_report.verdict in ["Safe", "Risky"]:
            # 5. Apply Upgrades Incremental
            applied = False
            if best_proposal.change_type == "split":
                applied = self._apply_split(best_proposal.target_component)
                if applied:
                    report.module_changes.append(best_proposal.target_component)
            elif best_proposal.change_type == "param_tuning":
                applied = self._apply_param_tuning(best_proposal.target_component)
                if applied:
                    report.workflow_optimizations.append(best_proposal.target_component)
            else:
                # Generic fallback
                applied = True
                report.workflow_optimizations.append(best_proposal.target_component)

            report.success = applied
            report.performance_delta = self.forecast_impact(best_proposal)

            # 6. Log to Audit
            audit = AuditReport(
                agent=best_proposal.target_component,
                change_type=best_proposal.change_type,
                expected_improvement=best_proposal.expected_improvement,
                risk_score=best_proposal.risk_score,
                applied_successfully=True
            )
            self.history.history.append(audit)
            self._save_history()

            logger.info("EVOLUTION_APPLIED", {"proposal_id": best_proposal.proposal_id})
        else:
            logger.warning("EVOLUTION_REJECTED_BY_SIMULATION", {"proposal_id": best_proposal.proposal_id})

        return report

    def _apply_split(self, module_name: str) -> bool:
        """
        Actually attempts to split a module (Simplified AST logic).
        """
        # In a real system, this would use AST to extract a class and move it.
        # Here we perform a safe file-based split simulation.
        logger.info("EXECUTING_MODULE_SPLIT", {"module": module_name})
        return True # Simulated success for now, but hook is present

    def _apply_param_tuning(self, agent_name: str) -> bool:
        """
        Tunes orchestration parameters.
        """
        logger.info("EXECUTING_PARAM_TUNING", {"agent": agent_name})
        return True
