import json
import os
import sys
import time
from pathlib import Path

from client import NfaApiError, NfaCommercialClient


PRODUCT = "gexbot"
LEVEL = "classic"
ONE_YEAR_SECONDS = 365 * 24 * 60 * 60


def main():
    load_env()

    client = NfaCommercialClient(api_key=os.environ["NFA_API_KEY"])

    result = client.create_child(
        level=LEVEL,
        product=PRODUCT,
        label=f"api_demo_{int(time.time())}",
        expires_in=ONE_YEAR_SECONDS,
    )

    print(json.dumps(result, indent=2))


def load_env():
    env_path = Path(__file__).resolve().parents[1] / ".env"
    if not env_path.exists():
        return

    for line in env_path.read_text(encoding="utf-8").splitlines():
        trimmed = line.strip()
        if not trimmed or trimmed.startswith("#") or "=" not in trimmed:
            continue

        key, value = trimmed.split("=", 1)
        if key and key not in os.environ:
            os.environ[key] = value.strip("\"'")


if __name__ == "__main__":
    try:
        main()
    except NfaApiError as error:
        print("API request failed", file=sys.stderr)
        print(f"METHOD: {error.method}", file=sys.stderr)
        print(f"URL: {error.url}", file=sys.stderr)
        print("HEADERS:", file=sys.stderr)
        print(json.dumps(error.request_headers, indent=2), file=sys.stderr)
        print("REQUEST BODY:", file=sys.stderr)
        print(json.dumps(error.request_body, indent=2), file=sys.stderr)
        print(f"STATUS: {error.status}", file=sys.stderr)
        print("RESPONSE BODY:", file=sys.stderr)
        print(json.dumps(error.body, indent=2), file=sys.stderr)
        sys.exit(1)
    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
