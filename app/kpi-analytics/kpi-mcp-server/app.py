from __future__ import annotations

import os
from typing import Any

import requests
import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi_mcp import FastApiMCP

load_dotenv()

KPI_DATA_API_URL = os.getenv("KPI_DATA_API_URL", "http://127.0.0.1:8080").rstrip("/")
MCP_HOST = os.getenv("MCP_HOST", "0.0.0.0")
MCP_PORT = int(os.getenv("MCP_PORT", "8091"))

app = FastAPI(
    title="Pulse KPI MCP Server",
    version="0.1.0",
    description="MCP wrapper around the Pulse KPI Serving API.",
)


def _get_kpi(path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
    url = f"{KPI_DATA_API_URL}{path}"
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
    except requests.HTTPError as exc:
        status_code = exc.response.status_code if exc.response is not None else 502
        detail = exc.response.text if exc.response is not None else str(exc)
        raise HTTPException(status_code=status_code, detail=detail) from exc
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"KPI Serving API unavailable: {exc}") from exc

    try:
        return response.json()
    except ValueError as exc:
        raise HTTPException(status_code=502, detail="KPI Serving API returned invalid JSON") from exc


@app.get("/health", operation_id="health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": "kpi-mcp-server",
        "kpi_data_api_url": KPI_DATA_API_URL,
    }


@app.get(
    "/tools/kpi/domains/{tenant_id}",
    operation_id="list_kpi_domains",
    description="List KPI domains for a tenant.",
)
def list_kpi_domains(tenant_id: str) -> dict[str, Any]:
    return _get_kpi(f"/kpis/{tenant_id}/domains")


@app.get(
    "/tools/kpi/metrics/{tenant_id}",
    operation_id="list_kpis_in_domain",
    description="List KPI metric names for a tenant, optionally filtered by domain.",
)
def list_kpis_in_domain(
    tenant_id: str,
    domain: str | None = Query(default=None),
) -> dict[str, Any]:
    params = {"domain": domain} if domain else None
    return _get_kpi(f"/kpis/{tenant_id}/metrics", params=params)


@app.get(
    "/tools/kpi/latest/{tenant_id}",
    operation_id="get_latest_kpis",
    description="Get latest KPI values for a tenant, optionally filtered by domain.",
)
def get_latest_kpis(
    tenant_id: str,
    domain: str | None = Query(default=None),
) -> dict[str, Any]:
    params = {"domain": domain} if domain else None
    return _get_kpi(f"/kpis/{tenant_id}/latest", params=params)


@app.get(
    "/tools/kpi/history/{tenant_id}/{domain}/{metric_name}",
    operation_id="get_kpi_history",
    description="Get KPI history for one tenant, domain, and metric.",
)
def get_kpi_history(
    tenant_id: str,
    domain: str,
    metric_name: str,
    periods: int = Query(default=6, ge=1, le=52),
) -> dict[str, Any]:
    return _get_kpi(
        f"/kpis/{tenant_id}/metrics/{domain}/{metric_name}/history",
        params={"limit": periods},
    )


mcp = FastApiMCP(
    app,
    name="Pulse KPI MCP Server",
    description="Tools for reading Pulse KPI domains, metrics, latest values, and metric history.",
    describe_all_responses=True,
    describe_full_response_schema=True,
    include_operations=[
        "list_kpi_domains",
        "list_kpis_in_domain",
        "get_latest_kpis",
        "get_kpi_history",
    ],
)
mcp.mount_http(app, mount_path="/mcp")


if __name__ == "__main__":
    uvicorn.run("app:app", host=MCP_HOST, port=MCP_PORT, reload=True)
