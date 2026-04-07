import os

import boto3
from utils import (
    RateLimitExceeded,
    build_response,
    enforce_rate_limit,
    get_user_id,
    validate_job_id,
)

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


def lambda_handler(event, context):
    try:
        enforce_rate_limit(event, endpoint_key="jobs:delete", is_write=True)

        user_id = get_user_id(event)
        job_id = validate_job_id(event["pathParameters"]["jobId"])

        response = table.delete_item(
            Key={
                "userId": user_id,
                "jobId": job_id,
            },
            ConditionExpression="attribute_exists(userId) AND attribute_exists(jobId)",
            ReturnValues="ALL_OLD",
        )

        deleted_item = response.get("Attributes")
        if not deleted_item:
            return build_response(404, {"message": "Job not found"})

        return build_response(200, {
            "message": "Job deleted successfully",
            "job": deleted_item,
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