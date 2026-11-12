# home-automation

ESPHome device configs and Home Assistant config for the home and the desk.

## Home Assistant

http://homeassistant.local/ (192.168.0.142), plain port 80, no `:8123`. `.local` resolves from Windows, not from WSL; from WSL use the IP.

## Layout

| Path | What lives there |
|---|---|
| `esphome/` | One YAML per device; `common/` holds shared blocks (wifi, api, logging). |
| `esphome/secrets.sops.yaml` | WiFi and API secrets, sops-encrypted. Decrypt to `esphome/secrets.yaml` (gitignored) to build. |
| `homeassistant/` | Home Assistant config directory. |
| `bridge/` | Scripts that carry device data to consumers outside Home Assistant. |
| `docs/` | Design notes and decisions. |
| `telemetry/` | Self-contained Claude telemetry stack: OTel collector, VictoriaMetrics, VictoriaLogs. |

## Secrets

`.sops.yaml` names who can decrypt. Plaintext `secrets.yaml` never enters git.

```bash
sops -d esphome/secrets.sops.yaml > esphome/secrets.yaml
```

## Checks

No PRs and no CI: the repo is private and commits go straight to `main`
(GitHub Actions needs a paid plan or a public repo). The checks run locally:
`yamllint --strict .`, `scripts/verify_encrypted.py` (also a pre-commit hook,
`.pre-commit-config.yaml`) and `esphome config` per device.
Conventions for agents: `CLAUDE.md`.
