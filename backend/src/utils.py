import json
import os
import re
import time
from datetime import datetime
from urllib.parse import urlparse

import boto3


# AWS resources
dynamodb = boto3.resource("dynamodb")
RATE_LIMIT_TABLE_NAME = os.getenv("RATE_LIMIT_TABLE")
rate_limit_table = dynamodb.Table(RATE_LIMIT_TABLE_NAME) if RATE_LIMIT_TABLE_NAME else None


# Validation allow-lists and field sizes
ALLOWED_STATUSES = {"Applied", "Interviewing", "Rejected", "Offer", "Accepted"}

MAX_COMPANY_LEN = 100
MAX_TITLE_LEN = 100
MAX_LOCATION_LEN = 100
MAX_URL_LEN = 500
MAX_NOTES_LEN = 2000

UUID_V4ISH_RE = re.compile(
    r"^[0-9a-fA-F]{8}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{4}-"
    r"[0-9a-fA-F]{12}$"
)


class RateLimitExceeded(Exception):
    def __init__(self, retry_after: int, message: str = "Too many requests. Please slow down."):
        super().__init__(message)
        self.retry_after = retry_after
        self.message = message


def build_response(status_code, body, extra_headers=None):
    """
    Shared API response builder.
    Keeps CORS behavior intact and supports Retry-After for 429 responses.
    """
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*",
    }

    if extra_headers:
        headers.update(extra_headers)

    return {
        "statusCode": status_code,
        "headers": headers,
        "body": json.dumps(body),
    }


def parse_json_body(event):
    """
    Parse JSON safely and fail closed on invalid bodies.
    """
    raw_body = event.get("body", "{}")
    try:
        body = json.loads(raw_body)
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid JSON body") from exc

    if not isinstance(body, dict):
        raise ValueError("Request body must be a JSON object")

    return body


def get_user_id(event):
    """
    Pull the Cognito subject claim from API Gateway authorizer context.
    """
    try:
        return event["requestContext"]["authorizer"]["claims"]["sub"]
    except KeyError as exc:
        raise ValueError("Unauthorized request context") from exc


def get_source_ip(event):
    """
    Supports the API Gateway event shapes you are using now.
    """
    request_context = event.get("requestContext", {})

    # REST API shape
    identity_ip = request_context.get("identity", {}).get("sourceIp")
    if identity_ip:
        return identity_ip

    # HTTP API fallback
    http_ip = request_context.get("http", {}).get("sourceIp")
    if http_ip:
        return http_ip

    return "unknown-ip"


def validate_job_id(job_id):
    if not isinstance(job_id, str) or not UUID_V4ISH_RE.match(job_id):
        raise ValueError("Invalid jobId")
    return job_id


def _normalize_text(value: str) -> str:
    """
    OWASP-aligned approach:
    - normalize input before storage
    - remove control chars
    - collapse excessive whitespace
    - DO NOT HTML-encode on input
    Encoding should happen on output. React already escapes text output.
    """
    value = value.strip()
    value = re.sub(r"[\x00-\x1f\x7f]", "", value)
    value = re.sub(r"\s+", " ", value)
    return value


def clean_text(value: str, max_len: int) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ValueError("Invalid text field")

    value = _normalize_text(value)

    if len(value) > max_len:
        raise ValueError(f"Field exceeds max length of {max_len}")

    return value


def validate_required_text(value: str, field_name: str, max_len: int) -> str:
    cleaned = clean_text(value, max_len)
    if not cleaned:
        raise ValueError(f"{field_name} is required")
    return cleaned


def validate_status(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("Invalid status")

    value = _normalize_text(value)
    if value not in ALLOWED_STATUSES:
        raise ValueError("Invalid status value")

    return value


def validate_date(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("Invalid date")

    value = value.strip()

    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError("dateApplied must be in YYYY-MM-DD format") from exc

    return value


def validate_url(value: str) -> str:
    if value is None or value == "":
        return ""

    if not isinstance(value, str):
        raise ValueError("Invalid URL")

    value = value.strip()

    if len(value) > MAX_URL_LEN:
        raise ValueError(f"URL exceeds max length of {MAX_URL_LEN}")

    parsed = urlparse(value)

    # Only allow normal web URLs
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("jobUrl must be a valid http or https URL")

    return value


def sanitize_job_payload(body: dict, partial: bool = False) -> dict:
    """
    Strict schema:
    - reject unknown fields
    - validate required fields for creates
    - validate only provided fields for updates
    """
    allowed_keys = {"company", "title", "status", "dateApplied", "location", "jobUrl", "notes"}
    unknown_keys = set(body.keys()) - allowed_keys
    if unknown_keys:
        raise ValueError(f"Unknown fields provided: {', '.join(sorted(unknown_keys))}")

    cleaned = {}

    if "company" in body or not partial:
        if "company" not in body:
            raise ValueError("company is required")
        cleaned["company"] = validate_required_text(body["company"], "company", MAX_COMPANY_LEN)

    if "title" in body or not partial:
        if "title" not in body:
            raise ValueError("title is required")
        cleaned["title"] = validate_required_text(body["title"], "title", MAX_TITLE_LEN)

    if "status" in body or not partial:
        if "status" not in body:
            raise ValueError("status is required")
        cleaned["status"] = validate_status(body["status"])

    if "dateApplied" in body or not partial:
        if "dateApplied" not in body:
            raise ValueError("dateApplied is required")
        cleaned["dateApplied"] = validate_date(body["dateApplied"])

    if "location" in body:
        cleaned["location"] = clean_text(body["location"], MAX_LOCATION_LEN)

    if "jobUrl" in body:
        cleaned["jobUrl"] = validate_url(body["jobUrl"])

    if "notes" in body:
        cleaned["notes"] = clean_text(body["notes"], MAX_NOTES_LEN)

    if not partial:
        cleaned.setdefault("location", "")
        cleaned.setdefault("jobUrl", "")
        cleaned.setdefault("notes", "")

    return cleaned


def _get_int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _increment_rate_counter(scope: str, identifier: str, endpoint_key: str, window_seconds: int, limit: int):
    """
    Sliding-by-window rate limiter backed by DynamoDB.
    This is app-level protection and works per user + per IP.
    TTL cleans up old counters automatically.
    """
    if not rate_limit_table:
        return

    now = int(time.time())
    window_start = now - (now % window_seconds)
    window_end = window_start + window_seconds
    ttl = window_end + window_seconds

    counter_id = f"{scope}#{identifier}#{endpoint_key}#{window_start}"

    response = rate_limit_table.update_item(
        Key={"id": counter_id},
        UpdateExpression="ADD #count :inc SET #expiresAt = :ttl",
        ExpressionAttributeNames={
            "#count": "count",
            "#expiresAt": "expiresAt",
        },
        ExpressionAttributeValues={
            ":inc": 1,
            ":ttl": ttl,
        },
        ReturnValues="UPDATED_NEW",
    )

    count = int(response["Attributes"]["count"])
    if count > limit:
        retry_after = max(1, window_end - now)
        raise RateLimitExceeded(retry_after=retry_after)


def enforce_rate_limit(event, endpoint_key: str, is_write: bool):
    """
    Dual limiter:
    - per authenticated user
    - per source IP

    Sensible defaults:
    - reads: 120/user/min, 300/IP/5min
    - writes: 30/user/min, 60/IP/5min
    """
    user_id = get_user_id(event)
    source_ip = get_source_ip(event)

    if is_write:
        user_limit = _get_int_env("USER_WRITE_RATE_LIMIT_PER_MINUTE", 30)
        ip_limit = _get_int_env("IP_WRITE_RATE_LIMIT_PER_5_MIN", 60)
    else:
        user_limit = _get_int_env("USER_READ_RATE_LIMIT_PER_MINUTE", 120)
        ip_limit = _get_int_env("IP_READ_RATE_LIMIT_PER_5_MIN", 300)

    _increment_rate_counter("user", user_id, endpoint_key, 60, user_limit)
    _increment_rate_counter("ip", source_ip, endpoint_key, 300, ip_limit)