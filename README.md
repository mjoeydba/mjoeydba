# SQL Server Observability Platform

This repository hosts an open monitoring platform that correlates OpenTelemetry MSSQL metrics ingested into Elastic with direct SQL Server diagnostics and LLM-guided remediation via Ollama.

## Project Highlights

- **Collector Bridge** – FastAPI service that queries Elastic for recent telemetry, normalizes metrics, and exposes REST endpoints.
- **LLM Analytics** – Prompt engineering utilities that summarize telemetry and DMV output, calling Ollama for contextual recommendations.
- **Live Monitoring** – Direct SQL Server connector for on-demand DMV snapshots covering waits, blocking, sessions, and top queries.
- **Research-Driven Roadmap** – Competitive analysis and best-practice documentation inform feature priorities.

## Getting Started

1. Install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. Configure environment values in `config/settings.yaml` or set `APP_CONFIG_FILE` to a custom path.
3. Launch the API:
   ```bash
   uvicorn src.api.app:create_app --factory --reload
   ```
4. Explore the API docs at `http://localhost:8000/docs`.

## Documentation

- [Architecture Overview](docs/architecture.md)
- [Competitive Landscape](docs/research/competitive_landscape.md)
- [Best Practices & OSS Resources](docs/research/best_practices.md)

## Roadmap

- Enrich telemetry aggregation with trend analysis and baselining.
- Extend LLM analytics with scenario-specific prompt templates (blocking, capacity, HA).
- Build a React dashboard for visualization and alert triage.
- Integrate alerting workflows with Elastic Watcher and messaging platforms.

## Contributing

Issues and pull requests are welcome. Please run tests before submitting changes:

```bash
pytest
```

## License

This project is released under the MIT License. See `LICENSE` (to be added) for details.
