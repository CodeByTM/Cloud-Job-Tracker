import os

import boto3
from boto3.dynamodb.conditions import Key
from utils import RateLimitExceeded, build_response, enforce_rate_limit, get_user_id

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


def lambda_handler(event, context):
    try:
        enforce_rate_limit(event, endpoint_key="dashboard:get", is_write=False)

        user_id = get_user_id(event)

        response = table.query(
            KeyConditionExpression=Key("userId").eq(user_id)
        )

        jobs = response.get("Items", [])

        stats = {
            "total": len(jobs),
            "applied": 0,
            "interviewing": 0,
            "rejected": 0,
            "offer": 0,
            "accepted": 0,
        }

        for job in jobs:
            status = job.get("status", "").strip().lower()

            if status == "applied":
                stats["applied"] += 1
            elif status == "interviewing":
                stats["interviewing"] += 1
            elif status == "rejected":
                stats["rejected"] += 1
            elif status == "offer":
                stats["offer"] += 1
            elif status == "accepted":
                stats["accepted"] += 1

        return build_response(200, {"dashboard": stats})

    except RateLimitExceeded as e:
        return build_response(
            429,
            {"message": e.message},
            {"Retry-After": str(e.retry_after)},
        )
    except ValueError as e:
        return build_response(401, {"message": str(e)})
    except Exception as e:
        return build_response(500, {
            "message": "Internal server error",
            "error": str(e),
        })