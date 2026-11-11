# Working conventions: home-automation

ESPHome device configs, Home Assistant config and the bridge scripts for the
home and the desk. Layout is in [README.md](README.md).

## Secrets
- Plaintext `secrets.yaml` is gitignored and never committed; only
  `esphome/secrets.sops.yaml` (sops, age) is. Decrypt locally to build.
- Never print a decrypted value, paste one into an issue or a commit
  message, or commit a device's API key or WiFi password.
- `scripts/verify_encrypted.py` (pre-commit) fails on a tracked
  `secrets.yaml` or a `*.sops.*` file that is not really encrypted.

## Workflow
- Private repo, no PRs, no CI: commit straight to `main`. Do not open PRs or add workflows.

## Checks before committing
- `yamllint --strict .`
- `python3 scripts/verify_encrypted.py`
- For a device YAML: `python3 scripts/stub_esphome_secrets.py && esphome config esphome/<device>.yaml`
- Tool versions: `requirements-ci.txt`.
