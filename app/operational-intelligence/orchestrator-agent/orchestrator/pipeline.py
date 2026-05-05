from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from google.adk.agents import BaseAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from pydantic import BaseModel, Field

from financial_agent.agent import root_agent as financial_agent
from sales_crm_agent.agent import root_agent as sales_crm_agent
from synthesis_agent.agent import root_agent as synthesis_agent

APP_NAME = "operational-intelligence-local"
DEFAULT_USER_ID = "local-user"


class PipelineRunRequest(BaseModel):
    tenant_id: str = "pulse-demo"
    trace_id: str = Field(default_factory=lambda: f"trace-local-{uuid4()}")
    run_id: str = Field(default_factory=lambda: f"oi-run-local-{uuid4()}")
    source_kpi_run_id: str = "kpi-run-local"
    period_end: str | None = None


class PipelineRunResult(BaseModel):
    tenant_id: str
    trace_id: str
    run_id: str
    source_kpi_run_id: str
    status: str
    financial_insights: dict[str, Any]
    sales_crm_insights: dict[str, Any]
    synthesized_insights: dict[str, Any]
    final_severity: str
    completed_at: str


def run_pipeline(request: PipelineRunRequest | dict[str, Any]) -> PipelineRunResult:
    request_model = (
        request
        if isinstance(request, PipelineRunRequest)
        else PipelineRunRequest.model_validate(request)
    )

    financial_output = _run_agent_json(
        agent=financial_agent,
        prompt=_domain_prompt(
            tenant_id=request_model.tenant_id,
            domain="financial",
            trace_id=request_model.trace_id,
            source_kpi_run_id=request_model.source_kpi_run_id,
        ),
        session_id=f"{request_model.run_id}-financial",
    )
    sales_crm_output = _run_agent_json(
        agent=sales_crm_agent,
        prompt=_domain_prompt(
            tenant_id=request_model.tenant_id,
            domain="sales_crm",
            trace_id=request_model.trace_id,
            source_kpi_run_id=request_model.source_kpi_run_id,
        ),
        session_id=f"{request_model.run_id}-sales-crm",
    )
    synthesis_output = _run_agent_json(
        agent=synthesis_agent,
        prompt=_synthesis_prompt(
            tenant_id=request_model.tenant_id,
            trace_id=request_model.trace_id,
            financial_output=financial_output,
            sales_crm_output=sales_crm_output,
        ),
        session_id=f"{request_model.run_id}-synthesis",
    )

    return PipelineRunResult(
        tenant_id=request_model.tenant_id,
        trace_id=request_model.trace_id,
        run_id=request_model.run_id,
        source_kpi_run_id=request_model.source_kpi_run_id,
        status="completed",
        financial_insights=financial_output,
        sales_crm_insights=sales_crm_output,
        synthesized_insights=synthesis_output,
        final_severity=str(synthesis_output.get("final_severity", "low")),
        completed_at=datetime.now(UTC).isoformat(),
    )


def _run_agent_json(agent: BaseAgent, prompt: str, session_id: str) -> dict[str, Any]:
    text = _strip_json_code_fence(
        _run_agent_text(agent=agent, prompt=prompt, session_id=session_id),
    )
    try:
        result = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Agent {agent.name} returned invalid JSON: {text}") from exc
    if not isinstance(result, dict):
        raise ValueError(f"Agent {agent.name} returned JSON that is not an object")
    return result


def _run_agent_text(agent: BaseAgent, prompt: str, session_id: str) -> str:
    session_service = InMemorySessionService()
    session_service.create_session_sync(
        app_name=APP_NAME,
        user_id=DEFAULT_USER_ID,
        session_id=session_id,
    )
    runner = Runner(
        app_name=APP_NAME,
        agent=agent,
        session_service=session_service,
    )
    message = types.Content(
        role="user",
        parts=[types.Part(text=prompt)],
    )

    final_text: str | None = None
    for event in runner.run(
        user_id=DEFAULT_USER_ID,
        session_id=session_id,
        new_message=message,
    ):
        if event.is_final_response() and event.content and event.content.parts:
            text_parts = [part.text for part in event.content.parts if part.text]
            final_text = "".join(text_parts).strip()

    if not final_text:
        raise RuntimeError(f"Agent {agent.name} did not return a final text response")
    return final_text


def _strip_json_code_fence(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```json") and stripped.endswith("```"):
        return stripped.removeprefix("```json").removesuffix("```").strip()
    if stripped.startswith("```") and stripped.endswith("```"):
        return stripped.removeprefix("```").removesuffix("```").strip()
    return stripped


def _domain_prompt(
    tenant_id: str,
    domain: str,
    trace_id: str,
    source_kpi_run_id: str,
) -> str:
    return json.dumps(
        {
            "task": "analyze_domain_kpis",
            "tenant_id": tenant_id,
            "domain": domain,
            "trace_id": trace_id,
            "source_kpi_run_id": source_kpi_run_id,
            "output": "strict_json_only",
        },
    )


def _synthesis_prompt(
    tenant_id: str,
    trace_id: str,
    financial_output: dict[str, Any],
    sales_crm_output: dict[str, Any],
) -> str:
    return json.dumps(
        {
            "task": "synthesize_operational_insights",
            "tenant_id": tenant_id,
            "trace_id": trace_id,
            "financial_output": financial_output,
            "sales_crm_output": sales_crm_output,
            "output": "strict_json_only",
        },
    )
