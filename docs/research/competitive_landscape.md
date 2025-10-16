# Competitive Landscape: SQL Server Monitoring

This document summarizes publicly available information about commercial SQL Server monitoring platforms to inform feature planning for our open solution.

## Idera SQL Diagnostic Manager (IDM)

- **Performance Dashboards** – Real-time and historical dashboards for CPU, memory, IO, waits, and sessions with customizable baselines.
- **Alerting & Notifications** – Configurable thresholds with email, SNMP, and webhook integrations; includes advisory actions based on best practices.
- **Query Performance Analytics** – Deadlock detection, plan statistics, and query wait analysis with recommendations.
- **Tempdb & Storage Monitoring** – Specialized views for tempdb contention, disk space, and IO hotspots.
- **Cloud & Hybrid Support** – Supports Azure SQL Database, Managed Instance, and AWS RDS in addition to on-prem SQL Server.
- **Mobile & Web UI** – Lightweight web interface and mobile apps for alert triage.

## SolarWinds SQL Sentry

- **Top SQL & Blocking Analysis** – Rich blocking chains, query plans, and history with root-cause workflows.
- **Always On & Availability Group Monitoring** – Dashboards for replication lag, failover readiness, and synchronization status.
- **Advisory Conditions** – Rule engine with template-based alerting and recommended fixes.
- **Event Calendar** – Correlates system events (jobs, backups) with performance spikes.
- **Resource Monitoring** – Wait stats, storage IO, and Windows host metrics with customizable baselines.
- **Integration** – Connects with SolarWinds Orion platform for cross-stack visibility.

## Feature Implications for Our Project

| Capability | IDM | SQL Sentry | Project Direction |
|------------|-----|------------|-------------------|
| Telemetry ingestion from Elastic | ✖ | ✖ | ✅ (core differentiator) |
| LLM-guided remediation | ✖ | ✖ | ✅ via Ollama |
| Blocking visualization | ✅ | ✅ | Planned via DMV collectors and Elastic snapshots |
| Availability Group insights | ✅ | ✅ | Roadmap item using Extended Events telemetry |
| Automation & alerting | ✅ | ✅ | Planned via workflow engine + Elastic Watcher |
| Mobile experience | ✅ | ✅ | Deferred |

Commercial tools emphasize curated dashboards, proactive alerts, and deep blocking analysis. Our roadmap should prioritize parity for critical diagnostics while leveraging LLM-driven insights and open standards.
