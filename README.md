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
3. Validate KPI Serving API locally.
4. Validate KPI MCP Server locally.
5. Validate the Local Orchestrator pipeline locally.
6. Validate the full local end-to-end flow.
7. Deploy the validated services to Google Cloud Platform.
8. Connect GCS, Pub/Sub, Cloud Functions, Cloud Run, and BigQuery.
9. Validate the cloud end-to-end flow.
```

The local architecture acts as the functional reference implementation. Google Cloud deployment is performed only after the local validation checklist succeeds completely.

## Implementation Phases

### Phase 1. Local Validation

The local validation phase focuses on functional correctness.

Validated components:

```text
KPI Serving API
KPI MCP Server
Financial Intelligence Agent
Sales CRM Intelligence Agent
Insight Synthesis Agent
Local Orchestrator
```

The local environment validates:

```text
ADK integration
MCP tool integration
REST-to-MCP conversion
agent orchestration
pipeline execution
JSON output contracts
trace propagation
```

The local implementation flow is:

```text
KPI Serving API, port 8080
-> KPI MCP Server, port 8091
-> Financial Intelligence Agent
-> Sales CRM Intelligence Agent
-> Insight Synthesis Agent
-> Local Orchestrator, port 8090
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
-> KPI MCP Server on Cloud Run
-> KPI Serving API on Cloud Run
-> insights-ready Pub/Sub topic
```

The Google Cloud deployment phase should only start after the local validation checklist succeeds completely.

## Project Structure

```text
ada-pulse-2026/
  app/
    infra/                         # GCS upload and ingest helpers
    kpi-analytics/
      kpi-compute/                 # KPI Cloud Function
      kpi-serving/                 # FastAPI read API over BigQuery Gold Layer
      kpi-mcp-server/              # Local MCP wrapper around kpi-serving
    operational-intelligence/
      orchestrator-agent/          # Local ADK agents and FastAPI orchestrator
    reporting-delivery/
  data/
    mockaroo/
    ingest/
    kpi/
  docs/
  scripts/
  pyproject.toml
```

## Local Architecture

The local Operational Intelligence flow is:

```text
KPI Serving API, port 8080
-> KPI MCP Server, port 8091
-> Financial Intelligence Agent
-> Sales CRM Intelligence Agent
-> Insight Synthesis Agent
-> Local Orchestrator, port 8090
```

The MVP follows the Lab 8 Sequential Pipeline Pattern:

```text
Financial Intelligence Agent
-> Sales CRM Intelligence Agent
-> Insight Synthesis Agent
```

A later version can use the Lab 8 Parallel Fan-Out/Gather Pattern:

```text
Financial Intelligence Agent + Sales CRM Intelligence Agent
-> Insight Synthesis Agent
```

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
cd "C:\Projects\Advanced Data Architectures\ada-pulse-2026"
uv sync
```

Check Google Cloud configuration:

```powershell
gcloud auth list
gcloud config get-value project
gcloud config list
```

Set the expected project:

```powershell
gcloud config set project ada26-pulse-project
```

Configure Application Default Credentials for BigQuery and Vertex AI:

```powershell
gcloud auth application-default login
gcloud auth application-default set-quota-project ada26-pulse-project
```

Expected project value:

```text
ada26-pulse-project
```

Google Cloud may warn that the project has no `environment` tag. That warning does not block local development.

## Git Branch Workflow

Operational Intelligence work should be developed on a separate branch.

Check the current working tree:

```powershell
git status
```

Create and switch to a new branch:

```powershell
git switch -c feature/operational-intelligence-local
```

Confirm the active branch:

```powershell
git branch
```

The active branch is marked with `*`.

Existing local changes move to the new branch when `git switch -c` is used. Before committing, only stage files that belong to the work.

Example:

```powershell
git add README.md docs/Operational-Intelligence-plan.md app/kpi-analytics/kpi-mcp-server app/operational-intelligence/orchestrator-agent
git commit -m "Add local operational intelligence workflow"
```

Data files, `pyproject.toml`, and `uv.lock` should only be staged when those changes are intentional.

## Environment Files

Do not commit `.env` files.

The KPI MCP server uses:

```text
app/kpi-analytics/kpi-mcp-server/.env
```

Expected local content:

```text
KPI_DATA_API_URL=http://127.0.0.1:8080
MCP_HOST=0.0.0.0
MCP_PORT=8091
```

The Operational Intelligence orchestrator and agents use:

```text
app/operational-intelligence/orchestrator-agent/.env
```

Expected local content:

```text
GOOGLE_GENAI_USE_VERTEXAI=true
GOOGLE_CLOUD_PROJECT=ada26-pulse-project
GOOGLE_CLOUD_LOCATION=europe-west1
MODEL_NAME=gemini-2.5-flash-lite
KPI_MCP_URL=http://127.0.0.1:8091/mcp
```

Access-token based configuration, for example `GCP_ACCESS_TOKEN`, is lab/demo style only. Access tokens expire and should not be committed.

## Terminal Layout

Use separate terminals for each long-running service.

```text
Terminal 1: KPI Serving API, port 8080
Terminal 2: KPI MCP Server, port 8091
Terminal 3: ADK web or individual agent test
Terminal 4: Local orchestrator, port 8090
Terminal 5: curl or Invoke-RestMethod tests
```

## 1. Start KPI Serving API

The KPI Serving API validates the read layer over the BigQuery Gold table.

Install service requirements without changing `pyproject.toml`:

```powershell
cd "C:\Projects\Advanced Data Architectures\ada-pulse-2026"
uv pip install -r app\kpi-analytics\kpi-serving\requirements.txt
```

Start the service:

```powershell
cd "C:\Projects\Advanced Data Architectures\ada-pulse-2026\app\kpi-analytics\kpi-serving"
uv run python -m uvicorn main:app --reload --port 8080
```

Local URLs:

```text
API:  http://127.0.0.1:8080
Docs: http://127.0.0.1:8080/docs
```

Health check, from another terminal:

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
curl "http://127.0.0.1:8080/kpis/pulse-demo/metrics?domain=financial"
curl "http://127.0.0.1:8080/kpis/pulse-demo/latest?domain=financial"
curl "http://127.0.0.1:8080/kpis/pulse-demo/latest?domain=sales_crm"
curl "http://127.0.0.1:8080/kpis/pulse-demo/metrics/financial/burn_rate/history?limit=6"
```

The tenant path must be `pulse-demo`. Other tenant values return `404`.

## 2. Start KPI MCP Server

The KPI MCP server follows the Lab 6 REST-to-MCP pattern:

```text
KPI Serving API
-> REST wrapper endpoints
-> MCP tools
-> ADK agents
```

Location:

```text
app/kpi-analytics/kpi-mcp-server/
  app.py
  requirements.txt
  .env
  .gitignore
```

Install service requirements without changing `pyproject.toml`:

```powershell
cd "C:\Projects\Advanced Data Architectures\ada-pulse-2026"
uv pip install -r app\kpi-analytics\kpi-mcp-server\requirements.txt
```

Start the service:

```powershell
cd "C:\Projects\Advanced Data Architectures\ada-pulse-2026\app\kpi-analytics\kpi-mcp-server"
$env:KPI_DATA_API_URL="http://127.0.0.1:8080"
uv run python -m uvicorn app:app --reload --port 8091
```

Local URLs:

```text
API:          http://127.0.0.1:8091
MCP endpoint: http://127.0.0.1:8091/mcp
```

REST wrapper checks:

```powershell
curl http://127.0.0.1:8091/health
curl http://127.0.0.1:8091/tools/kpi/domains/pulse-demo
curl "http://127.0.0.1:8091/tools/kpi/metrics/pulse-demo?domain=financial"
curl "http://127.0.0.1:8091/tools/kpi/latest/pulse-demo?domain=financial"
curl "http://127.0.0.1:8091/tools/kpi/history/pulse-demo/financial/burn_rate?periods=6"
```

MCP tools exposed through `operation_id`:

```text
list_kpi_domains
list_kpis_in_domain
get_latest_kpis
get_kpi_history
```

Validate MCP with MCP Inspector:

```powershell
npx @modelcontextprotocol/inspector
```

Use this MCP endpoint in the Inspector:

```text
http://127.0.0.1:8091/mcp
```

Test these MCP tool calls:

```text
list_kpi_domains tenant_id=pulse-demo
list_kpis_in_domain tenant_id=pulse-demo domain=financial
get_latest_kpis tenant_id=pulse-demo domain=financial
get_kpi_history tenant_id=pulse-demo domain=financial metric_name=burn_rate periods=6
```

Continue only after the MCP tools return KPI data.

## 3. Validate ADK Agents

Location:

```text
app/operational-intelligence/orchestrator-agent/
  financial_agent/
    agent.py
  sales_crm_agent/
    agent.py
  synthesis_agent/
    agent.py
  mcp_tools.py
  orchestrator/
    __init__.py
    pipeline.py
  app.py
```

The plain `adk` command may point to a different CLI in this environment. Use the Google ADK Python module entrypoint.

Run each agent directly:

```powershell
cd "C:\Projects\Advanced Data Architectures\ada-pulse-2026\app\operational-intelligence\orchestrator-agent"
uv run python -m google.adk.cli run financial_agent
uv run python -m google.adk.cli run sales_crm_agent
uv run python -m google.adk.cli run synthesis_agent
```

When prompted for a user name, use a simple local value:

```text
local-user
```

Example financial prompt:

```text
Use tenant_id pulse-demo. Retrieve latest financial KPIs and 6 periods of history for burn_rate, cash_flow, revenue_growth, and outstanding_invoices. Return strict JSON only.
```

Start ADK web:

```powershell
cd "C:\Projects\Advanced Data Architectures\ada-pulse-2026\app\operational-intelligence\orchestrator-agent"
uv run python -m google.adk.cli web --port 8000 .
```

Open:

```text
http://127.0.0.1:8000
```

The ADK web UI should list:

```text
financial_agent
sales_crm_agent
synthesis_agent
```

If ADK web shows `No agents found in current folder`, the command was started from the wrong folder. Stop the server, move to `app/operational-intelligence/orchestrator-agent`, and start it again.

The `orchestrator/` folder is not an ADK app. It contains pipeline code for the FastAPI orchestrator.

## 4. Start Local Orchestrator

The local orchestrator is exposed by:

```text
app/operational-intelligence/orchestrator-agent/app.py
```

It calls:

```text
orchestrator/pipeline.py
```

Endpoints:

```text
GET /health
POST /pipeline/run
GET /pipeline/{run_id}/status
POST /pubsub/kpis-computed
```

The local `/pubsub/kpis-computed` endpoint is currently a placeholder. Use `/pipeline/run` for local manual testing.

Before starting the orchestrator, verify:

```text
1. KPI Serving API runs on http://127.0.0.1:8080.
2. KPI MCP Server runs on http://127.0.0.1:8091.
3. MCP Inspector can call the KPI tools.
4. orchestrator-agent/.env contains Vertex/Gemini and KPI_MCP_URL settings.
```

Start the orchestrator:

```powershell
cd "C:\Projects\Advanced Data Architectures\ada-pulse-2026\app\operational-intelligence\orchestrator-agent"
uv run python -m uvicorn app:app --reload --port 8090
```

Health check:

```powershell
curl http://127.0.0.1:8090/health
```

Expected response:

```json
{"status":"ok","service":"operational-intelligence-orchestrator"}
```

Manual pipeline run, PowerShell safe version:

```powershell
$body = @{
  tenant_id = "pulse-demo"
  trace_id = "trace-local-001"
  run_id = "manual-run-001"
  source_kpi_run_id = "kpi-run-local-001"
} | ConvertTo-Json

Invoke-RestMethod `
  -Method Post `
  -Uri "http://127.0.0.1:8090/pipeline/run" `
  -ContentType "application/json" `
  -Body $body
```

Check run status:

```powershell
curl http://127.0.0.1:8090/pipeline/manual-run-001/status
```

Expected pipeline behavior:

```text
1. Financial agent returns strict JSON.
2. Sales CRM agent returns strict JSON.
3. Synthesis agent combines both outputs.
4. Orchestrator returns one combined insight payload.
```

The pipeline strips markdown JSON code fences from agent output before JSON parsing. This handles common LLM responses that wrap JSON in triple backticks with a `json` label.

Example pattern:

```text
triple-backtick json
{ ... }
triple-backtick
```

## Troubleshooting

`uvicorn` returns `Could not import module "app"`:

```text
Cause: command started from the wrong folder, or app.py is missing.
Fix: run from app/operational-intelligence/orchestrator-agent.
```

ADK web shows `No agents found in current folder`:

```text
Cause: ADK web was started from orchestrator/ or another subfolder.
Fix: run from app/operational-intelligence/orchestrator-agent.
```

`uv run adk run financial_agent` returns an unrecognized argument error:

```text
Cause: the plain adk command points to another CLI.
Fix: use uv run python -m google.adk.cli run financial_agent.
```

PowerShell `curl -d` returns invalid JSON:

```text
Cause: quoting differences in PowerShell.
Fix: use Invoke-RestMethod with ConvertTo-Json.
```

Pipeline returns `Agent ... returned invalid JSON`:

```text
Cause: an agent returned text that is not JSON.
Fix: tighten the agent prompt or inspect the agent response in the error detail.
```

## Local Validation Checklist

Use this order before committing local Operational Intelligence work:

```text
1. git status reviewed.
2. gcloud project is ada26-pulse-project.
3. ADC quota project is ada26-pulse-project.
4. KPI Serving API /health works.
5. KPI Serving API returns financial and sales_crm data.
6. KPI MCP Server /health works.
7. MCP REST wrapper endpoints return KPI data.
8. MCP Inspector lists and executes the KPI tools.
9. ADK run works for financial_agent.
10. ADK run works for sales_crm_agent.
11. ADK run works for synthesis_agent.
12. Local orchestrator /health works.
13. Local orchestrator /pipeline/run returns a combined payload.
14. Only intentional files are staged.
```

## Notes

- Pipeline status for teammates: [CURRENT_STATE.md](CURRENT_STATE.md) (ingest, KPI function, serving API).
- Operational Intelligence plan: [docs/Operational-Intelligence-plan.md](docs/Operational-Intelligence-plan.md).

# Cloud Deployment Phase

### Phase 2. Google Cloud Services (GCS)

The following sections describe the deployment of the validated local implementation to Google Cloud Platform.

The objective of this phase is not to debug functionality, but to move the already validated local architecture into managed cloud infrastructure using:

- Cloud Run
- Cloud Functions
- Pub/Sub
- BigQuery
- GCS

Only continue with this phase after the Local Validation Checklist succeeds completely.

# Cloud Deployment via Google Cloud Console UI

This section describes the cloud deployment workflow using the Google Cloud Console UI. The deployment flow extends the local implementation and moves the services to managed Google Cloud infrastructure.

The target deployment flow is:

```text
Local repository
-> GCS ingest bucket
-> KPI Cloud Function
-> BigQuery Gold Layer
-> Pub/Sub
-> KPI Serving API on Cloud Run
-> KPI MCP Server on Cloud Run
-> Operational Intelligence Orchestrator on Cloud Run
-> insights-ready Pub/Sub topic
```

The UI-based deployment is suitable for:

- Assignment demonstrations
- Initial infrastructure setup
- Team onboarding
- Service inspection and debugging

CLI deployment remains preferable for automation and CI/CD, but the UI flow is fully valid for the Assignment 2 implementation.

## Cloud Architecture

The deployed architecture is:

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
        | push subscription
        v
Cloud Run: operational-intelligence-orchestrator
        |
        | MCP calls
        v
Cloud Run: kpi-mcp-server
        |
        | REST calls
        v
Cloud Run: kpi-serving
        |
        | queries
        v
BigQuery Gold Layer
```

## 5. Enable Required Google Cloud APIs

Open:

```text
Google Cloud Console
-> APIs & Services
-> Library
```

Enable these APIs:

```text
Cloud Run API
Cloud Functions API
Cloud Build API
Artifact Registry API
Pub/Sub API
BigQuery API
Eventarc API
Secret Manager API
Vertex AI API
Generative Language API
```

## 6. Create or Validate GCS Bucket

Open:

```text
Cloud Storage
```

Validate that the bucket exists:

```text
pulse-demo-bronze
```

If the bucket does not exist:

```text
Create Bucket
Name: pulse-demo-bronze
Region: choose the project region
Storage class: Standard
Access control: Uniform
```

## 7. Upload Ingest Files Through UI

Open:

```text
Cloud Storage
-> pulse-demo-bronze
```

Create a folder:

```text
ingest/test-run-001/
```

Upload:

```text
financial_clean.csv
sales_marketing_clean.csv
```

After both CSV files are uploaded, upload:

```text
ready.json
```

The ready.json upload should always be the final upload step because it triggers KPI computation.

## 8. Enable and Configure Pub/Sub

### 8.1 Create Pub/Sub topics

Open:

```text
Pub/Sub
-> Topics
```

Create:

```text
kpis-computed
insights-ready
```

### 8.2 Validate Pub/Sub activation

Open:

```text
Pub/Sub
-> Topics
```

Both topics should appear in the list.

## 9. Deploy KPI Cloud Function Through UI

Open:

```text
Cloud Functions
-> Create Function
```

Configuration:

```text
Name:
compute_kpis

Region:
us-central1

Environment:
2nd gen

Runtime:
Python 3.11
```

Trigger:

```text
Trigger Type:
Cloud Storage

Bucket:
pulse-demo-bronze

Event:
google.cloud.storage.object.v1.finalized
```

Entry point:

```text
compute_kpis
```

After deployment:

- upload ready.json
- verify KPI rows appear in BigQuery
- verify kpis-computed is published

## 10. Validate BigQuery Gold Layer

Open:

```text
BigQuery
```

Dataset:

```text
kpi_analytics_gold
```

Table:

```text
gold_kpi_snapshots
```

Validate that KPI rows appear after the Cloud Function execution.

## 11. Deploy KPI Serving API Through Cloud Run UI

Open:

```text
Cloud Run
-> Create Service
```

Configuration:

```text
Service Name:
kpi-serving

Region:
europe-west1

Authentication:
Allow unauthenticated invocations
```

Environment variables:

```text
PROJECT_ID=ada26-pulse-project
KPI_GOLD_TABLE=ada26-pulse-project.kpi_analytics_gold.gold_kpi_snapshots
```

After deployment, Cloud Run displays the Service URL.

This URL becomes:

```text
KPI_SERVING_URL
```

Validate:

```text
https://KPI_SERVING_URL/health
https://KPI_SERVING_URL/docs
```

## 12. Deploy KPI MCP Server Through Cloud Run UI

The KPI MCP Server follows the Lab 6 REST-to-MCP pattern.

Open:

```text
Cloud Run
-> Create Service
```

Configuration:

```text
Service Name:
kpi-mcp-server

Region:
europe-west1

Authentication:
Allow unauthenticated invocations
```

Environment variables:

```text
KPI_DATA_API_URL=https://KPI_SERVING_URL
```

This URL becomes:

```text
KPI_MCP_URL
```

Expected MCP endpoint:

```text
https://KPI_MCP_URL/mcp
```

## 13. Deploy Operational Intelligence Orchestrator Through Cloud Run UI

Open:

```text
Cloud Run
-> Create Service
```

Configuration:

```text
Service Name:
operational-intelligence-orchestrator

Region:
europe-west1

Authentication:
Allow unauthenticated invocations
```

Environment variables:

```text
GOOGLE_GENAI_USE_VERTEXAI=true
GOOGLE_CLOUD_PROJECT=ada26-pulse-project
GOOGLE_CLOUD_LOCATION=europe-west1
MODEL_NAME=gemini-2.5-flash-lite
KPI_MCP_URL=https://KPI_MCP_URL/mcp
```

Validate:

```text
https://OI_URL/health
```

## 14. Configure Pub/Sub Push Subscription Through UI

Open:

```text
Pub/Sub
-> Subscriptions
-> Create Subscription
```

Configuration:

```text
Subscription ID:
orchestrator-kpis-computed-sub

Topic:
kpis-computed

Delivery Type:
Push

Endpoint URL:
https://OI_URL/pubsub/kpis-computed
```

## 15. Publish Manual Pub/Sub Test Event Through UI

Open:

```text
Pub/Sub
-> Topics
-> kpis-computed
-> Publish Message
```

Message body:

```text
KPI computation completed
```

Attributes:

```text
tenant_id = pulse-demo
run_id = kpi-run-ui-001
trace_id = trace-ui-001
```

## 16. Validate Cloud Logs

Open:

```text
Cloud Run
-> operational-intelligence-orchestrator
-> Logs
```

Search for:

```text
trace-ui-001
```

Expected operations:

```text
run_pipeline
financial_intelligence_agent
sales_crm_intelligence_agent
insight_synthesis_agent
publish_insights_ready
```

## 17. Validate insights-ready Output

Open:

```text
Pub/Sub
-> Subscriptions
```

Create a temporary debug subscription:

```text
insights-ready-debug-sub
```

Pull messages and validate the final payload.

## 18. Full End-to-End Validation Flow

```text
1. Upload ingest files to GCS.
2. Upload ready.json.
3. Cloud Function starts KPI computation.
4. BigQuery Gold Layer is updated.
5. kpis-computed Pub/Sub event is published.
6. Pub/Sub triggers Operational Intelligence Orchestrator.
7. Orchestrator calls Financial and Sales agents.
8. Agents retrieve KPI data through KPI MCP Server.
9. Insight Synthesis Agent combines outputs.
10. Orchestrator publishes insights-ready.
11. Reporting & Delivery consumes insights-ready.
```

## 19. Cloud Deployment Validation Checklist

```text
1. Required Google Cloud APIs enabled.
2. GCS bucket pulse-demo-bronze exists.
3. Ingest files uploaded successfully.
4. ready.json uploaded last.
5. KPI Cloud Function deployed.
6. BigQuery Gold Layer populated.
7. Pub/Sub topics created.
8. KPI Serving API deployed to Cloud Run.
9. KPI MCP Server deployed to Cloud Run.
10. Operational Intelligence Orchestrator deployed.
11. Pub/Sub push subscription created.
12. Manual Pub/Sub test event succeeds.
13. Cloud logs show trace propagation.
14. insights-ready messages are published.
15. End-to-end flow validated successfully.
```

