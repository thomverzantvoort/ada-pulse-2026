from __future__ import annotations

import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent

from mcp_tools import kpi_toolset

load_dotenv()

MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash-lite")

FINANCIAL_INSTRUCTION = """
Analyze financial KPI values and trends for tenant_id pulse-demo.

Use the KPI MCP tools to retrieve:
- get_latest_kpis with domain financial
- get_kpi_history for burn_rate, cash_flow, revenue_growth, and outstanding_invoices

Apply these MVP rules:
- cash_flow < 0 means high severity
- burn_rate increasing for at least 3 periods means medium severity
- revenue_growth < 0 means medium severity
- outstanding_invoices increasing means medium severity
- cash_flow < 0 and outstanding_invoices increasing means high severity

Return only valid JSON with this shape:
{
  "agent": "financial_intelligence_agent",
  "domain": "financial",
  "status": "success",
  "insights": [
    {
      "metric_name": "cash_flow",
      "severity": "high",
      "trend": "decreasing",
      "insight": "Cash flow has deteriorated compared with previous periods.",
      "recommendation": "Review short-term expenses and prioritize invoice collection.",
      "evidence": {
        "latest_value": -12000,
        "previous_value": 5000,
        "periods_observed": 6
      }
    }
  ]
}

Use an empty insights array when no rule is triggered.
Do not include markdown, explanations, or extra keys.
"""

financial_agent = LlmAgent(
    name="financial_intelligence_agent",
    model=MODEL_NAME,
    description="Analyzes financial KPI values and trends.",
    instruction=FINANCIAL_INSTRUCTION,
    tools=[
        kpi_toolset(
            [
                "get_latest_kpis",
                "get_kpi_history",
            ],
        ),
    ],
)

root_agent = financial_agent
