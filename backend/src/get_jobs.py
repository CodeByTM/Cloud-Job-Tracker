import os

import boto3
from boto3.dynamodb.conditions import Key
from utils import RateLimitExceeded, build_response, enforce_rate_limit, get_user_id

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])


def lambda_handler(event, context):
    try:
        enforce_rate_limit(event, endpoint_key="jobs:list", is_write=False)
        user_id = get_user_id(event)

        response = table.query(
            KeyConditionExpression=Key("userId").eq(user_id)
        )

        return build_response(200, {"jobs": response.get("Items", [])})

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