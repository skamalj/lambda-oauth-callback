import os
import boto3
import requests

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ["DYNAMODB_PROFILE_TABLE_NAME"])

def lambda_handler(event, context):
    # Parse query parameters from Salesforce redirect
    qs = event.get("queryStringParameters", {})
    code = qs.get("code")
    state = qs.get("state")  # state is: wa:whatsapp:+1234567890

    if not code or not state or not state.startswith("wa:"):
        return {
            "statusCode": 400,
            "body": "Invalid request"
        }

    wa_id = state.replace("wa:", "")

    # Exchange authorization code for access + refresh token
    token_resp = requests.post("https://login.salesforce.com/services/oauth2/token", data={
        "grant_type": "authorization_code",
        "code": code,
        "client_id": os.environ["SF_CLIENT_ID"],
        "client_secret": os.environ["SF_CLIENT_SECRET"],
        "redirect_uri": os.environ["SF_REDIRECT_URI"],
    })

    if token_resp.status_code != 200:
        return {
            "statusCode": 400,
            "body": "OAuth failed. Could not retrieve token."
        }

    token_data = token_resp.json()

    # Save tokens and instance info to DynamoDB
    table.put_item(Item={
        "wa_id": wa_id,
        "access_token": token_data["access_token"],
        "refresh_token": token_data.get("refresh_token"),
        "instance_url": token_data["instance_url"],
        "issued_at": int(token_data.get("issued_at", 0))
    })

    # OPTIONAL: notify the user via WhatsApp (requires integration with your send logic)
    # Example (pseudo-code):
    # send_whatsapp_message(wa_id, "✅ Your Salesforce account is now connected!")

    return {
        "statusCode": 200,
        "body": "✅ Salesforce connected! You can now return to WhatsApp and start using the bot."
    }
