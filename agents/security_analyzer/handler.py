import os
import asyncio
from typing import Dict, Any, List
from agents.security_analyzer.analyzer import SecurityAnalyzer
from agents.security_analyzer.models import ProjectSecurityReport, RiskSeverity

async def analyze_project_security(root_path: str) -> ProjectSecurityReport:
    root_path = os.path.abspath(root_path)
    files_to_scan = []

    for root, _, files in os.walk(root_path):
        for file in files:
            if file.endswith(".py"):
                files_to_scan.append(os.path.join(root, file))

    results = []
    analyzer = SecurityAnalyzer()

    def process_file(file_path):
        try:
            return analyzer.scan_file(file_path)
        except Exception:
            return None

    tasks = [asyncio.to_thread(process_file, fp) for fp in files_to_scan]
    scans = await asyncio.gather(*tasks)
    results = [s for s in scans if s is not None]

    summary = {
        "total_files": len(results),
        "critical_risks": sum(len([r for r in s.risks_detected if r.severity == RiskSeverity.CRITICAL]) for s in results),
        "high_risks": sum(len([r for r in s.risks_detected if r.severity == RiskSeverity.HIGH]) for s in results),
        "unsafe_patterns": sum(len(s.unsafe_patterns) for s in results),
        "risky_deps": sum(len(s.risky_dependencies) for s in results)
    }

    return ProjectSecurityReport(
        root_path=root_path,
        reports=results,
        summary=summary
    )

async def handle_task(task_packet: Dict[str, Any]) -> Dict[str, Any]:
    """
    Orchestration handler for FOG.
    Expects 'project_path' or 'file_path' in payload.
    """
    payload = task_packet.get("payload", {})
    project_path = payload.get("project_path")
    file_path = payload.get("file_path")

    analyzer = SecurityAnalyzer()

    try:
        if project_path:
            report = await analyze_project_security(project_path)
            return {
                "status": "success",
                "result": report.model_dump(mode='json')
            }
        elif file_path:
            report = analyzer.scan_file(file_path)
            return {
                "status": "success",
                "result": report.model_dump(mode='json')
            }
        else:
            return {"status": "error", "message": "Missing project_path or file_path in payload"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
