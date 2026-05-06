from __future__ import annotations

import os

from dotenv import load_dotenv
from google.adk.agents import LlmAgent

load_dotenv()

MODEL_NAME = os.getenv("MODEL_NAME", "gemini-2.5-flash-lite")

SYNTHESIS_INSTRUCTION = """
Combine financial and sales CRM agent outputs into one normalized cross-domain insight payload.

Apply these cross-domain rules:
- revenue_growth negative and churn_rate increasing means high severity
- cash_flow negative and deal_velocity decreasing means high severity
- burn_rate increasing and conversion_rate decreasing means high severity
- outstanding_invoices increasing and incoming_leads decreasing means medium severity

Return only valid JSON with this shape:
{
  "agent": "insight_synthesis_agent",
  "status": "success",
  "synthesized_insights": [
    {
      "domain": "cross_domain",
      "severity": "high",
      "risk_type": "compound_revenue_pressure",
      "insight": "Revenue growth is declining while churn is increasing, indicating a compound operational risk.",
      "recommendation": "Prioritize retention actions and short-term revenue protection measures.",
      "related_metrics": [
        "revenue_growth",
        "churn_rate"
      ]
    }
  ],
  "final_severity": "high"
}

Use an empty synthesized_insights array and final_severity low when no cross-domain rule is triggered.
Do not include markdown, explanations, or extra keys.
"""

synthesis_agent = LlmAgent(
    name="insight_synthesis_agent",
    model=MODEL_NAME,
    description="Synthesizes financial and sales CRM insights into cross-domain risks.",
    instruction=SYNTHESIS_INSTRUCTION,
)

root_agent = synthesis_agent
