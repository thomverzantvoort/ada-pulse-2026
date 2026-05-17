# ADA Pulse 2026

Working repository for Assignment 2 implementation of the Pulse architecture.

This README describes the complete implementation and deployment workflow for the Operational Intelligence domain.

The implementation follows a two-phase approach:

```text
Phase 1
Local validation and functional testing

Phase 2
Cloud deployment to Google Cloud Platform
```

The local implementation is always validated first before deployment to Google Cloud Platform. This prevents debugging local implementation issues and cloud infrastructure issues at the same time.

The deployment strategy is therefore:

```text
1. Build and validate all services locally.
2. Validate ADK agents locally.
3. Validate KPI Serving API and MCP endpoint locally.
4. Validate the Local Orchestrator pipeline locally.
5. Validate the full local end-to-end flow.
6. Deploy the validated services to Google Cloud Platform.
7. Connect GCS, Pub/Sub, Cloud Functions, Cloud Run, and BigQuery.
8. Validate the cloud end-to-end flow.
```

The local architecture acts as the functional reference implementation. Google Cloud deployment is performed only after the local validation checklist succeeds completely.

## Implementation Phases

### Phase 1. Local Validation

The local validation phase focuses on functional correctness.

Validated components:

```text
KPI Serving API (with MCP endpoint embedded in main.py)
Financial Intelligence Agent
Sales CRM Intelligence Agent
Insight Synthesis Agent
Local Orchestrator
```

The local environment validates:

```text
ADK integration
MCP tool integration
REST-to-MCP conversion (via fastapi-mcp in kpi-serving/main.py)
agent orchestration
pipeline execution
JSON output contracts
```

The local implementation flow is:

```text
KPI Serving API + MCP endpoint (/mcp), port 8080
-> Financial Intelligence Agent + Sales CRM Intelligence Agent (parallel)
-> Insight Synthesis Agent
-> Local Orchestrator, port 8081
```

### Phase 2. Google Cloud Deployment

After successful local validation, the implementation is deployed to Google Cloud Platform.

The cloud deployment adds:

```text
GCS ingest bucket
Cloud Function KPI computation
BigQuery Gold Layer
Pub/Sub eventing
Cloud Run deployment
push subscriptions
distributed cloud logging
```

The cloud deployment flow is:

```text
GCS ingest files
-> KPI Cloud Function
-> BigQuery Gold Layer
-> kpis-computed Pub/Sub topic
-> Operational Intelligence Orchestrator on Cloud Run
-> KPI Serving API with MCP on Cloud Run (pulse-kpi-serving-mcp)
-> insights-ready Pub/Sub topic
```

The Google Cloud deployment phase should only start after the local validation checklist succeeds completely.

## Project Structure

```text
ada-pulse-2026/
  app/
    infra/
      data-ingest-uploader/
        upload_ingest_to_gcs.py        # uploads ingest files to GCS
    kpi-analytics/
      kpi-compute/                     # KPI Cloud Function
        main.py
        requirements.txt
      kpi-serving/                     # FastAPI read API over BigQuery Gold Layer
        main.py                        # includes MCP endpoint at /mcp via fastapi-mcp
        bq_repository.py
        config.py
        router_kpis.py
        schemas.py
        requirements.txt               # includes fastapi-mcp
        Dockerfile
        README.md
    operational-intelligence/
      orchestrator-agent/              # FastAPI orchestrator + ADK agents
        app.py                         # FastAPI app and pipeline runner
        Dockerfile
        requirements.txt
        .env.example
        README.md
        pulse_oi/
          __init__.py
          agent.py                     # root_agent: SequentialAgent wrapping ParallelAgent + synthesis
          financial_agent.py           # FinancialIntelligenceAgent
          sales_crm_agent.py           # SalesCrmIntelligenceAgent
          synthesis_agent.py           # InsightSynthesisAgent
    reporting-delivery/
      main.py                        # FastAPI app, receives Pub/Sub push, orchestrates pipeline
      renderer.py                    # renders insight JSON into styled HTML report
      email_sender.py                # delivers HTML report via Gmail SMTP
      Dockerfile
      requirements.txt
      README.md
  data/
    ingest/
    kpi/
  docs/
    Operational-Intelligence-plan.md
    KPI-Analytics-plan.md
    Assignment2-Outline.md
  scripts/
  pyproject.toml
```

## Local Architecture

The local Operational Intelligence flow is:

```text
KPI Serving API + MCP endpoint (/mcp), port 8080
-> Financial Intelligence Agent + Sales CRM Intelligence Agent (parallel)
-> Insight Synthesis Agent
-> Orchestrator, port 8081
```

The pipeline uses the ADK Parallel Fan-Out/Gather pattern followed by synthesis:

```text
ParallelAgent: Financial Intelligence Agent + Sales CRM Intelligence Agent
-> InsightSynthesisAgent
```

The MCP endpoint is embedded directly in the KPI Serving API (`kpi-serving/main.py`) using
`fastapi-mcp`. There is no separate MCP server process — the `/mcp` endpoint runs on the
same port as the REST API (8080).

## Prerequisites

Required local tools:

```text
PowerShell
Git
uv
gcloud CLI
Node.js and npx, for MCP Inspector
```

Create or sync the Python environment from the repository root:

```powershell
uv sync
```

Check Google Cloud configuration:

```powershell
gcloud auth list
gcloud config get-value project
gcloud config list
```

Configure Application Default Credentials for BigQuery and Vertex AI:

```powershell
gcloud auth application-default login
```

## Git Branch Workflow

Operational Intelligence work should be developed on a separate branch.

Check the current working tree:

```powershell
git status
```

Create and switch to a new branch:

```powershell
git switch -c feature/operational-intelligence
```

Confirm the active branch:

```powershell
git branch
```

The active branch is marked with `*`.

Before committing, only stage files that belong to the work. Do not stage `.env`, `__pycache__`, or `sessions.db`.

Example:

```powershell
git add README.md app/kpi-analytics/kpi-serving/main.py app/operational-intelligence/orchestrator-agent
git commit -m "Add operational intelligence pipeline"
```

## Environment Files

Do not commit `.env` files.

The Operational Intelligence orchestrator uses:

```text
app/operational-intelligence/orchestrator-agent/.env
```

Copy from `.env.example` and fill in your values. Expected local content:

```text
GOOGLE_GENAI_USE_VERTEXAI=true
GOOGLE_CLOUD_PROJECT=<your-project-id>
KPI_MCP_URL=http://127.0.0.1:8080/mcp
INSIGHTS_READY_TOPIC=insights-ready
```

`KPI_MCP_URL` points to the MCP endpoint embedded in the KPI Serving API — same port (8080), path `/mcp`.

## Terminal Layout

Use separate terminals for each long-running service.

```text
Terminal 1: KPI Serving API + MCP, port 8080
Terminal 2: Orchestrator + ADK web UI, port 8081
Terminal 3: curl or Invoke-RestMethod tests
```

## 1. Start KPI Serving API

The KPI Serving API reads from the BigQuery Gold table and also exposes an MCP endpoint
at `/mcp` via `fastapi-mcp` in `main.py`.

Install service requirements:

```powershell
uv pip install -r app\kpi-analytics\kpi-serving\requirements.txt
```

Start the service:

```powershell
cd app\kpi-analytics\kpi-serving
uv run python -m uvicorn main:app --reload --port 8080
```

Health check:

```powershell
curl http://127.0.0.1:8080/health
```

Expected response:

```json
{"status":"ok"}
```

KPI data checks:

```powershell
curl http://127.0.0.1:8080/kpis/pulse-demo/domains
curl "http://127.0.0.1:8080/kpis/pulse-demo/latest?domain=financial"
curl "http://127.0.0.1:8080/kpis/pulse-demo/latest?domain=sales_crm"
curl "http://127.0.0.1:8080/kpis/pulse-demo/metrics/financial/burn_rate/history?limit=6"
```

The tenant path must be `pulse-demo`. Other tenant values return `404`.

## 2. Validate MCP Endpoint

The MCP endpoint is embedded in `kpi-serving/main.py` using `fastapi-mcp`. Once the
KPI Serving API is running, the MCP endpoint is available at the same port under `/mcp`.

MCP tools exposed:

```text
list_kpi_domains
list_kpi_metrics
get_latest_kpis
get_latest_kpi_single
get_kpi_history
```

Validate with MCP Inspector:

```powershell
npx @modelcontextprotocol/inspector
```

Connect the Inspector to:

```text
http://127.0.0.1:8080/mcp
```

Test tool calls:

```text
get_latest_kpis tenant_id=pulse-demo domain=financial
get_kpi_history tenant_id=pulse-demo domain=financial metric_name=burn_rate limit=6
```

Continue only after the MCP tools return KPI data.

## 3. Validate ADK Agents

All agents are defined inside the `pulse_oi` package:

```text
app/operational-intelligence/orchestrator-agent/
  app.py                        - FastAPI app and pipeline runner
  Dockerfile
  requirements.txt
  .env.example
  pulse_oi/
    __init__.py
    agent.py                    - root_agent: SequentialAgent (ParallelAgent + synthesis)
    financial_agent.py          - FinancialIntelligenceAgent
    sales_crm_agent.py          - SalesCrmIntelligenceAgent
    synthesis_agent.py          - InsightSynthesisAgent
```

### Agent overview

**FinancialIntelligenceAgent** (`financial_agent.py`)
Retrieves financial KPIs via MCP and applies severity rules.
Metrics: `burn_rate`, `cash_flow`, `revenue_growth`, `outstanding_invoices`, `weekly_profit`
Output key: `financial_insights`

**SalesCrmIntelligenceAgent** (`sales_crm_agent.py`)
Retrieves sales and CRM KPIs via MCP and applies severity rules.
Metrics: `churn_rate`, `conversion_rate`, `deal_velocity`, `incoming_leads`
Output key: `sales_crm_insights`

**InsightSynthesisAgent** (`synthesis_agent.py`)
Reads both domain outputs from session state. Applies cross-domain compound risk rules.
Produces consolidated report with `final_severity`.
Output key: `synthesized_insights`

**Agent composition** (`agent.py`):

```text
SequentialAgent: OperationalIntelligencePipeline
  |-- ParallelAgent: ParallelKpiAnalysis
  |       |-- FinancialIntelligenceAgent
  |       └-- SalesCrmIntelligenceAgent
  └-- InsightSynthesisAgent
```

Start the ADK web UI:

```powershell
cd app\operational-intelligence\orchestrator-agent
uvicorn app:app --host 0.0.0.0 --port 8081
```

Open the ADK web UI at `http://127.0.0.1:8081/dev-ui`

The ADK app name is `pulse_oi`.

## 4. Run the Pipeline

The pipeline is implemented directly in `app.py` using the ADK `Runner` with
`InMemorySessionService`. There is no separate orchestrator subfolder.

Endpoints:

```text
GET  /health
POST /pipeline/run
POST /pubsub/kpis-computed
```

Before starting, verify:

```text
1. KPI Serving API is running on port 8080.
2. MCP Inspector can call the KPI tools at http://127.0.0.1:8080/mcp.
3. orchestrator-agent/.env contains GOOGLE_GENAI_USE_VERTEXAI, GOOGLE_CLOUD_PROJECT, and KPI_MCP_URL.
```

Manual pipeline run:

```powershell
$body = @{ tenant_id = "pulse-demo"; run_id = "manual-run-001" } | ConvertTo-Json

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8081/pipeline/run" `
  -ContentType "application/json" `
  -Body $body
```

Expected pipeline behavior:

```text
1. FinancialIntelligenceAgent and SalesCrmIntelligenceAgent run in parallel.
2. Both agents call get_latest_kpis and get_kpi_history via MCP.
3. InsightSynthesisAgent combines both outputs into a consolidated report.
4. Result returned as JSON with final_severity and cross-domain insights.
```

## Troubleshooting

`uvicorn` returns `Could not import module "app"`:

```text
Cause: command started from the wrong folder.
Fix: run from app/operational-intelligence/orchestrator-agent.
```

ADK web shows `No agents found in current folder`:

```text
Cause: ADK web was started from a subfolder instead of orchestrator-agent/.
Fix: run from app/operational-intelligence/orchestrator-agent.
```

PowerShell `curl -d` returns invalid JSON:

```text
Cause: quoting differences in PowerShell.
Fix: use Invoke-RestMethod with ConvertTo-Json.
```

Pipeline returns invalid JSON:

```text
Cause: an agent returned text that is not valid JSON.
Fix: inspect the agent response in the error detail and check agent instructions.
```

## Local Validation Checklist

```text
1. git status reviewed.
2. gcloud project is set correctly.
3. ADC configured correctly.
4. KPI Serving API /health works on port 8080.
5. KPI Serving API returns financial and sales_crm data.
6. MCP Inspector connects to /mcp on port 8080 and executes get_latest_kpis and get_kpi_history.
7. orchestrator-agent/.env has correct GOOGLE_GENAI_USE_VERTEXAI, GOOGLE_CLOUD_PROJECT, KPI_MCP_URL.
8. Orchestrator /health works on port 8081.
9. Orchestrator /pipeline/run returns a consolidated synthesis payload with final_severity.
10. Only intentional files staged (no .env, no __pycache__, no sessions.db).
```

---

# Cloud Deployment Phase

Only continue with this phase after the Local Validation Checklist succeeds completely.

## Cloud Architecture

```text
GCS Bucket: pulse-demo-bronze
        |
        | ready.json finalized
        v
Cloud Function: compute_kpis
        |
        | writes
        v
BigQuery: kpi_analytics_gold.gold_kpi_snapshots
        |
        | publishes
        v
Pub/Sub topic: kpis-computed
        |
        | push subscription: kpis-computed-push-orchestrator
        v
Cloud Run: pulse-orchestrator
        |
        | MCP calls to /mcp
        v
Cloud Run: pulse-kpi-serving-mcp
(kpi-serving with MCP embedded in main.py)
        |
        | queries
        v
BigQuery Gold Layer
        |
        | publishes
        v
Pub/Sub topic: insights-ready
        |
        | push subscription: insights-ready-push-reporting
        v
Cloud Run: pulse-reporting-delivery
        |
        | renders HTML report and sends via Gmail SMTP
        v
Email delivered to configured recipient
```

## 5. Enable Required Google Cloud APIs

Open:

```text
Google Cloud Console -> APIs & Services -> Library
```

Enable:

```text
Cloud Run API
Cloud Functions API
Cloud Build API
Artifact Registry API
Pub/Sub API
BigQuery API
Eventarc API
Vertex AI API
```

## 6. Create or Validate GCS Bucket

Validate that the bucket exists:

```text
pulse-demo-bronze
```

## 7. Upload Ingest Files

Upload to `pulse-demo-bronze` in this order:

```text
1. financial_clean.csv
2. sales_marketing_clean.csv
3. ready.json  (always last — triggers KPI computation)
```

## 8. Enable and Configure Pub/Sub

Create two topics:

```text
kpis-computed
insights-ready
```

## 9. Deploy KPI Cloud Function

Source: `app/kpi-analytics/kpi-compute`

```text
Name: compute_kpis
Region: us-central1
Environment: 2nd gen
Runtime: Python 3.11
Trigger: Cloud Storage, bucket pulse-demo-bronze, event finalized
Entry point: compute_kpis
```

After deployment, upload `ready.json` and verify KPI rows appear in BigQuery.

## 10. Validate BigQuery Gold Layer

Dataset: `kpi_analytics_gold`
Table: `gold_kpi_snapshots`

Validate KPI rows appear after Cloud Function execution.

## 11. Deploy KPI Serving API with MCP (pulse-kpi-serving-mcp)

Source: `app/kpi-analytics/kpi-serving`

The MCP endpoint is embedded in `main.py` via `fastapi-mcp`. This single service provides
both the REST API and the `/mcp` endpoint used by the agents.

```bash
gcloud run deploy pulse-kpi-serving-mcp \
  --source app/kpi-analytics/kpi-serving \
  --region <your-region> \
  --allow-unauthenticated \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=<your-project-id>,BQ_DATASET=kpi_analytics_gold,BQ_TABLE=gold_kpi_snapshots"
```

After deployment, note the Service URL. The MCP endpoint is at:

```text
https://<service-url>/mcp
```

Validate:

```text
https://<service-url>/health
https://<service-url>/docs
```

## 12. Deploy Operational Intelligence Orchestrator

Source: `app/operational-intelligence/orchestrator-agent`

```bash
gcloud run deploy pulse-orchestrator \
  --source app/operational-intelligence/orchestrator-agent \
  --region <your-region> \
  --allow-unauthenticated \
  --timeout 300 \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=<your-project-id>,GOOGLE_GENAI_USE_VERTEXAI=true,INSIGHTS_READY_TOPIC=insights-ready,KPI_MCP_URL=https://<kpi-serving-mcp-url>/mcp"
```

Validate:

```text
https://<orchestrator-url>/health
```

Expected response:

```json
{"status":"ok","service":"operational-intelligence-orchestrator"}
```

## 13. Configure Pub/Sub Push Subscription

Create a push subscription that sends `kpis-computed` messages to the orchestrator:

```bash
gcloud pubsub subscriptions create kpis-computed-push-orchestrator \
  --topic kpis-computed \
  --push-endpoint https://<orchestrator-url>/pubsub/kpis-computed \
  --ack-deadline 300
```

## 14. Test the Cloud Pipeline

Trigger via REST (synchronous):

```powershell
$body = @{ tenant_id = "pulse-demo"; run_id = "cloud-test-001" } | ConvertTo-Json
Invoke-RestMethod -Method Post `
  -Uri "https://<orchestrator-url>/pipeline/run" `
  -ContentType "application/json" `
  -Body $body
```

Trigger via Pub/Sub (simulates the KPI Cloud Function):

```powershell
gcloud pubsub topics publish kpis-computed `
  --message="KPI computation completed" `
  --attribute=tenant_id=pulse-demo,run_id=kpi-run-001,trace_id=trace-001
```

## 15. Validate insights-ready Output

Create a debug subscription and pull results:

```powershell
gcloud pubsub subscriptions create insights-ready-debug --topic insights-ready

gcloud pubsub subscriptions pull insights-ready-debug --auto-ack --limit 5
```

## 16. Check Cloud Logs

```powershell
gcloud run services logs read pulse-orchestrator --region <your-region> --limit 80
```

Expected log entries:

```text
Pub/Sub trigger received
Pipeline run started
HTTP Request: POST .../mcp - 200 OK
Response received from the model
Published insights-ready
Pipeline run completed - severity=high
```

## 17. Full End-to-End Validation Flow

```text
1. Upload ingest files to GCS.
2. Upload ready.json last.
3. Cloud Function computes KPIs.
4. BigQuery Gold Layer is updated.
5. kpis-computed Pub/Sub event is published.
6. Push subscription triggers Orchestrator.
7. FinancialIntelligenceAgent and SalesCrmIntelligenceAgent run in parallel.
8. Both agents retrieve KPI data via MCP from pulse-kpi-serving-mcp.
9. InsightSynthesisAgent combines outputs.
10. Orchestrator publishes insights-ready.
11. insights-ready-push-reporting subscription triggers pulse-reporting-delivery.
12. renderer.py generates styled HTML report from insight payload.
13. email_sender.py delivers report via Gmail SMTP to configured recipient.****
```

## 18. Cloud Deployment Validation Checklist

```text
1. Required Google Cloud APIs enabled.
2. GCS bucket exists with ingest files.
3. KPI Cloud Function deployed and triggered by ready.json.
4. BigQuery Gold Layer populated.
5. Pub/Sub topics kpis-computed and insights-ready exist.
6. pulse-kpi-serving-mcp deployed and /health returns ok.
7. MCP endpoint at /mcp returns KPI tools.
8. pulse-orchestrator deployed and /health returns ok.
9. Pub/Sub push subscription kpis-computed-push-orchestrator created.
10. Manual /pipeline/run returns consolidated synthesis payload.
11. Pub/Sub test message triggers orchestrator automatically.
12. insights-ready messages are published and pullable.
13. pulse-reporting-delivery deployed and /health returns ok.
14. Pub/Sub push subscription insights-ready-push-reporting created.
15. Email report delivered to recipient after insights-ready fires.
```

## Notes

- Operational Intelligence plan: [docs/Operational-Intelligence-plan.md](docs/Operational-Intelligence-plan.md)
- Each agent's README is in `app/operational-intelligence/orchestrator-agent/README.md`
- KPI Serving API README is in `app/kpi-analytics/kpi-serving/README.md`
