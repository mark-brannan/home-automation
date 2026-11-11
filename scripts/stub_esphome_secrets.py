#!/usr/bin/env python3
"""Write esphome/secrets.yaml with placeholder values, for `esphome config` in CI.

CI holds no decryption key. The key names in a sops YAML file are cleartext,
so read those and invent a value of the right shape for each: a base64 32-byte
string where the name says key, otherwise a plain 12-character string.
"""
import base64
import re
import sys
from pathlib import Path

SRC = Path("esphome/secrets.sops.yaml")
DST = Path("esphome/secrets.yaml")


def names(text):
    return [m.group(1) for m in re.finditer(r"^([A-Za-z_][\w-]*):", text, re.M) if m.group(1) != "sops"]


def placeholder(name):
    if "key" in name.lower():
        return base64.b64encode(b"0" * 32).decode()
    return "placeholder0000"


def main():
    keys = names(SRC.read_text()) if SRC.exists() else []
    DST.write_text("".join(f'{k}: "{placeholder(k)}"\n' for k in keys))
    print(f"wrote {DST} with {len(keys)} placeholder secret(s)", file=sys.stderr)


if __name__ == "__main__":
    main()
