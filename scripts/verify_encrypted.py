#!/usr/bin/env python3
"""Fail if git tracks a plaintext secret file.

Two rules, checked against what git has committed (`git ls-files`, content
from the index), so a gitignored working copy never matters:

1. No tracked file is named `secrets.yaml` / `secrets.yml` (ESPHome's plaintext
   secrets; only `secrets.sops.yaml` may be committed).
2. Every tracked `*.sops.yaml|yml|json|env` carries sops metadata with a `mac`
   and a `version`, i.e. sops really encrypted it.

Local hooks can be skipped; this runs in CI on every push. Pattern after
symphony's verify_encrypted.sh.
"""
import re
import subprocess
import sys

PLAINTEXT = re.compile(r"(^|/)secrets\.ya?ml$")
SOPS_FILE = re.compile(r"(^|/)[^/]+\.sops\.(ya?ml|json|env)$")


def is_sops_encrypted(text):
    """True when the text carries sops metadata with a mac and a version."""
    if re.search(r'"sops"\s*:\s*\{', text):  # JSON
        return bool(re.search(r'"mac"\s*:', text) and re.search(r'"version"\s*:', text))
    if re.search(r"^sops:\s*$", text, re.M):  # YAML
        return bool(re.search(r"^\s+mac:", text, re.M) and re.search(r"^\s+version:", text, re.M))
    if re.search(r"^sops_mac=", text, re.M):  # dotenv
        return bool(re.search(r"^sops_version=", text, re.M))
    return False


def tracked():
    out = subprocess.run(["git", "ls-files", "-z"], check=True, capture_output=True).stdout
    return [p for p in out.decode().split("\0") if p]


def check(paths, read):
    problems = []
    for p in paths:
        if PLAINTEXT.search(p):
            problems.append("PLAINTEXT SECRETS FILE TRACKED: " + p)
        elif SOPS_FILE.search(p) and not is_sops_encrypted(read(p)):
            problems.append("NOT ENCRYPTED: " + p)
    return problems


def self_test():
    enc_yaml = "key: ENC[AES256_GCM,data:x]\nsops:\n  mac: ENC[x]\n  version: 3.9.0\n"
    assert is_sops_encrypted(enc_yaml)
    assert not is_sops_encrypted("wifi_password: hunter2\n")
    assert not is_sops_encrypted("sops:\n  note: forged, no mac\n")
    assert is_sops_encrypted('{"a": "ENC[x]", "sops": {"mac": "ENC[x]", "version": "3.9"}}')
    files = {"esphome/secrets.sops.yaml": "wifi: hunter2\n", "esphome/ok.sops.yaml": enc_yaml}
    got = check(["esphome/secrets.yaml", "a/secrets.yml", *files], files.get)
    assert got == [
        "PLAINTEXT SECRETS FILE TRACKED: esphome/secrets.yaml",
        "PLAINTEXT SECRETS FILE TRACKED: a/secrets.yml",
        "NOT ENCRYPTED: esphome/secrets.sops.yaml",
    ], got
    print("self-test OK")


def main():
    if "--self-test" in sys.argv:
        return self_test()
    def read(p):
        return subprocess.run(["git", "show", ":" + p], check=True, capture_output=True, text=True).stdout
    paths = tracked()
    problems = check(paths, read)
    if problems:
        print("\n".join(problems), file=sys.stderr)
        print("\nA secret must never be committed in plaintext. Do not push; "
              "see README 'Secrets'.", file=sys.stderr)
        sys.exit(1)
    n = sum(1 for p in paths if SOPS_FILE.search(p))
    print(f"OK: {n} sops file(s) encrypted as committed; no plaintext secrets.yaml tracked.")


if __name__ == "__main__":
    main()
