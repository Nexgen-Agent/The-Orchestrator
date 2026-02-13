import json
import os
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from agents.shooting_star_intelligence.models import (
    IntelligenceSource, InnovationOpportunity, CapabilityProgress, IntelligenceReport, SystemReadiness
)
from fog.core.state import state_store
from fog.core.logging import logger
from agents.sandbox_simulation.simulator import SandboxSimulator, SimulationConfig
from agents.meta_agent_trainer.engine import MetaAgentTrainerEngine

class ShootingStarIntelligence:
    def __init__(self, data_path: str = "storage/shooting_star_readiness.json"):
        self.data_path = data_path
        self.simulator = SandboxSimulator()
        self.mate = MetaAgentTrainerEngine()
        self._load_readiness()

    def _load_readiness(self):
        if os.path.exists(self.data_path):
            try:
                with open(self.data_path, "r") as f:
                    data = json.load(f)
                    self.readiness = SystemReadiness(**data)
            except Exception:
                self.readiness = SystemReadiness(overall_readiness=0.0)
        else:
            self.readiness = SystemReadiness(overall_readiness=0.0)

    def _save_readiness(self):
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        with open(self.data_path, "w") as f:
            json.dump(self.readiness.model_dump(mode='json'), f, indent=4)

    async def gather_intelligence(self, topic: str) -> List[IntelligenceSource]:
        """
        Simulates gathering actionable intelligence from public sources.
        """
        logger.info("GATHERING_INTELLIGENCE", {"topic": topic})
        # Mock intelligence sources
        sources = [
            IntelligenceSource(
                source_url=f"https://github.com/topics/{topic}",
                reliability_score=0.85,
                topic_tags=[topic, "open-source"],
                solution_type="library"
            ),
            IntelligenceSource(
                source_url=f"https://stackoverflow.com/questions/tagged/{topic}",
                reliability_score=0.9,
                topic_tags=[topic, "troubleshooting"],
                solution_type="fix"
            )
        ]
        return sources

    async def track_progress(self, agent_name: str, current_capability: float) -> CapabilityProgress:
        """
        Updates and tracks progress for a specific agent/module.
        """
        # Calculate deployment readiness probability based on capability %
        # Threshold for 'ready' is usually 98-99%
        deployment_prob = min(1.0, current_capability / 98.0)

        progress = CapabilityProgress(
            agent_name=agent_name,
            version="1.1.0",
            capability_percentage=current_capability,
            deployment_probability=deployment_prob
        )

        # Update system-wide readiness
        updated = False
        for i, p in enumerate(self.readiness.module_progress):
            if p.agent_name == agent_name:
                self.readiness.module_progress[i] = progress
                updated = True
                break
        if not updated:
            self.readiness.module_progress.append(progress)

        self._calculate_overall_readiness()
        self._save_readiness()

        return progress

    def _calculate_overall_readiness(self):
        if not self.readiness.module_progress:
            self.readiness.overall_readiness = 0.0
            return

        total_cap = sum(p.capability_percentage for p in self.readiness.module_progress)
        self.readiness.overall_readiness = total_cap / len(self.readiness.module_progress)

    async def perform_readiness_audit(self, agent_name: str, project_path: str) -> IntelligenceReport:
        """
        Performs a full audit including simulation, intelligence gathering, and innovation assessment.
        """
        # 1. Get current progress
        current_p = next((p for p in self.readiness.module_progress if p.agent_name == agent_name), None)
        cap = current_p.capability_percentage if current_p else 50.0
        prob = current_p.deployment_probability if current_p else 0.5

        # 2. Gather Intelligence
        intel = await self.gather_intelligence(agent_name)

        # 3. Simulate Readiness
        sim_config = SimulationConfig(
            project_path=project_path,
            task_description=f"Readiness audit for {agent_name}. Capability: {cap}%",
            isolated_run=True
        )
        sim_report = await asyncio.to_thread(self.simulator.simulate, sim_config)

        # 4. Assess Innovation Opportunities
        innovations = [
            InnovationOpportunity(
                title="Parallel Task Execution",
                description="Leverage async loops for higher throughput.",
                impact_score=0.8,
                feasibility_score=0.9
            )
        ]

        report = IntelligenceReport(
            agent_name=agent_name,
            version="1.1.0",
            capability_percentage=cap,
            deployment_probability=prob,
            innovation_opportunities=innovations,
            optimization_actions=["Refactor core loop", "Add telemetry"],
            learning_sources=intel,
            status="ready" if cap >= 98.0 else "not_ready",
            notes=f"Simulation verdict: {sim_report.verdict}. {sim_report.summary}"
        )

        logger.info("READINESS_AUDIT_COMPLETED", {"agent": agent_name, "status": report.status})
        return report

    async def autonomous_evolution_cycle(self, agent_name: str, project_path: str):
        """
        Feeds intelligence into FOG MATE to trigger an evolution cycle.
        """
        intel = await self.gather_intelligence(agent_name)
        logger.info("TRIGGERING_MATE_EVOLUTION", {"agent": agent_name, "sources": len(intel)})

        # Call MATE to train based on intel (simulated interaction)
        # report = await self.mate.simulate_training(agent_name, project_path)

        # After MATE cycle, we would update our tracking
        await self.track_progress(agent_name, 75.0) # Mock improvement

    async def get_training_recommendations(self) -> List[Dict[str, Any]]:
        """
        Provides links and instructions for training the FOG ecosystem faster.
        """
        return [
            {
                "title": "Hugging Face Transformers",
                "description": "Integrate state-of-the-art NLP models to improve intent detection and conversational depth.",
                "url": "https://huggingface.co/docs/transformers/index"
            },
            {
                "title": "LangChain Framework",
                "description": "Use LangChain to orchestrate complex multi-agent chains and memory management.",
                "url": "https://python.langchain.com/docs/get_started/introduction"
            },
            {
                "title": "AutoGPT & BabyAGI Patterns",
                "description": "Study autonomous agent loops to implement better self-correction in the Friction Solver.",
                "url": "https://github.com/Significant-Gravitas/Auto-GPT"
            },
            {
                "title": "OpenAI Function Calling",
                "description": "Learn how to better map natural language to tool execution for the External Tool Interface.",
                "url": "https://platform.openai.com/docs/guides/function-calling"
            }
        ]
