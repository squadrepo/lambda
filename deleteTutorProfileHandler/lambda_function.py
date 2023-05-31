import json
import boto3

def deleteTutor(info):
    db = boto3.resource("dynamodb").Table("TutoringProfiles")
    dbUser = boto3.resource("dynamodb").Table("Users")
    dbSub = boto3.resource("dynamodb").Table("Subjects")
    try:
        response = db.delete_item(
            Key={'uid': info['uid']},
            ReturnValues="ALL_OLD"
        )
        
        response2 = dbUser.get_item(Key={'uid': info['uid']})
        
        subjects = response["Attributes"]["subjects"]
        univ = response2["Item"]["univ"]
        
        for subject in list(subjects):
            response3 = dbSub.get_item(Key={'subject':subject, 'universityName':univ})
            tutuid = response3["Item"]["tutorUids"]
            tutlist = list(tutuid)
            tutlist.remove(info['uid'])
            dbSub.update_item(
                Key={'subject':subject, 'universityName':univ},
                UpdateExpression="set tutorUids=:tutSet",
                ExpressionAttributeValues={":tutSet": set(tutlist)}
            )
            
        return True
    except Exception as err:
        print(err)
        return False
        
def lambda_handler(event, context):
    db = boto3.resource("dynamodb").Table("TutoringProfiles")
    data = event['queryStringParameters']
    remove = deleteTutor(data)
        
    if remove == False:
        return {
        'statusCode': 500,
        'body': 'issues with keys provided.'
        }
    else:
        return {'statusCode': 204}
    # TODO implement