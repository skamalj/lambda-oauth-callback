import boto3

dynamodb = boto3.client('dynamodb', region_name='us-east-1')  # Change region if needed

table_name = "salesforce_tokens"

def create_salesforce_token_table():
    try:
        response = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'wa_id',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'wa_id',
                    'AttributeType': 'S'  # String
                }
            ],
            BillingMode='PAY_PER_REQUEST',  # On-demand pricing (cheaper for low traffic)
        )
        print(f"Creating table '{table_name}'... Status: {response['TableDescription']['TableStatus']}")
    except dynamodb.exceptions.ResourceInUseException:
        print(f"Table '{table_name}' already exists.")

if __name__ == "__main__":
    create_salesforce_token_table()
