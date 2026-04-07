import json
import os
import uuid
from datetime import datetime, timezone

import boto3
from utils import get_user_id, sanitize_job_payload

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


def build_response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        },
        "body": json.dumps(body)
    }


def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))
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
            "updatedAt": now
        }

        table.put_item(Item=item)

        return build_response(201, {
            "message": "Job created successfully",
            "job": item
        })

    except ValueError as e:
        return build_response(400, {"message": str(e)})
    except json.JSONDecodeError:
        return build_response(400, {"message": "Invalid JSON body"})
    except Exception as e:
        return build_response(500, {
            "message": "Internal server error",
            "error": str(e)
        })