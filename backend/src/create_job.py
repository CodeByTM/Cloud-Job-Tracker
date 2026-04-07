import os
import uuid
from datetime import datetime, timezone

import boto3
from utils import (
    RateLimitExceeded,
    build_response,
    enforce_rate_limit,
    get_user_id,
    parse_json_body,
    sanitize_job_payload,
)

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


def lambda_handler(event, context):
    try:
        enforce_rate_limit(event, endpoint_key="jobs:create", is_write=True)

        body = parse_json_body(event)
        cleaned = sanitize_job_payload(body, partial=False)
        user_id = get_user_id(event)

        now = datetime.now(timezone.utc).isoformat()
        job_id = str(uuid.uuid4())

        item = {
            "userId": user_id,
            "jobId": job_id,
            "company": cleaned["company"],
            "title": cleaned["title"],
            "status": cleaned["status"],
            "dateApplied": cleaned["dateApplied"],
            "location": cleaned["location"],
            "jobUrl": cleaned["jobUrl"],
            "notes": cleaned["notes"],
            "createdAt": now,
            "updatedAt": now,
        }

        table.put_item(Item=item)

        return build_response(201, {
            "message": "Job created successfully",
            "job": item,
        })

    except RateLimitExceeded as e:
        return build_response(
            429,
            {"message": e.message},
            {"Retry-After": str(e.retry_after)},
        )
    except ValueError as e:
        return build_response(400, {"message": str(e)})
    except Exception as e:
        return build_response(500, {
            "message": "Internal server error",
            "error": str(e),
        })