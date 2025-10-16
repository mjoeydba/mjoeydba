# SQL Server Monitoring Best Practices & OSS Resources

## Monitoring Focus Areas

1. **Wait Statistics** – Track cumulative waits and wait categories to identify resource contention (CPU, IO, locking). Baseline against typical workload patterns.
2. **Session Activity & Blocking** – Monitor active sessions, blocking chains, and head blockers to rapidly triage user impact.
3. **Query Performance** – Review top resource-consuming queries, plan regressions, and query store history.
4. **Resource Utilization** – Capture host-level CPU, memory, storage throughput, and tempdb usage to correlate with SQL metrics.
5. **Backup & Maintenance** – Validate job success, durations, and maintenance plan adherence.
6. **High Availability** – Observe Availability Group synchronization state, replica latency, and failover readiness.

## Operational Practices

- **Baseline Collection** – Gather historical metrics to compute adaptive thresholds rather than static alerting.
- **Automated Alerting** – Combine Elastic Watcher, webhook notifications, and runbook automation to shorten MTTR.
- **Security & Compliance** – Audit access, encrypt connections, and mask sensitive data when exporting telemetry.
- **Observability Integration** – Export collector service metrics using OpenTelemetry for full-stack tracing.
- **Capacity Planning** – Trend growth in database size, log usage, and IO saturation to forecast upgrades.

## Influential OSS Scripts

| Script | Source | Purpose | Integration Notes |
|--------|--------|---------|-------------------|
| `sp_WhoIsActive` (Adam Machanic) | [GitHub](https://github.com/amachanic/sp_whoisactive) | Deep session & blocking insight | Use as reference for DMV queries in `live_monitor/dmv_queries.py`. |
| Ola Hallengren Maintenance Solution | [ola.hallengren.com](https://ola.hallengren.com/) | Backup, integrity, index maintenance | Surface job runtimes & failures through telemetry and live DMV checks. |
| Brent Ozar First Responder Kit | [firstresponderkit.org](https://www.brentozar.com/first-aid/) | sp_Blitz, sp_BlitzCache, sp_BlitzFirst for health checks | Map critical findings to LLM prompts for remediation suggestions. |
| `dbatools` PowerShell Module | [dbatools.io](https://dbatools.io/) | Operational automation (migrations, checks) | Align API endpoints to trigger automation workflows where appropriate. |

These resources guide the SQL queries, metrics, and remediation content that the analytics layer should understand. Aligning with community knowledge accelerates adoption and credibility.
