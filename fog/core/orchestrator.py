import asyncio
from typing import Dict, Any, List
from fog.models.task import TaskPacket, TaskType, TaskStatus
from fog.core.engine import orchestration_engine
from fog.core.connector import agent_registry
from fog.core.state import state_store
import uuid
from fog.core.logging import logger
from agents.personality_engine.engine import FingerprintManager, StyleAdaptor

class ChatOrchestrator:
    def __init__(self):
        self.agent_keywords = {
            "FrictionSolver": ["fix", "error", "broken", "repair", "issue", "problem", "failure"],
            "SoftwareBuilder": ["build", "create", "construct", "module", "generate code", "implement"],
            "DeploymentAutomation": ["deploy", "release", "push", "production", "ship", "deployment"],
            "SystemMonitor": ["status", "health", "how are you", "monitor", "metrics", "stats"],
            "SelfEvolutionEngine": ["improve", "evolve", "optimize", "upgrade", "refactor"],
            "Debugger": ["debug", "trace", "crash", "log analysis", "inspect"]
        }
        self.personality = FingerprintManager()

    async def process(self, prompt: str, user_id: str = "default_user") -> Dict[str, Any]:
        """
        Process a user prompt, route to an agent, and return dispatch info.
        """
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
        profile = self.personality.get_profile(user_id)
        adaptation = StyleAdaptor.generate_adaptation(profile)

        message = self._generate_message(agent_name, adaptation)

        return {
            "status": "dispatched",
            "task_id": task_id,
            "agent_assigned": agent_name,
            "message": message
        }

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
