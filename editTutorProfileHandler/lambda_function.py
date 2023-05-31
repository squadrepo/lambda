import json
import boto3

def updateTutor(info):
    db = boto3.resource("dynamodb").Table("TutoringProfiles")
    dbUser = boto3.resource("dynamodb").Table("Users")
    dbSub = boto3.resource("dynamodb").Table("Subjects")
    
    try:
        response = db.update_item(
            Key={'uid':info['uid']},
            UpdateExpression="set availability=:s, bio=:b, classesTaken=:c, hrRate=:h, subjects=:sub",
            ExpressionAttributeValues={
                ":s" : info["availability"],
                ":b": info["bio"],
                ":c": info["classesTaken"],
                ":h": info["hrRate"],
                ":sub": info["subjects"] 
            },
            ReturnValues="ALL_OLD"
        )
        response2 = dbUser.get_item(Key={'uid': info['uid']})
        
        oldSubjects = response["Attributes"]["subjects"]
        univ = response2["Item"]["univ"]
        
        for subject in list(oldSubjects):
            response3 = dbSub.get_item(Key={'subject':subject, 'universityName':univ})
            tutuid = response3["Item"]["tutorUids"]
            tutlist = list(tutuid)
            tutlist.remove(info['uid'])
            dbSub.update_item(
                Key={'subject':subject, 'universityName':univ},
                UpdateExpression="set tutorUids=:tutSet",
                ExpressionAttributeValues={":tutSet": set(tutlist)}
            )
        #add new subjects
        for sub in list(info["subjects"]):
            response4 = dbSub.get_item(Key={'subject': sub, 'universityName': univ})
            TTID = response4['Item']['tutorUids']
            TTID.add(info['uid'])
            dbSub.update_item(
                Key={'subject': sub, 'universityName': univ},
                UpdateExpression="set tutorUids=:u",
                ExpressionAttributeValues={
                ':u': TTID
                },
                ReturnValues="NONE"
            )  
            
        return True
    except Exception as err:
        print(err)
        return False
        
def lambda_handler(event, context):
    # TODO implement
    data = json.loads(event['body'])
    Tutor = updateTutor(data)
    
    if Tutor == False:
        return {
        'statusCode': 500,
        'body': 'issues with keys provided.'
        }
    else:
        return {'statusCode': 204}