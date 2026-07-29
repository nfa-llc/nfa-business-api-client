import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request


BASE_URL = "https://business.gexbot.com"
DEFAULT_EXPIRES_IN = 365 * 24 * 60 * 60
COMMERCIAL_LEVELS = {"classic", "state", "orderflow"}
BILLING_MONTH_PATTERN = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
REDACTED_HEADER_VALUE = "<redacted>"


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
    def __init__(self, api_key):
        if not api_key:
            raise ValueError("NFA_API_KEY is required")

        self.base_url = BASE_URL
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
        return self.request(f"/user/children/{_path_segment(child_id)}")

    def create_child(
        self,
        level,
        product="gexbot",
        label=None,
        expires_in=DEFAULT_EXPIRES_IN,
    ):
        _validate_level(level)
        return self.request(
            "/user/children",
            method="POST",
            body={
                "product": product,
                "integration": "custom",
                "level": level,
                "label": label or _default_label(),
                "expires_in": expires_in,
            },
        )

    def change_child_tier(self, child_id, level):
        _validate_level(level)
        return self.request(
            f"/user/children/{_path_segment(child_id)}/subscription",
            method="PATCH",
            body={"level": level},
        )

    def delete_child(self, child_id):
        return self.request(f"/user/children/{_path_segment(child_id)}", method="DELETE")

    def get_commercial_billing(self, month=None):
        path = "/user/commercial-billing"
        if month is not None:
            if not BILLING_MONTH_PATTERN.fullmatch(month):
                raise ValueError("month must use YYYY-MM")
            path = f"{path}?{urllib.parse.urlencode({'month': month})}"
        return self.request(path)

    def create_child_key(
        self,
        child_id,
        product="gexbot",
        label=None,
        expires_in=DEFAULT_EXPIRES_IN,
    ):
        return self.request(
            f"/user/children/{_path_segment(child_id)}/key",
            method="POST",
            body={
                "product": product,
                "integration": "custom",
                "label": label or _default_label(),
                "expires_in": expires_in,
            },
        )

    def rotate_child_key(self, child_id, key_id, expires_in=DEFAULT_EXPIRES_IN):
        return self.request(
            f"/user/children/{_path_segment(child_id)}/key",
            method="PATCH",
            body={
                "id": key_id,
                "expires_in": expires_in,
            },
        )

    def revoke_child_key(self, child_id, key_id):
        return self.request(
            f"/user/children/{_path_segment(child_id)}/key",
            method="DELETE",
            body={"id": key_id},
        )

    def rotate_all_child_keys(self, expires_in=DEFAULT_EXPIRES_IN):
        return self.request(
            "/user/children/keys",
            method="PATCH",
            body={"expires_in": expires_in},
        )


def _redact_headers(headers):
    return {
        name: REDACTED_HEADER_VALUE if name.lower() == "authorization" else value
        for name, value in headers.items()
    }


def _validate_level(level):
    if level not in COMMERCIAL_LEVELS:
        allowed = ", ".join(sorted(COMMERCIAL_LEVELS))
        raise ValueError(f"level must be one of: {allowed}")


def _path_segment(value):
    return urllib.parse.quote(str(value), safe="")


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
