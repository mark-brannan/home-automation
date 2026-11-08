# home-automation

ESPHome device configs and Home Assistant config for the home and the desk.

## Layout

| Path | What lives there |
|---|---|
| `esphome/` | One YAML per device; `common/` holds shared blocks (wifi, api, logging). |
| `esphome/secrets.sops.yaml` | WiFi and API secrets, sops-encrypted. Decrypt to `esphome/secrets.yaml` (gitignored) to build. |
| `homeassistant/` | Home Assistant config directory. |
| `bridge/` | Scripts that carry device data to consumers outside Home Assistant. |
| `docs/` | Design notes and decisions. |

## Secrets

`.sops.yaml` names who can decrypt. Plaintext `secrets.yaml` never enters git.

```bash
sops -d esphome/secrets.sops.yaml > esphome/secrets.yaml
```

## Checks

CI (`.github/workflows/`) runs yamllint, a plaintext-secrets check
(`scripts/verify_encrypted.py`), `esphome config` over `esphome/*.yaml`, and a
full-history secret scan. The same secrets check runs locally through
pre-commit (`.pre-commit-config.yaml`). Conventions for agents: `CLAUDE.md`.
