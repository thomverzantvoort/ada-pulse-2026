from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException

from orchestrator.pipeline import PipelineRunRequest, PipelineRunResult, run_pipeline

app = FastAPI(
    title="Operational Intelligence Orchestrator",
    version="0.1.0",
    description="Local orchestrator for Operational Intelligence agents.",
)

_RUN_STATUS: dict[str, dict[str, Any]] = {}


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "operational-intelligence-orchestrator",
    }


@app.post("/pipeline/run", response_model=PipelineRunResult)
def run_pipeline_endpoint(request: PipelineRunRequest) -> PipelineRunResult:
    _RUN_STATUS[request.run_id] = {
        "run_id": request.run_id,
        "trace_id": request.trace_id,
        "tenant_id": request.tenant_id,
        "status": "running",
    }
    try:
        result = run_pipeline(request)
    except Exception as exc:
        _RUN_STATUS[request.run_id] = {
            "run_id": request.run_id,
            "trace_id": request.trace_id,
            "tenant_id": request.tenant_id,
            "status": "failed",
            "error_message": str(exc),
        }
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    _RUN_STATUS[request.run_id] = result.model_dump()
    return result


@app.get("/pipeline/{run_id}/status")
def get_pipeline_status(run_id: str) -> dict[str, Any]:
    status = _RUN_STATUS.get(run_id)
    if status is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return status


@app.post("/pubsub/kpis-computed")
def receive_kpis_computed() -> dict[str, str]:
    return {
        "status": "not_implemented",
        "message": "Local Pub/Sub push handling will be added after manual pipeline runs work.",
    }
