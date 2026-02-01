import os
import asyncio
from typing import Dict, Any, List
from agents.code_quality.evaluator import CodeQualityEvaluator
from agents.code_quality.models import ProjectQualityReport

async def analyze_project_quality(root_path: str) -> ProjectQualityReport:
    root_path = os.path.abspath(root_path)
    files_to_evaluate = []

    for root, _, files in os.walk(root_path):
        for file in files:
            if file.endswith(".py"):
                files_to_evaluate.append(os.path.join(root, file))

    results = []

    def process_file(file_path):
        try:
            evaluator = CodeQualityEvaluator(file_path)
            return evaluator.evaluate()
        except Exception:
            return None

    tasks = [asyncio.to_thread(process_file, fp) for fp in files_to_evaluate]
    evaluations = await asyncio.gather(*tasks)
    results = [e for e in evaluations if e is not None]

    if not results:
        return ProjectQualityReport(root_path=root_path, average_score=0, files=[], summary_stats={})

    avg_score = sum(r.score for r in results) / len(results)

    summary_stats = {
        "total_files": len(results),
        "total_complexity": sum(r.cyclomatic_complexity for r in results),
        "total_unused_imports": sum(len(r.unused_imports) for r in results),
        "total_missing_try_except": sum(len(r.missing_try_except) for r in results),
        "critical_risk_files": len([r for r in results if r.risk_level == "Critical"]),
        "high_risk_files": len([r for r in results if r.risk_level == "High"])
    }

    return ProjectQualityReport(
        root_path=root_path,
        average_score=avg_score,
        files=results,
        summary_stats=summary_stats
    )

async def handle_task(task_packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestration handler for FOG.
    Expects 'project_path' or 'file_path' in payload.
    """
    payload = task_packet.get("payload", {})
    project_path = payload.get("project_path")
    file_path = payload.get("file_path")

    try:
        if project_path:
            report = await analyze_project_quality(project_path)
            return {
                "status": "success",
                "result": report.model_dump(mode='json')
            }
        elif file_path:
            evaluator = CodeQualityEvaluator(file_path)
            report = evaluator.evaluate()
            return {
                "status": "success",
                "result": report.model_dump(mode='json')
            }
        else:
            return {"status": "error", "message": "Missing project_path or file_path in payload"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
