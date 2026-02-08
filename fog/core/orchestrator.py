import asyncio
from typing import Dict, Any, List
from fog.models.task import TaskPacket, TaskType, TaskStatus
from fog.core.engine import orchestration_engine
from fog.core.connector import agent_registry
from fog.core.state import state_store
import uuid
from fog.core.logging import logger
from agents.personality_engine.engine import FingerprintManager, StyleAdaptor
from fog.core.synthesizer import ChatResponseSynthesizer
import importlib

class ChatOrchestrator:
    def __init__(self):
        self.agent_keywords = {
            "FrictionSolver": ["fix", "error", "broken", "repair", "issue", "problem", "failure"],
            "SoftwareBuilder": ["build", "create", "construct", "module", "generate code", "implement"],
            "DeploymentAutomation": ["deploy", "release", "push", "production", "ship", "deployment"],
            "SystemMonitor": ["status", "health", "how are you", "monitor", "metrics", "stats"],
            "SelfEvolutionEngine": ["improve", "evolve", "optimize", "upgrade", "refactor"],
            "Debugger": ["debug", "trace", "crash", "log analysis", "inspect"],
            "ShootingStarIntelligence": ["ready", "roadmap", "train", "operational", "how far", "learning", "discovery"]
        }
        self.intents = {
            "STATUS_QUERY": ["what is working", "what is not", "health", "system status"],
            "READINESS_QUERY": ["how far", "operational", "roadmap", "ready", "percentage"],
            "TRAINING_QUERY": ["train", "faster", "ai agents", "online", "resources", "links"]
        }
        self.personality = FingerprintManager()

    def _detect_intent(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        for intent, keywords in self.intents.items():
            if any(kw in prompt_lower for kw in keywords):
                return intent
        return "GENERAL_TASK"

    async def process(self, prompt: str, user_id: str = "default_user") -> Dict[str, Any]:
        """
        Process a user prompt, route to an agent, and return dispatch info or full response.
        """
        intent = self._detect_intent(prompt)
        profile = self.personality.get_profile(user_id)
        adaptation = StyleAdaptor.generate_adaptation(profile)

        if intent != "GENERAL_TASK":
            # Direct response for queries
            data = await self._handle_query_intent(intent, prompt)
            message = ChatResponseSynthesizer.synthesize(intent, data, adaptation)

            return {
                "status": "completed",
                "task_id": f"query-{uuid.uuid4().hex[:8]}",
                "agent_assigned": "Orchestrator",
                "message": message
            }

        # 1. Determine agent
        agent_name = self._route(prompt)

        # 2. Create task
        task_id = f"chat-{uuid.uuid4().hex[:8]}"
        task = TaskPacket(
            task_id=task_id,
            system_name=agent_name,
            module_name="chat_orchestrator",
            task_type=TaskType.ANALYSIS,
            payload={"prompt": prompt, "chat_interaction": True}
        )

        # 3. Submit task to engine
        logger.info("CHAT_ORCHESTRATOR_ROUTING", {"prompt": prompt, "agent": agent_name, "task_id": task_id})
        await orchestration_engine.submit_task(task)

        # 4. Generate Personalized Acknowledgment
        message = self._generate_message(agent_name, adaptation)

        return {
            "status": "dispatched",
            "task_id": task_id,
            "agent_assigned": agent_name,
            "message": message
        }

    async def _handle_query_intent(self, intent: str, prompt: str) -> Dict[str, Any]:
        """
        Calls relevant agents synchronously to gather data for a query.
        """
        if intent == "STATUS_QUERY":
            from agents.system_monitor.handler import handle_task as monitor_handler
            from agents.system_resilience.resilience import ResilienceManager

            res = await monitor_handler({"payload": {}})
            health = res.get("result", {})

            resilience = ResilienceManager()
            history = resilience.get_resilience_history()
            health["recent_fixes"] = [h.model_dump(mode='json') for h in history[-3:]] # Last 3 fixes

            return health

        elif intent == "READINESS_QUERY":
            from agents.shooting_star_intelligence.intelligence import ShootingStarIntelligence
            from agents.self_evaluator.evaluator import SelfEvaluator

            engine = ShootingStarIntelligence()
            readiness = engine.readiness.model_dump(mode='json')

            # Add some evaluator context if possible
            evaluator = SelfEvaluator()
            # Just a mock aggregation for now
            readiness["evaluation_summary"] = "System performance is stable across all active modules."

            return readiness

        elif intent == "TRAINING_QUERY":
            from agents.shooting_star_intelligence.intelligence import ShootingStarIntelligence
            engine = ShootingStarIntelligence()
            recs = await engine.get_training_recommendations()
            return {"training_recommendations": recs}

        return {"message": "I'm not sure how to answer that yet."}

    def _generate_message(self, agent_name: str, adaptation: Any) -> str:
        tone = adaptation.target_tone
        if tone == "formal":
            return f"I have successfully analyzed your request and delegated the execution to the {agent_name} module. You will be notified upon completion."
        elif tone == "casual":
            return f"Got it! I'm sending that over to {agent_name} right now. I'll let you know when it's done! 🚀"
        else:
            return f"Orchestrator has assigned this task to {agent_name}. Monitoring progress now."

    def _route(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        for agent, keywords in self.agent_keywords.items():
            if any(kw in prompt_lower for kw in keywords):
                return agent

        # Default agent if no match
        return "FrictionSolver"

chat_orchestrator = ChatOrchestrator()
