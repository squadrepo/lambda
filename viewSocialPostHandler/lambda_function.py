import json
import boto3
from layer import jsonDumpsSetDefault

def viewPost(univ, id):
    tableName = "SocialEvents"
    db = boto3.resource("dynamodb").Table(tableName)
    uTable = boto3.resource("dynamodb").Table("Users")
    
    try:   
        response = db.query(
            KeyConditionExpression= 'univAssoc = :u', 
            FilterExpression= 'eid = :i',
            ExpressionAttributeValues={
                ':u' : univ,
                ':i' : id
            }
        )
        item = response['Items'][0]
        uid = item['posterUid']
        print(item)
        #return item
    except Exception as err:
        print(err)
        return False  
        
    try:
        for users in item['comments']:
            resp2 = uTable.get_item(
                Key={'uid': users['commenterUid']},
                ProjectionExpression="fullName, pfpUrl"
                )
            users.update(resp2["Item"])
            
    except Exception as err:
        print(err)
        return False  
        
    try:
        resp3 = uTable.get_item(
            Key={'uid': uid},
            ProjectionExpression="fullName, pfpUrl"
        )
        user = resp3["Item"]
        user.update(item)
        return user
        
    except Exception as err:
        print(err)
        return False    
    
def lambda_handler(event, context):
    post = viewPost(event['queryStringParameters']['univAssoc'], event['queryStringParameters']['eid'])
    # TODO implement
    
    if post == False:
        return {
        'statusCode': 500,
        'body': 'issues with UID provided.'
        }
    else:
        return {
            'statusCode': 200,
            'body': json.dumps(post, default=jsonDumpsSetDefault)
        }