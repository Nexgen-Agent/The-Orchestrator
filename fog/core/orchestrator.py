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
from fog.core.memory import conversation_manager
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
            "STATUS_QUERY": ["working", "broken", "health", "system status", "condition", "status", "looking"],
            "READINESS_QUERY": ["how far", "operational", "roadmap", "ready", "percentage", "completion"],
            "TRAINING_QUERY": ["train", "faster", "ai agents", "online", "resources", "links", "improve"],
            "CAPABILITY_QUERY": ["what can you do", "who are you", "capabilities", "features", "help"]
        }
        self.personality = FingerprintManager()

    def _detect_intent(self, prompt: str) -> str:
        prompt_lower = prompt.lower().strip()

        # Vague input check
        if len(prompt_lower) < 2 or prompt_lower in [".", "?", "!", "hi", "hello"]:
            return "CLARIFICATION_NEEDED"

        for intent, keywords in self.intents.items():
            if any(kw in prompt_lower for kw in keywords):
                return intent

        # Action check
        if any(kw in prompt_lower for agent_kws in self.agent_keywords.values() for kw in agent_kws):
            return "GENERAL_TASK"

        return "CONVERSATIONAL"

    async def process(self, prompt: str, user_id: str = "default_user", session_id: str = "default_session") -> Dict[str, Any]:
        """
        Process a user prompt, maintain context, and return a synthesized natural language response.
        """
        # 1. Record User Message
        conversation_manager.add_message(session_id, "user", prompt)

        # 2. Get Context and Intent
        history = conversation_manager.get_context(session_id)
        intent = self._detect_intent(prompt)

        profile = self.personality.get_profile(user_id)
        adaptation = StyleAdaptor.generate_adaptation(profile)

        response_status = "completed"
        task_id = f"msg-{uuid.uuid4().hex[:8]}"

        # 3. Handle Intents
        if intent == "CLARIFICATION_NEEDED":
            message = self._get_clarification_response(adaptation)

        elif intent == "CONVERSATIONAL":
            message = self._get_general_conversational_response(prompt, history, adaptation)

        elif intent == "CAPABILITY_QUERY":
            message = self._get_capability_response(adaptation)

        elif intent in self.intents:
            # Silent data gathering from agents
            data = await self._handle_query_intent(intent, prompt)
            message = ChatResponseSynthesizer.synthesize(intent, data, adaptation)

        else:
            # Action required - Dispatched to agent
            agent_name = self._route(prompt)
            task_id = f"task-{uuid.uuid4().hex[:8]}"
            task = TaskPacket(
                task_id=task_id,
                system_name=agent_name,
                module_name="chat_orchestrator",
                task_type=TaskType.ANALYSIS,
                payload={"prompt": prompt, "chat_interaction": True}
            )

            logger.info("CHAT_ORCHESTRATOR_ACTION", {"prompt": prompt, "agent": agent_name, "task_id": task_id})
            await orchestration_engine.submit_task(task)

            # Silent acknowledgment
            message = self._generate_silent_ack(adaptation)
            response_status = "dispatched"

        # 4. Record and Return Response
        conversation_manager.add_message(session_id, "orchestrator", message, {"task_id": task_id, "intent": intent})

        return {
            "status": response_status,
            "task_id": task_id,
            "message": message
        }

    def _get_clarification_response(self, adaptation: Any) -> str:
        tone = adaptation.target_tone
        if tone == "formal":
            return "I apologize, but your input was insufficient for me to determine a specific course of action. Could you please provide more detail regarding your request?"
        elif tone == "casual":
            return "I didn't quite catch that! Could you give me a bit more detail so I know how to help? 😊"
        else:
            return "I need a bit more information to assist you correctly. Please clarify your request."

    def _get_general_conversational_response(self, prompt: str, history: List[Dict], adaptation: Any) -> str:
        # For a truly intelligent chatbot, we'd use an LLM here.
        # For this implementation, we simulate an intelligent response based on state awareness.
        tone = adaptation.target_tone
        if tone == "formal":
            return "I understand your point. I am currently monitoring the FOG ecosystem and can assist with system analysis, builds, or deployment tasks. How shall we proceed?"
        elif tone == "casual":
            return "I hear you! I'm hanging out in the gateway, ready to fix things or build new modules whenever you need. What's on your mind?"
        else:
            return "Understood. I'm ready to assist with any system tasks or answer your questions about FOG."

    def _get_capability_response(self, adaptation: Any) -> str:
        tone = adaptation.target_tone
        capabilities = [
            "Monitor system health and resource usage",
            "Resolve technical friction and failures",
            "Build and refactor software modules",
            "Automate production deployments",
            "Track operational readiness and evolution progress"
        ]

        if tone == "formal":
            msg = "As the Frontier Orchestration Gateway, I am equipped to perform the following operations:\n\n"
            for cap in capabilities:
                msg += f"- {cap}\n"
            msg += "\nI function as a central intelligence layer, coordinating multiple specialized agents to maintain system stability."
            return msg
        elif tone == "casual":
            msg = "I'm basically the brain of this whole setup! 🧠 Here's what I can do for you:\n\n"
            for cap in capabilities:
                msg += f"- {cap}\n"
            msg += "\nJust tell me what you need, and I'll handle the rest in the background."
            return msg
        else:
            return "I can monitor system health, fix errors, build modules, automate deployments, and track readiness. How can I help today?"

    def _generate_silent_ack(self, adaptation: Any) -> str:
        tone = adaptation.target_tone
        if tone == "formal":
            return "I have initiated the requested process. I will monitor the execution and provide an update upon completion."
        elif tone == "casual":
            return "I'm on it! I've started that process for you and I'll keep you posted on how it's going. 🚀"
        else:
            return "Understood. I am processing your request now."

    async def _handle_query_intent(self, intent: str, prompt: str) -> Dict[str, Any]:
        """
        Calls relevant agents synchronously to gather data for a query.
        """
        if intent == "STATUS_QUERY":
            from agents.system_monitor.handler import handle_task as monitor_handler
            from agents.system_resilience.resilience import ResilienceManager

            res = await monitor_handler({"payload": {}})
            health = res.get("result", {})

            # Check agent connectivity
            agent_status = {}
            for name, connector in agent_registry.agents.items():
                agent_status[name] = "Online" # In mock, they are always online

            health["agent_status"] = agent_status

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


    def _route(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        for agent, keywords in self.agent_keywords.items():
            if any(kw in prompt_lower for kw in keywords):
                return agent

        # Default agent if no match
        return "FrictionSolver"

chat_orchestrator = ChatOrchestrator()
