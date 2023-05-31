import json, boto3, base64

## CREATE TUTORING PROFILE HANDLER: {apiurl}/tutoring ##
# Created 2023-04-15 | Ghadah Ghuzayz
# LastRev 2023-04-22 | Vegan Lroy
# LastRev 2023-04-23 | Ghadah Ghuzayz
#
# Lambda fn for handling creation of tutoring profiles
#
########################################################

def lambda_handler(event, context):
    if 'isBase64Encoded' in event and event['isBase64Encoded']:
        data = json.loads(base64.b64decode(event['body']))
    else:
        data = json.loads(event['body'])
    
    try:
        uid = data['uid']
        bio = data['bio']
        availability = data['availability']
        
        for day in availability:
            for i in range(len(availability[day])):
                timeslot = set(availability[day][i])
                if len(timeslot) != 2:
                    return {'statusCode': 400}
                availability[day][i] = timeslot
        
        hrRate = float(data['hrRate'])
        subjects = set(data['subjects'])
        #classesTaken = set(data['classesTaken'])
        if len(data['classesTaken']) == 0:
            classesTaken = {''}
        else:
            classesTaken = set(data['classesTaken'])
    except Exception as err:
        print(err)
        return {'statusCode': 400}
    
        
    ### CHECK IF UID EXISTS ON USERS TABLE & GET UNIVERSITY, IF SO ###
    usersTable = boto3.resource("dynamodb").Table("Users")
    response = usersTable.get_item(Key={'uid': uid})
    
    if 'Item' in response:
        univ = response['Item']['univ']
    else:
        return {'statusCode' : 404}
    
    ### CHECK IF UID EXISTS ON TUTORING PROFILES TABLE ###
    tutPfTable = boto3.resource("dynamodb").Table("TutoringProfiles")
    response = tutPfTable.get_item(Key={'uid': uid})
    
    if 'Item' in response:
        return {'statusCode' : 400}
        
    subjtTable = boto3.resource("dynamodb").Table("Subjects")
    
    newProfile = {
        'uid': uid,
        'bio': bio,
        'availability': availability,
        'hrRate': int(hrRate),
        'subjects': subjects,
        'classesTaken': classesTaken,
        'rating': {
            "1": {""},
            "2": {""},
            "3": {""},
            "4": {""},
            "5": {""}
        },
        'disciples' : {''}
    }
    
    subjects = data['subjects'] 
    
    
    try:
        for sub in subjects:
            response = subjtTable.get_item(Key={'subject': sub, 'universityName': univ})
            TTID = response['Item']['tutorUids']
            
            TTID.add(uid)
            
            subjtTable.update_item(
                Key={'subject': sub, 'universityName': univ},
                UpdateExpression="set tutorUids=:u",
                ExpressionAttributeValues={
                ':u': TTID
                },
                ReturnValues="NONE"
            )
            #print(newProfile)
        tutPfTable.put_item(Item=newProfile)
        return {'statusCode': 204}
    
    except Exception as err:
        print(err)
        return {'statusCode': 500}