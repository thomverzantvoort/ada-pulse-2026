### Reporting & Delivery

The Reporting & Delivery layer is deployed to GCP Cloud Run. It subscribes to the
`insights-ready` Pub/Sub topic and automatically generates and delivers an HTML
intelligence report via email when the Orchestrator completes its agent pipeline.

#### Deployed Cloud Run service

| Service | Description |
|---|---|
| `pulse-reporting-delivery` | Reporting & Delivery service — receives insight payloads and delivers HTML reports via email |

#### Pub/Sub push subscription

A push subscription named `insights-ready-push-reporting` connects the `insights-ready` topic
to the Reporting & Delivery service. When the Orchestrator publishes to `insights-ready`,
GCP automatically POSTs the message to the Reporting & Delivery service on Cloud Run.

#### Reporting & Delivery flow

The service consists of three components:

- `renderer.py` — transforms the structured insight JSON payload into a styled HTML report,
  organized by domain (financial, sales/CRM) and cross-domain compound risks, with
  severity badges and trend indicators per metric.

- `email_sender.py` — delivers the rendered HTML report via Gmail SMTP to the configured
  recipient. Credentials are managed through Cloud Run environment variables and are
  never committed to the repository.

- `main.py` — FastAPI application that receives the Pub/Sub push message, decodes the
  base64 payload, invokes the renderer, and triggers email delivery. Also exposes a
  `/health` endpoint and a `/test` endpoint for local development without Pub/Sub.

#### Environment variables

The service requires the following environment variables, configured in Cloud Run:

| Variable | Purpose |
|---|---|
| `GMAIL_SENDER` | Gmail address used as the report sender |
| `GMAIL_APP_PASSWORD` | Gmail App Password for SMTP authentication |
| `REPORT_RECIPIENT` | Email address of the report recipient |

These variables are set directly in the Cloud Run service configuration and are never
stored in the repository.