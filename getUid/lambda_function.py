import json, boto3
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    data = event['queryStringParameters']
    username = data['username']
    
    tableName = "Users"
    db = boto3.resource("dynamodb").Table(tableName)

    response = db.query(
        IndexName='username-index',
        KeyConditionExpression=Key('username').eq(username)
        )
    
    if len(response['Items']) == 1:
        return {
            'statusCode': 200,
            'body': json.dumps({
                'uid': response['Items'][0]['uid']
            })
        }
    else:
        return {
            'statusCode': 404,
            'body': json.dumps({
                'Client-Error Description': 'User with username=' + username + ' NOT FOUND.'
            })
        }