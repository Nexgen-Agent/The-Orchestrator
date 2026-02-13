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
        agents_count = data.get("agents_online", 0)
        agent_status = data.get("agent_status", {})
        fixes = data.get("recent_fixes", [])

        offline_agents = [name for name, s in agent_status.items() if s != "Online"]

        if tone == "casual":
            msg = f"The system is currently {status.lower()}! 🟢 "
            msg += f"CPU usage is around {cpu}% and memory is at {mem}%. We've got {agents_count} agents active right now. "

            if offline_agents:
                msg += f"\n\nJust so you know, I'm having some trouble connecting to: {', '.join(offline_agents)}. I'll try to get them back online. "

            if fixes:
                msg += "\n\nI've also handled some recent issues to keep things stable: "
                fix_desc = [f"recovered {f.get('target')}" for f in fixes if f.get('action_type') == 'RECOVER_TASK']
                msg += ", ".join(fix_desc[:2]) + ". "

            msg += "\n\nIs there anything specific you'd like me to look into?"
            return msg
        else:
            msg = f"System analysis indicates a **{status}** status. "
            msg += f"Resource utilization is currently at {cpu}% CPU and {mem}% memory, with {agents_count} agent handlers engaged. "

            if offline_agents:
                msg += f"\n\nConnectivity Alert: The following agents are currently unreachable: {', '.join(offline_agents)}. "

            if fixes:
                msg += "\n\nResilience protocols have successfully addressed recent failures, including: "
                targets = [f.get('target') for f in fixes]
                msg += ", ".join(targets[:3]) + ". "

            msg += "\n\nThe orchestration environment remains stable and operational."
            return msg

    @staticmethod
    def _format_readiness(data: Dict[str, Any], tone: str) -> str:
        readiness = data.get("overall_readiness", 0.0) * 100
        modules = data.get("module_progress", [])
        summary = data.get("evaluation_summary", "")

        if tone == "casual":
            msg = f"We're currently at **{readiness:.1f}%** readiness for full deployment! 🚀 "

            if summary:
                msg += f"Basically, {summary.lower().replace('.', '')}. "

            if modules:
                top_modules = sorted(modules, key=lambda x: x['capability_percentage'], reverse=True)[:3]
                msg += "\n\nOur strongest modules right now are " + ", ".join([f"{m['agent_name']} ({m['capability_percentage']:.0f}%)" for m in top_modules]) + ". "

            msg += "\n\nWe're making solid progress toward the 98% goal!"
            return msg
        else:
            msg = f"Overall system readiness is assessed at **{readiness:.1f}%**. "

            if summary:
                msg += f"{summary} "

            if modules:
                msg += "\n\nModule Capability Analysis:\n"
                for m in modules[:5]:
                    msg += f"- **{m['agent_name']}**: {m['capability_percentage']:.1f}% functional readiness.\n"

            msg += "\nOperational deployment will proceed once the aggregate score exceeds the 98% threshold."
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
