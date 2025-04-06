// @! create readme for this included code include=lambda-oauth-callback/src/app.py include=lambda-oauth-callback/template.yaml provider=anthropic

# Salesforce OAuth Callback Lambda Function

This AWS Lambda function handles the OAuth callback flow for connecting WhatsApp users with their Salesforce accounts. It processes the OAuth redirect from Salesforce, exchanges the authorization code for access tokens, and stores the credentials securely in DynamoDB.

## Overview

The solution consists of:
- A Lambda function that processes OAuth callbacks
- API Gateway integration to expose the callback endpoint
- DynamoDB table to store Salesforce access tokens
- AWS Secrets Manager integration for secure credential storage

## Architecture

1. User initiates Salesforce connection from WhatsApp
2. User is redirected to Salesforce login
3. After successful authentication, Salesforce redirects to the Lambda callback URL
4. Lambda exchanges the auth code for tokens and stores them in DynamoDB
5. User is notified of successful connection

## Prerequisites

- AWS Account with appropriate permissions
- Salesforce Developer Account
- Configured Salesforce Connected App with:
  - OAuth callback URL matching the Lambda function URL
  - Client ID and Client Secret

## Configuration

### Environment Variables

- `DYNAMODB_PROFILE_TABLE_NAME`: Name of DynamoDB table for token storage
- `SF_REDIRECT_URI`: Salesforce OAuth callback URL
- `SF_CLIENT_ID`: Salesforce Connected App Client ID
- `SF_CLIENT_SECRET`: Salesforce Connected App Client Secret

### AWS Secrets Manager

The following secrets need to be configured:
- `sf_client_id`: Salesforce Client ID
- `sf_client_secret`: Salesforce Client Secret
- `sf_callback_uri`: OAuth Callback URI

### DynamoDB Table Structure


Table Name: salesforce_tokens
Primary Key: wa_id (String)
Attributes:
  - access_token (String)
  - refresh_token (String)
  - instance_url (String)
  - issued_at (Number)


## Deployment

The application is deployed using AWS SAM (Serverless Application Model). To deploy:

1. Install AWS SAM CLI
2. Configure AWS credentials
3. Run deployment commands:
bash
sam build
sam deploy --guided


## Security

The solution implements several security best practices:
- Credentials stored in AWS Secrets Manager
- OAuth state parameter validation
- Secure token storage in DynamoDB
- Least privilege IAM roles

## Error Handling

The function handles several error scenarios:
- Invalid or missing OAuth code/state parameters
- Failed token exchange with Salesforce
- Missing or invalid configuration

## Customization

The function includes a commented section for WhatsApp notifications that can be implemented based on your messaging infrastructure:

python
# send_whatsapp_message(wa_id, "✅ Your Salesforce account is now connected!")


## API Endpoints

- POST `/callback`: Handles Salesforce OAuth callback
  - Query Parameters:
    - `code`: OAuth authorization code
    - `state`: State parameter (format: `wa:whatsapp:+phonenumber`)

## Output

Successful connection returns:
- Status Code: 200
- Body: Success message

Error cases return:
- Status Code: 400
- Body: Error description