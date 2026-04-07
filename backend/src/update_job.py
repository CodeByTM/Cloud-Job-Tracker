import os
from datetime import datetime, timezone

import boto3
from utils import (
    RateLimitExceeded,
    build_response,
    enforce_rate_limit,
    get_user_id,
    parse_json_body,
    sanitize_job_payload,
    validate_job_id,
)

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


def lambda_handler(event, context):
    try:
        enforce_rate_limit(event, endpoint_key="jobs:update", is_write=True)

        user_id = get_user_id(event)
        job_id = validate_job_id(event["pathParameters"]["jobId"])
        body = parse_json_body(event)
        cleaned = sanitize_job_payload(body, partial=True)

        if not cleaned:
            return build_response(400, {"message": "No valid fields provided for update"})

        update_parts = []
        expr_attr_values = {}
        expr_attr_names = {}

        for field, value in cleaned.items():
            update_parts.append(f"#{field} = :{field}")
            expr_attr_names[f"#{field}"] = field
            expr_attr_values[f":{field}"] = value

        now = datetime.now(timezone.utc).isoformat()
        update_parts.append("#updatedAt = :updatedAt")
        expr_attr_names["#updatedAt"] = "updatedAt"
        expr_attr_values[":updatedAt"] = now

        response = table.update_item(
            Key={
                "userId": user_id,
                "jobId": job_id,
            },
            UpdateExpression="SET " + ", ".join(update_parts),
            ExpressionAttributeNames=expr_attr_names,
            ExpressionAttributeValues=expr_attr_values,
            ConditionExpression="attribute_exists(userId) AND attribute_exists(jobId)",
            ReturnValues="ALL_NEW",
        )

        return build_response(200, {
            "message": "Job updated successfully",
            "job": response["Attributes"],
        })

    except RateLimitExceeded as e:
        return build_response(
            429,
            {"message": e.message},
            {"Retry-After": str(e.retry_after)},
        )
    except ValueError as e:
        return build_response(400, {"message": str(e)})
    except KeyError:
        return build_response(400, {"message": "Missing jobId path parameter"})
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        return build_response(404, {"message": "Job not found"})
    except Exception as e:
        return build_response(500, {
            "message": "Internal server error",
            "error": str(e),
        })