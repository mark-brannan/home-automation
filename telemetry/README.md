# telemetry

An OpenTelemetry collector taking OTLP from Claude Code, with metrics kept in
VictoriaMetrics and logs and events in VictoriaLogs, and a Grafana over both
(apart from the boat stack's). The folder stands alone:
copy it to any Docker host and it comes up empty and starts taking data.

```bash
docker compose up -d      # from this folder
docker compose down       # stop; data stays in the named volumes
```

## Settings

| Env var | Default | What it does |
|---|---|---|
| `GRAFANA_ADMIN_PASSWORD` | required | Grafana `admin` password, set on first start only; later, change it in the UI. |
| `TELEMETRY_BIND` | `127.0.0.1` | Address the collector and Grafana listen on; `0.0.0.0` to open them to the LAN. |
| `CLAUDE_CHECKOUT` | unset | Path to a `mark-brannan/claude` checkout; Grafana loads its `dashboards/`. |
| `CLAUDE_METRICS_DB_DIR` | unset | Folder holding `metrics.db` from `bin/metrics-db`; unset, the SQLite panels show nothing. |

## Ports

| Port | Service |
|---|---|
| 3030 | Grafana, on `TELEMETRY_BIND`; anonymous viewers; `admin` with `GRAFANA_ADMIN_PASSWORD` |
| 4317, 4318 | Collector, OTLP gRPC and HTTP, on `TELEMETRY_BIND` |
| 8428 | VictoriaMetrics, query API, localhost only |
| 9428 | VictoriaLogs, query API, localhost only |

Grafana's data sources and dashboard provider are files under `grafana/provisioning/`;
its three plugins are pinned in `compose.yaml` and fetched on first start.
Metrics are kept 12 months and logs 90 days, set in `compose.yaml`.
