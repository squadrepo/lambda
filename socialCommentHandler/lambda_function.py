import json
import boto3
import datetime

def lambda_handler(event, context):
    # TODO implement
    data = json.loads(event['body'])
    
    tableName = "SocialEvents"
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
            Key={'univAssoc': data['univAssoc'], 'createTimestamp' : int(data['createTimestamp'])},
            ProjectionExpression="comments"
            )
        cmnt = response['Item']
        cmnt['comments'].append(newCmnt)
        
        db.update_item(
            Key={'univAssoc': data['univAssoc'], 'createTimestamp' : int(data['createTimestamp'])},
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