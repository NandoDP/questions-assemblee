"""Test simple du endpoint local /api/superset/guest-token.

Usage:
    python test_guest_token_endpoint.py

Variables optionnelles:
    API_BASE_URL=http://127.0.0.1:5001
    DASHBOARD_ID=1
"""

import os
import sys

import requests


API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:5001").rstrip("/")
DASHBOARD_ID = os.getenv("DASHBOARD_ID", "1")


def main() -> int:
    url = f"{API_BASE_URL}/api/superset/guest-token"
    response = requests.get(url, params={"dashboardId": DASHBOARD_ID}, timeout=30)

    print(f"GET {response.url}")
    print(f"Status: {response.status_code}")

    try:
        payload = response.json()
    except ValueError:
        print("Réponse non JSON:")
        print(response.text)
        return 1

    if response.ok:
        token = payload.get("token", "")
        print("guest-token: OK")
        print(f"dashboardId: {payload.get('dashboardId')}")
        print(f"supersetDomain: {payload.get('supersetDomain')}")
        print(f"token_prefix: {token[:24]}...")
        return 0

    print("guest-token: ECHEC")
    print(payload)
    return 1


if __name__ == "__main__":
    sys.exit(main())