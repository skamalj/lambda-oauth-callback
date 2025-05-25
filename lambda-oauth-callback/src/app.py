import os
import boto3
import requests

from logger import get_logger  # Assuming this is the filename of your logger module

logger = get_logger(__name__)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ["DYNAMODB_PROFILE_TABLE_NAME"])
sf_url = os.environ["SF_URL"]

def lambda_handler(event, context):
    logger.info("Received event: %s", event)

    # Parse query parameters from Salesforce redirect
    qs = event.get("queryStringParameters", {})
    code = qs.get("code")
    state = qs.get("state")  # e.g., profile:1234567890

    if not code or not state or not state.startswith("profile:"):
        logger.warning("Invalid request: missing or malformed 'code' or 'state'")
        return {
            "statusCode": 400,
            "body": "Invalid request"
        }

    profile_id = state.replace("profile:", "")
    logger.info("Extracted profile_id: %s", profile_id)

    try:
        # Exchange authorization code for access + refresh token
        logger.info("Requesting Salesforce tokens for profile_id: %s", profile_id)
        token_resp = requests.post(f"{sf_url}/services/oauth2/token", data={
            "grant_type": "authorization_code",
            "code": code,
            "client_id": os.environ["SF_CLIENT_ID"],
            "client_secret": os.environ["SF_CLIENT_SECRET"],
            "redirect_uri": os.environ["SF_REDIRECT_URI"],
        })

        logger.info("Salesforce token response status: %s", token_resp.status_code)

        if token_resp.status_code != 200:
            logger.error("Salesforce OAuth token request failed: %s", token_resp.text)
            return {
                "statusCode": 400,
                "body": "OAuth failed. Could not retrieve token."
            }

        token_data = token_resp.json()
        logger.debug("Salesforce token data: %s", token_data)

        # Save tokens and instance info to DynamoDB
        logger.info("Saving Salesforce token data to DynamoDB for profile_id: %s", profile_id)
        table.put_item(Item={
            "wa_id": profile_id,
            "access_token": token_data["access_token"],
            "refresh_token": token_data.get("refresh_token"),
            "instance_url": token_data["instance_url"],
            "issued_at": int(token_data.get("issued_at", 0))
        })

    except Exception as e:
        logger.exception("Unexpected error during token exchange or saving to DynamoDB")
        return {
            "statusCode": 500,
            "body": "Internal server error"
        }

    return {
        "statusCode": 200,
        "body": "✅ Salesforce connected! You can now return to WhatsApp and start using the bot."
    }
