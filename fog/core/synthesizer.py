from typing import Dict, Any, List
import json

class ChatResponseSynthesizer:
    @staticmethod
    def synthesize(intent: str, data: Dict[str, Any], adaptation: Any) -> str:
        """
        Synthesize a natural language response from agent data.
        """
        tone = adaptation.target_tone

        if intent == "STATUS_QUERY":
            return ChatResponseSynthesizer._format_status(data, tone)
        elif intent == "READINESS_QUERY":
            return ChatResponseSynthesizer._format_readiness(data, tone)
        elif intent == "TRAINING_QUERY":
            return ChatResponseSynthesizer._format_training(data, tone)
        else:
            return ChatResponseSynthesizer._format_general(data, tone)

    @staticmethod
    def _format_status(data: Dict[str, Any], tone: str) -> str:
        status = data.get("system_status", "Unknown")
        cpu = data.get("resource_usage", {}).get("cpu_percent", 0)
        mem = data.get("resource_usage", {}).get("memory_percent", 0)
        agents = data.get("agents_online", 0)

        if tone == "casual":
            msg = f"Systems are looking {status.lower()} right now! 🟢\n\n"
            msg += f"- **CPU**: {cpu}%\n"
            msg += f"- **Memory**: {mem}%\n"
            msg += f"- **Agents Online**: {agents}\n\n"
            msg += "Everything's running smooth. What's next on the list?"
            return msg
        else:
            msg = f"The current system status is **{status}**.\n\n"
            msg += f"**Resource Metrics:**\n"
            msg += f"- Processor Load: {cpu}%\n"
            msg += f"- Memory Utilization: {mem}%\n"
            msg += f"- Active Agent Handlers: {agents}\n\n"
            msg += "The orchestration engine is operating within nominal parameters."
            return msg

    @staticmethod
    def _format_readiness(data: Dict[str, Any], tone: str) -> str:
        readiness = data.get("overall_readiness", 0.0) * 100
        modules = data.get("module_progress", [])

        if tone == "casual":
            msg = f"We're about **{readiness:.1f}%** of the way to full operational glory! 🚀\n\n"
            if modules:
                msg += "Here's the breakdown:\n"
                for m in modules:
                    msg += f"- {m['agent_name']}: {m['capability_percentage']:.1f}%\n"
            msg += "\nWe're getting closer every cycle!"
            return msg
        else:
            msg = f"System-wide operational readiness is currently at **{readiness:.1f}%**.\n\n"
            if modules:
                msg += "Detailed Module Readiness:\n"
                for m in modules:
                    msg += f"- **{m['agent_name']}**: {m['capability_percentage']:.1f}% readiness score.\n"
            msg += "\nFull operational status will be achieved upon all critical modules reaching 98% capability."
            return msg

    @staticmethod
    def _format_training(data: Dict[str, Any], tone: str) -> str:
        recommendations = data.get("training_recommendations", [])

        if tone == "casual":
            msg = "If you want to speed things up, check out these awesome resources: 🧠\n\n"
            for rec in recommendations:
                msg += f"### {rec['title']}\n"
                msg += f"{rec['description']}\n"
                msg += f"🔗 [Access Here]({rec['url']})\n\n"
            msg += "Just point me to one of these and I'll start learning!"
            return msg
        else:
            msg = "To accelerate system evolution, the following resources have been identified:\n\n"
            for rec in recommendations:
                msg += f"**{rec['title']}**\n"
                msg += f"Instruction: {rec['description']}\n"
                msg += f"Source URL: {rec['url']}\n\n"
            msg += "Integration of these intelligence sources will significantly reduce training latency."
            return msg

    @staticmethod
    def _format_general(data: Dict[str, Any], tone: str) -> str:
        message = data.get("message", "Task completed.")
        return message
