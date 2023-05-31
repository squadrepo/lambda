import json
import boto3
from layer import jsonDumpsSetDefault


def getTutors(subject, univ):
    tTable = boto3.resource("dynamodb").Table("TutoringProfiles")
    uTable = boto3.resource("dynamodb").Table("Users")
    sTable = boto3.resource("dynamodb").Table("Subjects")
    profiles = []
    try:
        response = sTable.get_item(Key={'subject': subject, 'universityName': univ})
        users = response['Item']['tutorUids']
        for user in users:
            response = tTable.get_item(Key={'uid':user})
            profile = response['Item']
        
            response = uTable.get_item(
                Key={'uid':user},
                ProjectionExpression="fullName, pfpUrl"
            )
            profile.update(response['Item'])
            profiles.append(profile)
        return profiles
        
    except Exception as err:
        print(err)
        return False
        
        
def lambda_handler(event, context):
    # TODO implement
    tutors = getTutors(event['queryStringParameters']['subject'], event['queryStringParameters']['universityName'])
    
    if tutors == False:
        return {
            'statusCode': 500,
            'body': 'issues with keys provided.'
        }
    else:
        return {
            'statusCode': 200,
            'body': json.dumps(tutors, default=jsonDumpsSetDefault)
    }