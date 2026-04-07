import json
import os
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
        user_id = get_user_id(event)
        job_id = event["pathParameters"]["jobId"]
        body = json.loads(event.get("body", "{}"))
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
                "jobId": job_id
            },
            UpdateExpression="SET " + ", ".join(update_parts),
            ExpressionAttributeNames=expr_attr_names,
            ExpressionAttributeValues=expr_attr_values,
            ConditionExpression="attribute_exists(userId) AND attribute_exists(jobId)",
            ReturnValues="ALL_NEW"
        )

        return build_response(200, {
            "message": "Job updated successfully",
            "job": response["Attributes"]
        })

    except ValueError as e:
        return build_response(400, {"message": str(e)})
    except json.JSONDecodeError:
        return build_response(400, {"message": "Invalid JSON body"})
    except KeyError:
        return build_response(400, {"message": "Missing jobId path parameter"})
    except dynamodb.meta.client.exceptions.ConditionalCheckFailedException:
        return build_response(404, {"message": "Job not found"})
    except Exception as e:
        return build_response(500, {
            "message": "Internal server error",
            "error": str(e)
        })