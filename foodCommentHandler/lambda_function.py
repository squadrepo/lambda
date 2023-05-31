import json
import boto3
import datetime

def lambda_handler(event, context):
    # TODO implement
    
    data = json.loads(event['body'])
    
    tableName = "FoodEvents"
    db = boto3.resource("dynamodb").Table(tableName)
    CreateTimestmp = int(datetime.datetime.now().timestamp())
    
    newCmnt = {
        'createTimestamp' : CreateTimestmp,
        'attachmentUrls' : {''},
        'commenterUid' : data['commenterUid'],
        'commentText' : data['commentText']
    }
    try:
        response = db.get_item(
            Key={'hashKey': int(data['hashKey']), 'rangeKey' : data['rangeKey']},
            ProjectionExpression="comments"
            )
        cmnt = response['Item']
        cmnt['comments'].append(newCmnt)
        
        db.update_item(
            Key={'hashKey': int(data['hashKey']), 'rangeKey' : data['rangeKey']},
            UpdateExpression="set comments=:u",
            ExpressionAttributeValues={
                ':u': cmnt['comments']
            },
            ReturnValues="NONE"
        )
        return {'statusCode': 204}
        
    except Exception as err:
        return {'statusCode': 500}
        print(err)