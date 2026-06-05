import json
import re
import time
import urllib.error
import urllib.request


DEFAULT_BASE_URL = "https://business.gexbot.com"
DEFAULT_EXPIRES_IN = 365 * 24 * 60 * 60


class NfaApiError(Exception):
    def __init__(self, method, url, status, reason, body, request_headers, request_body=None):
        self.method = method
        self.url = url
        self.status = status
        self.reason = reason
        self.body = body
        self.request_body = request_body
        self.request_headers = _redact_headers(request_headers)
        super().__init__(f"{method} {url} failed ({status}): {reason}")


class NfaCommercialClient:
    def __init__(self, api_key, base_url=DEFAULT_BASE_URL):
        if not api_key:
            raise ValueError("NFA_API_KEY is required")

        if not base_url.startswith(("http://", "https://")):
            base_url = f"https://{base_url}"

        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def request(self, path, method="GET", body=None):
        payload = None
        if body is not None:
            payload = json.dumps(body).encode("utf-8")

        url = f"{self.base_url}{path}"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        request = urllib.request.Request(
            url,
            data=payload,
            method=method,
            headers=headers,
        )

        try:
            with urllib.request.urlopen(request) as response:
                return _read_response_body(response)
        except urllib.error.HTTPError as error:
            response_body = _read_response_body(error)
            reason = response_body.get("message") if isinstance(response_body, dict) else error.reason
            raise NfaApiError(
                method,
                url,
                error.code,
                reason,
                response_body,
                request_headers=headers,
                request_body=body,
            ) from None

    def list_children(self):
        return self.request("/user/children")

    def get_child(self, child_id):
        return self.request(f"/user/children/{child_id}")

    def create_child(
        self,
        product="gexbot",
        integration="custom",
        label=None,
        expires_in=DEFAULT_EXPIRES_IN,
    ):
        return self.request(
            "/user/children",
            method="POST",
            body={
                "product": product,
                "integration": integration,
                "label": label or _default_label(),
                "expires_in": expires_in,
            },
        )

    def delete_child(self, child_id):
        return self.request(f"/user/children/{child_id}", method="DELETE")

    def create_child_key(
        self,
        child_id,
        product="gexbot",
        integration="custom",
        label=None,
        expires_in=DEFAULT_EXPIRES_IN,
    ):
        return self.request(
            f"/user/children/{child_id}/key",
            method="POST",
            body={
                "product": product,
                "integration": integration,
                "label": label or _default_label(),
                "expires_in": expires_in,
            },
        )

    def rotate_child_key(self, child_id, key_id, expires_in=DEFAULT_EXPIRES_IN):
        return self.request(
            f"/user/children/{child_id}/key",
            method="PATCH",
            body={
                "product": "gexbot",
                "id": raw_api_key_id(key_id),
                "expires_in": expires_in,
            },
        )

    def revoke_child_key(self, child_id, key_id):
        return self.request(
            f"/user/children/{child_id}/key",
            method="DELETE",
            body={
                "product": "gexbot",
                "id": raw_api_key_id(key_id),
            },
        )

def raw_api_key_id(key_id):
    key_id = re.sub(r"^gexbot_[^_]+_", "", key_id)
    return re.sub(r"^nfa_", "", key_id)


def _redact_headers(headers):
    sensitive_headers = {
        "authorization",
        "ocp-apim-subscription-key",
        "x-api-key",
    }

    return {
        name: "<redacted>" if name.lower() in sensitive_headers else value
        for name, value in headers.items()
    }


def _default_label():
    return f"custom_{int(time.time() * 1000)}"


def _read_response_body(response):
    text = response.read().decode("utf-8")
    if not text:
        return None

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text
