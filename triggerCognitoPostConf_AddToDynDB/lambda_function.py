import json, boto3, datetime, uuid

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
        "classHist": "",
        "dispTags": "",
        "dob": "",
        "email": event['request']['userAttributes']['email'],
        "emailLastVerifiedDate": emailVerifiedDate,
        "fullName": event['request']['userAttributes']['name'],
        "pfpUrl": "",
        "tags": "",
        "tutorRating": 0,
        "univ": "",
        "univExclExp": True,
        "username": event['userName']
        }
    
    db.put_item(Item=newUser)
    
    return event