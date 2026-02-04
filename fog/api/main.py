from fastapi import FastAPI
from fog.api.router import router
from agents.human_control_interface.api import router as human_control_router
from agents.meta_evolution.api import router as meta_evolution_router
from agents.system_resilience.api import router as system_resilience_router
from agents.agent_collaboration.api import router as collaboration_router
from agents.shooting_star_ingestion.api import router as ingestion_router
from agents.deployment_automation.api import router as deployment_router
from agents.learning_feedback.api import router as learning_router
from fog.core.engine import orchestration_engine
import asyncio
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
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

@app.get("/")
async def root():
    return {"message": "Welcome to Frontier Orchestration Gateway (FOG)"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
