import json
import os
import sys
import time
from pathlib import Path

from client import NfaApiError, NfaCommercialClient


PRODUCT = "gexbot"
INTEGRATION = "custom"
ONE_YEAR_SECONDS = 365 * 24 * 60 * 60


def main():
    load_local_env()

    client = NfaCommercialClient(
        base_url=os.environ.get("NFA_BASE_URL", "https://business.gexbot.com"),
        api_key=os.environ.get("NFA_API_KEY"),
    )

    # Read-only access check: lists children without creating or revoking keys.
    list_existing_children(client)

    # Production-style workflows you can adapt in your backend:
    #
    # provision_child_for_customer(client, customer_id="customer_123")
    # batch_provision_children(client, customer_ids=["customer_123", "customer_456"])
    # rotate_child_key(client, child_id="child_id_here", key_id="key_id_here")
    # revoke_child_access(client, child_id="child_id_here")


def list_existing_children(client):
    print_json(client.list_children())


def provision_child_for_customer(client, customer_id):
    """Create one child user and store the fields needed to manage it later."""
    result = client.create_child(
        product=PRODUCT,
        integration=INTEGRATION,
        label=f"{customer_id}_{int(time.time())}",
        expires_in=ONE_YEAR_SECONDS,
    )

    access_record = child_access_record(customer_id, result)
    store_child_access_record(access_record)

    return result


def batch_provision_children(client, customer_ids):
    """Create keys for several customers. Add retries/idempotency in production."""
    results = {}
    for customer_id in customer_ids:
        results[customer_id] = provision_child_for_customer(client, customer_id)
    return results


def rotate_child_key(client, child_id, key_id):
    """Rotate a specific child key and store the replacement key metadata."""
    result = client.rotate_child_key(child_id, key_id, expires_in=ONE_YEAR_SECONDS)
    access_record = rotated_key_access_record(child_id, result)
    store_rotated_key_access_record(access_record)
    return result


def revoke_child_access(client, child_id):
    """Revoke a child user's access. The backend treats this as deletion."""
    return client.delete_child(child_id)


def child_access_record(customer_id, result):
    if not isinstance(result, dict):
        raise ValueError("Expected child creation response object")

    api_key = first_api_key(result)
    return {
        "customer_id": customer_id,
        "child_id": required_field(result, "id", "child id"),
        "api_key_id": required_field(api_key, "id", "API key id"),
        "api_key_secret": required_field(api_key, "secret", "one-time API key secret"),
        "product": api_key.get("product"),
        "integration": api_key.get("integration"),
        "label": api_key.get("label"),
        "expires_at": api_key.get("expires_at"),
    }


def rotated_key_access_record(child_id, result):
    api_key = first_api_key(result)
    return {
        "child_id": child_id,
        "api_key_id": required_field(api_key, "id", "API key id"),
        "api_key_secret": required_field(api_key, "secret", "one-time API key secret"),
        "product": api_key.get("product"),
        "integration": api_key.get("integration"),
        "label": api_key.get("label"),
        "expires_at": api_key.get("expires_at"),
    }


def first_api_key(result):
    if not isinstance(result, dict):
        raise ValueError("Expected API response object")

    if result.get("id") and result.get("secret"):
        return result

    api_keys = result.get("api_keys") or []
    for api_key in api_keys:
        if api_key.get("id"):
            return api_key

    raise ValueError("Response did not include an API key")


def required_field(record, field_name, description):
    value = record.get(field_name)
    if not value:
        raise ValueError(f"Response did not include {description}")
    return value


def store_child_access_record(record):
    # Replace this with your secret manager or encrypted application database.
    _ = record
    print(f"Store child id, API key id, and one-time secret for customer {record['customer_id']}.")


def store_rotated_key_access_record(record):
    # Replace this with your secret manager or encrypted application database.
    _ = record
    print(f"Store replacement API key id and one-time secret for child {record['child_id']}.")


def print_json(value):
    print(json.dumps(value, indent=2))


def load_local_env():
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
