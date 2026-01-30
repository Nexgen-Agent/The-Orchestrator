from fastapi import FastAPI
from fog.api.router import router
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

@app.get("/")
async def root():
    return {"message": "Welcome to Frontier Orchestration Gateway (FOG)"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
