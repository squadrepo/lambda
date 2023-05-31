import json
import boto3
from layer import jsonDumpsSetDefault


def getTutor(uid):
    tTable = boto3.resource("dynamodb").Table("TutoringProfiles")
    uTable = boto3.resource("dynamodb").Table("Users")
    
    
    try:
        response = tTable.get_item(Key={'uid':uid})
        profile = response['Item']
        
    except Exception as err:
        print(err)
        return False
        
    try:
        response = uTable.get_item(
            Key={'uid':uid},
            ProjectionExpression="fullName, pfpUrl"
        )
        profile.update(response['Item'])
        return profile
        
    except Exception as err:
        print(err)
        return False
        
        
def lambda_handler(event, context):
    # TODO implement
    tutor = getTutor(event['queryStringParameters']['uid'])
    
    if tutor == False:
        return {
            'statusCode': 500,
            'body': 'issues with keys provided.'
        }
    else:
        return {
            'statusCode': 200,
            'body': json.dumps(tutor, default=jsonDumpsSetDefault)
    }