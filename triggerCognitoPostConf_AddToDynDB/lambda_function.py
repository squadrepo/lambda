import json, boto3, datetime
from layer import getUniversityFromEmail

############ triggerCognitoPostConf_AddToDynDB ############
# Created 2023-02-24 | Vegan Lroy
# LastRev 2023-02-24 | Vegan Lroy
#
# Trigger for adding confirmed Cognito user to Users Table
#
###########################################################

# TRIGGER CODE
def lambda_handler(event, context):
    tableName = "Users"
    db = boto3.resource("dynamodb").Table(tableName)

    emailVerifiedDate = int(datetime.datetime.now().timestamp())
    
    newUser = {
        "uid": event['request']['userAttributes']['sub'],
        "aboutMe": "",
        "classHist": {""},
        "dob": -1,
        "email": event['request']['userAttributes']['email'],
        "emailLastVerifiedDate": emailVerifiedDate,
        "fullName": event['request']['userAttributes']['name'],
        "pfpUrl": "",
        "tags": {""},
        "tutorRating": 0,
        "univ": getUniversityFromEmail(event['request']['userAttributes']['email']),
        "univExclExp": True,
        "username": event['userName']
        }
    
    db.put_item(Item=newUser)
    
    return event