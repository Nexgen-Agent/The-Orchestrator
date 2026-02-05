import httpx
import asyncio

async def register_agents():
    agents = [
        {"name": "FrictionSolver", "endpoint": "http://localhost:3000/friction-solver", "handler_type": "http"},
        {"name": "SelfEvolutionEngine", "endpoint": "http://localhost:3000/self-evolution", "handler_type": "http"},
        {"name": "MetaAgentTrainer", "endpoint": "http://localhost:3000/mate", "handler_type": "http"},
        {"name": "ShootingStarIntelligence", "endpoint": "http://localhost:3000/shooting-star-intelligence", "handler_type": "http"},
        {"name": "StructureAnalyzer", "endpoint": "http://mock-analyzer:8000", "handler_type": "mock"},
        {"name": "DependencyGraph", "endpoint": "http://mock-graph:8000", "handler_type": "mock"},
        {"name": "LogicSummarizer", "endpoint": "http://mock-summarizer:8000", "handler_type": "mock"},
        {"name": "SoftwareBuilder", "endpoint": "http://mock-builder:8000", "handler_type": "mock"},
        {"name": "Debugger", "endpoint": "http://mock-debugger:8000", "handler_type": "mock"}
    ]

    async with httpx.AsyncClient() as client:
        for agent in agents:
            try:
                resp = await client.post("http://localhost:3000/register-agent", json=agent)
                print(f"Registered {agent['name']}: {resp.json()}")
            except Exception as e:
                print(f"Failed to register {agent['name']}: {e}")

if __name__ == "__main__":
    asyncio.run(register_agents())
