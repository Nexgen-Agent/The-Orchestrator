from fastapi import FastAPI
from fog.api.router import router
from agents.human_control_interface.api import router as human_control_router
from agents.meta_evolution.api import router as meta_evolution_router
from agents.system_resilience.api import router as system_resilience_router
from agents.agent_collaboration.api import router as collaboration_router
from agents.shooting_star_ingestion.api import router as ingestion_router
from agents.deployment_automation.api import router as deployment_router
from agents.learning_feedback.api import router as learning_router
from agents.visualization.api import router as visualization_router
from agents.software_builder.api import router as builder_router
from agents.debugger.api import router as debugger_router
from agents.friction_solver.api import router as friction_router
from agents.self_evolution_engine.api import router as evolution_router
from agents.meta_agent_trainer.api import router as mate_router
from agents.shooting_star_intelligence.api import router as intel_router
from agents.system_monitor.api import router as monitor_router
from fog.core.engine import orchestration_engine
import asyncio
from contextlib import asynccontextmanager
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Re-register agents from state store and auto-discover
    from fog.core.state import state_store
    from fog.core.connector import agent_registry, HttpAgentConnector, MockAgentConnector, LocalAgentConnector

    # 1. Registered agents from state store
    agents = state_store.get_agents()
    for name, config in agents.items():
        if config.get("handler_type") == "mock":
            connector = MockAgentConnector(name, config["endpoint"])
        elif config.get("handler_type") == "local":
            connector = LocalAgentConnector(name, config["endpoint"])
        else:
            connector = HttpAgentConnector(name, config["endpoint"])
        agent_registry.register_agent(connector)
        print(f"Re-registered agent: {name}")

    # 2. Auto-discover local agents
    if os.path.exists("agents"):
        for agent_dir in os.listdir("agents"):
            if os.path.isdir(os.path.join("agents", agent_dir)) and os.path.exists(os.path.join("agents", agent_dir, "handler.py")):
                # Derive name from directory (PascalCase)
                name = "".join(word.capitalize() for word in agent_dir.split("_"))
                if name not in agent_registry.agents:
                    connector = LocalAgentConnector(name, f"local://{agent_dir}")
                    agent_registry.register_agent(connector)
                    state_store.add_agent(name, {"name": name, "endpoint": f"local://{agent_dir}", "handler_type": "local"})
                    print(f"Auto-discovered and registered agent: {name}")

    await orchestration_engine.start()
    yield
    await orchestration_engine.stop()

app = FastAPI(title="Frontier Orchestration Gateway (FOG)", lifespan=lifespan)

app.include_router(router)
app.include_router(human_control_router)
app.include_router(meta_evolution_router)
app.include_router(system_resilience_router)
app.include_router(collaboration_router)
app.include_router(ingestion_router)
app.include_router(deployment_router)
app.include_router(learning_router)
app.include_router(visualization_router)
app.include_router(builder_router)
app.include_router(debugger_router)
app.include_router(friction_router)
app.include_router(evolution_router)
app.include_router(mate_router)
app.include_router(intel_router)
app.include_router(monitor_router)

# Static files for frontend
app.mount("/static", StaticFiles(directory="fog/frontend"), name="static")

@app.get("/")
async def root():
    return FileResponse("fog/frontend/index.html")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
