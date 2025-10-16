# Architecture Overview

This document describes the proposed SQL Server monitoring platform that leverages OpenTelemetry metrics ingested into Elastic alongside live SQL Server diagnostics and LLM-assisted analysis.

## High-Level Flow

1. **Telemetry Ingestion**
   - The OpenTelemetry MSSQL receiver exports metrics, traces, and logs to the OpenTelemetry Collector.
   - A dedicated exporter forwards telemetry into Elastic, targeting indices partitioned by signal type (e.g., `mssql-metrics-*`, `mssql-logs-*`).
   - Elastic index lifecycle management retains detailed metrics for a short window and aggregates older data for trend analysis.

2. **Collector Bridge Service** (`src/collector_bridge/`)
   - Periodically queries Elastic for the latest MSSQL telemetry snapshots.
   - Normalizes heterogeneous documents (wait stats, query store, IO, blocking) into canonical response models consumed by the API/UI and analytics pipeline.
   - Provides REST endpoints through FastAPI for downstream services to request aggregated metrics or raw event streams.

3. **Analytics Service** (`src/analytics/`)
   - Formats summarized telemetry and live DMV output into contextual prompts.
   - Invokes local or remote Ollama LLM models to reason about performance regressions, blocking chains, and capacity planning issues.
   - Persists generated insights along with metadata (input metrics, model, timestamp) for auditing.

4. **Live Monitoring Connector** (`src/live_monitor/`)
   - Uses SQL Server DMVs for near real-time data (sessions, waits, blocking, top queries) when direct connections are permitted.
   - Supports scheduled snapshots and ad-hoc queries exposed via the API.

5. **API Gateway** (`src/api/`)
   - Consolidates telemetry-derived metrics, LLM analyses, and live DMV snapshots into a cohesive REST API.
   - Authentication and RBAC (future enhancement) ensure least privilege when requesting sensitive data or connecting to production SQL Server instances.

6. **UI / Integrations** (Future Work)
   - React or dashboard clients consume the API.
   - Webhooks and incident management integrations (PagerDuty, Teams) use analytics outputs for automated triage.

## Data Schemas

| Dataset | Source | Fields (Examples) |
|---------|--------|-------------------|
| `mssql-metrics-*` | OpenTelemetry → Elastic | `timestamp`, `instance_name`, `cpu_percent`, `wait_type`, `wait_time_ms`, `blocking_session_id`, `query_hash`, `physical_io_bytes` |
| `mssql-logs-*` | OpenTelemetry → Elastic | `timestamp`, `severity`, `message`, `log_category`, `instance_name` |
| `llm_insights` | Analytics Service | `generated_at`, `model`, `summary`, `recommended_actions`, `supporting_metrics` |
| `live_sessions` | SQL Server DMVs | `collection_time`, `session_id`, `status`, `wait_type`, `cpu_time`, `logical_reads`, `blocking_session_id` |

Normalisation routines convert Elastic hits into typed models (`collector_bridge.models`) to simplify consumption by the analytics and UI layers.

## Deployment Topology

```
+--------------------+      +------------------+       +------------------+
| SQL Server (DMVs)  |      | OpenTelemetry    |       | Elastic Cluster  |
|                    | ---> | Collector MSSQL  | --->  | mssql-* indices  |
+--------------------+      +------------------+       +------------------+
           |                          |                             |
           |                          v                             v
           |                +------------------+      +------------------------+
           |                | Collector Bridge |<----| Analytics (LLM/Ollama) |
           |                |  FastAPI Service |---->| Recommendations API    |
           |                +------------------+      +------------------------+
           |                          |
           v                          v
   +------------------+       +------------------+
   | Live Monitor API |       | Front-end / CLI  |
   +------------------+       +------------------+
```

## Operational Considerations

- **Configuration Management** – `config/settings.yaml` holds environment-specific Elastic, Ollama, and SQL Server connection details. Secrets should ultimately live in vault services or environment variables.
- **Security** – Implement API authentication, TLS for Elastic connections, and least privilege SQL logins.
- **Scalability** – Horizontal scale via container orchestration. Background workers can pre-compute aggregates to reduce query latency.
- **Observability** – The service emits OpenTelemetry traces/metrics for its operations, enabling dogfooding.
- **Testing & CI** – GitHub Actions workflow executes unit tests and linting to maintain quality.

## Future Enhancements

- Alerting rules using Elastic Watcher or custom jobs.
- Historical baselining and anomaly detection leveraging ML models.
- UI dashboards with drill-downs similar to commercial tools (Idera, SolarWinds).
- Integration with incident management platforms.
