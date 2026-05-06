from __future__ import annotations

import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent

from mcp_tools import kpi_toolset

load_dotenv()

MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash-lite")

SALES_CRM_INSTRUCTION = """
Analyze sales and CRM KPI values and trends for tenant_id pulse-demo.

Use the KPI MCP tools to retrieve:
- get_latest_kpis with domain sales_crm
- get_kpi_history for incoming_leads, conversion_rate, deal_velocity, and churn_rate

Apply these MVP rules:
- conversion_rate decreasing for at least 3 periods means medium severity
- deal_velocity decreasing means medium severity
- churn_rate increasing means high severity
- incoming_leads decreasing and conversion_rate decreasing means high severity
- churn_rate increasing and deal_velocity decreasing means high severity

Return only valid JSON with this shape:
{
  "agent": "sales_crm_intelligence_agent",
  "domain": "sales_crm",
  "status": "success",
  "insights": [
    {
      "metric_name": "conversion_rate",
      "severity": "medium",
      "trend": "decreasing",
      "insight": "Conversion rate decreased while lead volume remained stable.",
      "recommendation": "Review lead qualification and follow-up quality.",
      "evidence": {
        "latest_value": 0.14,
        "previous_value": 0.22,
        "periods_observed": 6
      }
    }
  ]
}

Use an empty insights array when no rule is triggered.
Do not include markdown, explanations, or extra keys.
"""

sales_crm_agent = LlmAgent(
    name="sales_crm_intelligence_agent",
    model=MODEL_NAME,
    description="Analyzes sales and CRM KPI values and trends.",
    instruction=SALES_CRM_INSTRUCTION,
    tools=[
        kpi_toolset(
            [
                "get_latest_kpis",
                "get_kpi_history",
            ],
        ),
    ],
)

root_agent = sales_crm_agent
