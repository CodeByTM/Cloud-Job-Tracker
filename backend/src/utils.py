import html
import re
from datetime import datetime
from urllib.parse import urlparse


ALLOWED_STATUSES = {"Applied", "Interviewing", "Rejected", "Offer", "Accepted"}

MAX_COMPANY_LEN = 100
MAX_TITLE_LEN = 100
MAX_LOCATION_LEN = 100
MAX_URL_LEN = 500
MAX_NOTES_LEN = 2000


def clean_text(value: str, max_len: int) -> str:
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ValueError("Invalid text field")

    value = value.strip()
    value = re.sub(r"\s+", " ", value)
    value = html.escape(value, quote=True)

    if len(value) == 0:
        return ""

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

    value = value.strip()
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
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("jobUrl must be a valid http or https URL")

    return value


def get_user_id(event: dict) -> str:
    try:
        return event["requestContext"]["authorizer"]["claims"]["sub"]
    except KeyError as exc:
        raise ValueError("Unauthorized request context") from exc


def sanitize_job_payload(body: dict, partial: bool = False) -> dict:
    if not isinstance(body, dict):
        raise ValueError("Request body must be a JSON object")

    cleaned = {}

    if partial:
        allowed_keys = {"company", "title", "status", "dateApplied", "location", "jobUrl", "notes"}
        unknown_keys = set(body.keys()) - allowed_keys
        if unknown_keys:
            raise ValueError(f"Unknown fields provided: {', '.join(sorted(unknown_keys))}")

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