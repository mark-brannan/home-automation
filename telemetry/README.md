# telemetry

An OpenTelemetry collector taking OTLP from Claude Code, with metrics kept in
VictoriaMetrics and logs and events in VictoriaLogs. The folder stands alone:
copy it to any Docker host and it comes up empty and starts taking data.

```bash
docker compose up -d      # from this folder
docker compose down       # stop; data stays in the named volumes
```

## Settings

| Env var | Default | What it does |
|---|---|---|
| `TELEMETRY_BIND` | `127.0.0.1` | Address the collector listens on; `0.0.0.0` to take data from the LAN. |
| `CLAUDE_CHECKOUT` | unset | Path to a `mark-brannan/claude` checkout; Grafana reads its dashboards (not yet used). |

## Ports

| Port | Service |
|---|---|
| 4317, 4318 | Collector, OTLP gRPC and HTTP, on `TELEMETRY_BIND` |
| 8428 | VictoriaMetrics, query API, localhost only |
| 9428 | VictoriaLogs, query API, localhost only |

Metrics are kept 12 months and logs 90 days, set in `compose.yaml`.
