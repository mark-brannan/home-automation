#!/usr/bin/env python3
"""
Drive Home Assistant's first-run onboarding wizard via its internal REST
endpoints, so the only thing left in the web UI is anything these calls
can't reach (e.g. picking specific integrations to set up).

These endpoints (/api/onboarding/*) are NOT a documented/stable public API
-- they're what the onboarding frontend itself calls, reverse-engineered
from Home Assistant core's test suite (tests/components/onboarding/).
They can change between core versions. If a step 400s, the fallback is
always: open http://<host>:8123 and finish that one step by hand.

Usage:
    python3 onboard.py --host 192.168.0.XXX \
        --name "Solace" --username admin --password '...' \
        --location-name Home --lat 00.0 --lon -000.0 \
        --elevation 0 --unit-system metric --time-zone America/Los_Angeles

Only run this against a Home Assistant instance that has never been
onboarded (fresh flash). It will refuse to run otherwise.
"""
import argparse
import sys
import requests


def api(host):
    return f"http://{host}:8123/api"


def onboarding_status(host):
    r = requests.get(f"{api(host)}/onboarding", timeout=10)
    r.raise_for_status()
    return r.json()  # list of {"step": "...", "done": bool}


def step_done(status, step):
    return any(s["step"] == step and s["done"] for s in status)


def create_user(host, name, username, password, language="en"):
    r = requests.post(
        f"{api(host)}/onboarding/users",
        json={
            "client_id": f"http://{host}:8123/",
            "name": name,
            "username": username,
            "password": password,
            "language": language,
        },
        timeout=10,
    )
    r.raise_for_status()
    return r.json()  # {"auth_code": "...", ...}


def exchange_token(host, auth_code):
    r = requests.post(
        f"http://{host}:8123/auth/token",
        data={
            "grant_type": "authorization_code",
            "code": auth_code,
            "client_id": f"http://{host}:8123/",
        },
        timeout=10,
    )
    r.raise_for_status()
    return r.json()["access_token"]


def core_config(host, token, location_name, lat, lon, elevation, unit_system, time_zone):
    r = requests.post(
        f"{api(host)}/onboarding/core_config",
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )
    # core_config onboarding step just triggers default location detection;
    # explicit values are set afterwards via the normal config/core API.
    r.raise_for_status()
    r2 = requests.post(
        f"{api(host)}/config/core/config",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "location_name": location_name,
            "latitude": lat,
            "longitude": lon,
            "elevation": elevation,
            "unit_system": unit_system,
            "time_zone": time_zone,
        },
        timeout=15,
    )
    r2.raise_for_status()


def finish_integration_step(host, token):
    r = requests.post(
        f"{api(host)}/onboarding/integration",
        headers={"Authorization": f"Bearer {token}"},
        json={"client_id": f"http://{host}:8123/"},
        timeout=15,
    )
    r.raise_for_status()


def finish_analytics_step(host, token):
    r = requests.post(
        f"{api(host)}/onboarding/analytics",
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )
    # Non-fatal if this one 404s on older/newer core -- analytics opt-in
    # can be set later in the UI either way.
    if r.status_code not in (200, 404):
        print(f"  (analytics step returned {r.status_code}, continuing)", file=sys.stderr)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--host", required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--username", required=True)
    p.add_argument("--password", required=True)
    p.add_argument("--location-name", default="Home")
    p.add_argument("--lat", type=float, required=True)
    p.add_argument("--lon", type=float, required=True)
    p.add_argument("--elevation", type=int, default=0)
    p.add_argument("--unit-system", default="metric", choices=["metric", "us_customary"])
    p.add_argument("--time-zone", required=True)
    args = p.parse_args()

    status = onboarding_status(args.host)
    print("Current onboarding status:", status)

    if step_done(status, "user"):
        print("User step already done -- refusing to run against an "
              "already-onboarded instance. Finish setup in the web UI.")
        sys.exit(1)

    print("== creating admin user ==")
    result = create_user(args.host, args.name, args.username, args.password)
    token = exchange_token(args.host, result["auth_code"])
    print("  got access token")

    print("== setting location/timezone/units ==")
    core_config(args.host, token, args.location_name, args.lat, args.lon,
                args.elevation, args.unit_system, args.time_zone)

    print("== finishing integration-discovery step ==")
    finish_integration_step(args.host, token)

    print("== finishing analytics step ==")
    finish_analytics_step(args.host, token)

    print()
    print(f"Done. Log in at http://{args.host}:8123 as '{args.username}'.")
    print("From there: Settings > Add-ons > Add-on Store for ESPHome, "
          "Mosquitto, SSH & Web Terminal, etc.")


if __name__ == "__main__":
    main()
