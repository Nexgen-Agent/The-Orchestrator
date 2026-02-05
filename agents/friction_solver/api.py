from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from agents.friction_solver.solver import FrictionSolver
from agents.friction_solver.models import FrictionSolverConfig

router = APIRouter(prefix="/friction-solver", tags=["friction-solver"])

@router.post("/solve")
async def solve_friction(payload: Dict[str, Any]):
    project_path = payload.get("project_path")
    error_message = payload.get("error_message")
    context_logs = payload.get("context_logs")
    auto_apply = payload.get("auto_apply", False)

    if not project_path or not error_message:
        raise HTTPException(status_code=400, detail="Missing project_path or error_message")

    try:
        config = FrictionSolverConfig(
            project_path=project_path,
            error_message=error_message,
            context_logs=context_logs,
            auto_apply=auto_apply
        )
        solver = FrictionSolver()
        report = await solver.solve(config)
        return {"status": "success", "result": report.model_dump(mode='json')}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
