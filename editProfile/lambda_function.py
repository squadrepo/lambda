import json
import boto3

#Table deets according to the ER model

def update_profile(info):
    tableName = "Users"
    db = boto3.resource("dynamodb").Table(tableName)
    cognito = boto3.client('cognito-idp')
    poolID = "us-east-1_qKu4owaQ6"
    
    try:
        response = db.update_item(
            Key={'uid':info['uid']},
            UpdateExpression="set aboutMe=:bio, tags=:t, pfpUrl=:pic",
            ExpressionAttributeValues={
                ':bio': info['aboutMe'],
                ':t': set(info['tags']),
                ':pic':info['pfpUrl']
            },
            ReturnValues="NONE"
            )
        ##print(response['Attributes']['username'], info['username'])
        ##if info['username'] is not response['Attributes']['username']:
        ##    cognito.admin_update_user_attributes(
        ##        UserPoolId=poolID,
        ##        Username=response['Attributes']['username'],
        ##        UserAttributes=[
        ##            {
        ##                'Name': 'username',
        ##                'Value': info['username'],
        ##            },
        ##            ],
        ##    )
    except Exception as err:
        print(err)
        return False
    else:
        return True 
    
def lambda_handler(event, context):
    data = json.loads(event['body'])
    
    if update_profile(data):
        status = 204
    else:
        status = 500
        print("could not update table Users")
        
    return {'statusCode': status}