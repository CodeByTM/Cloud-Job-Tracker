import json
import os

import boto3
from utils import get_user_id

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

        response = table.get_item(
            Key={
                "userId": user_id,
                "jobId": job_id
            }
        )

        item = response.get("Item")

        if not item:
            return build_response(404, {"message": "Job not found"})

        return build_response(200, {"job": item})

    except ValueError as e:
        return build_response(401, {"message": str(e)})
    except KeyError:
        return build_response(400, {"message": "Missing jobId path parameter"})
    except Exception as e:
        return build_response(500, {
            "message": "Internal server error",
            "error": str(e)
        })