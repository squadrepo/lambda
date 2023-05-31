import json
import boto3
from layer import jsonDumpsSetDefault

def getFood(hash, range):
    fTable = boto3.resource("dynamodb").Table("FoodEvents")
    uTable = boto3.resource("dynamodb").Table("Users")

    try:
        resp1 = fTable.get_item(
            Key={'hashKey':int(hash), 'rangeKey':range}
        )
        post = resp1['Item']
        print(post)
        uid = post['posterUid']
        
    except Exception as err:
        print(err)
        return False
        
    try:
        for users in post['comments']:
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
        user.update(post)
        return user
        
    except Exception as err:
        print(err)
        return False    
    
    
def lambda_handler(event, context):
    food = getFood(event['queryStringParameters']['hashKey'], event['queryStringParameters']['rangeKey'])
    
    if food == False:
        return {
        'statusCode': 500,
        'body': 'issues with keys provided.'
        }
    else:
        return {
            'statusCode': 200,
            'body': json.dumps(food, default=jsonDumpsSetDefault)
        }