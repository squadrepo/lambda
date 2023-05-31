import json, boto3, base64, datetime, uuid
from layer import jsonDumpsSetDefault

## REQUEST TUTOR SESSION: {apiurl}/tutoring/requestSession ##
# Created 2023-04-23 | Vegan Lroy
# LastRev 2023-05-13 | Vegan Lroy
#
# Handles session-reqs for tutors from potential disciples
#
# Potential disciple sends request to this endpoint to seek
#   assistance from a given tutor
#
#############################################################

def lambda_handler(event, context):
    if 'isBase64Encoded' in event and event['isBase64Encoded']:
        data = json.loads(base64.b64decode(event['body']))
    else:
        data = json.loads(event['body'])
    
    try:
        tutorUid    = data['tutorUid']
        discipleUid = data['discipleUid']
        
        timestampRequested = int(data['timestampRequested'])
    except:
        return {
                'statusCode': 400,
                'body': json.dumps({'Client-Error Description': 'Missing tutorUid, discipleUid, timestampRequested value; or bad timestampRequested value.'})
            }
    
    dynamodb  = boto3.resource("dynamodb")
    users     = dynamodb.Table("Users")
    chatrooms = dynamodb.Table("ChatRooms")
    
    ### GET USERNAMES OF TUTOR AND DISCIPLE ###
    try:
        response = dynamodb.batch_get_item(
            RequestItems = {
                'Users': {
                    'Keys': [{'uid': tutorUid},{'uid': discipleUid}]
                }
            })
            
        tutorUserDoc, discpUserDoc = response['Responses']['Users'][0], response['Responses']['Users'][1]
    except:
        return {
                'statusCode': 404,
                'body': json.dumps({'Client-Error Description': 'Bad tutorUid or discipleUid value; id(s) not found.'})
            }
    
    # GENERATE CHATROOM INFO
    chnkCreateTimestmp = int(datetime.datetime.now().timestamp())
    cid = str(uuid.uuid4())
    
    newChatroomDict = {
        "cid": cid,
        "chunkCreateTimestamp": chnkCreateTimestmp,
        "roomName": "Tutor: " + tutorUserDoc['username'] + " - Request from " + discpUserDoc['username'],
        "ownerUid": "",
        "adminUids": {""},
        "modUids": {""},
        "memberUids": {discipleUid,tutorUid},
        "messageList": [{
            "uidSentBy": discipleUid,
            "text": "",
            "attachments": [{
                "cardType": "tutorRequest",
                "tutor": tutorUid,
                "requestor": discipleUid,
                "timestampRequested": timestampRequested
            }],
            "uidsReadBy": [],
            "timestamp": chnkCreateTimestmp
        }]
    }
    
    chatrooms.put_item(Item=newChatroomDict)
    
    allUsersUpdateSucceeded = True
    # UPDATE chatroomIds FOR USERS IN CHATROOM
    tutorCids = tutorUserDoc['chatroomCids']
    discpCids = discpUserDoc['chatroomCids']
    uidsList = [tutorUid,discipleUid]
    cidsList = [tutorCids,discpCids]

    for i in range(len(uidsList)):
        if len(cidsList[i]) == 1 and list(cidsList[i])[0] == "":
            cidsList[i] = {cid}
        else:
            cidsList[i].add(cid)
        
        updExp = "SET chatroomCids=:c"
        expAttrVals = {':c': cidsList[i]}
        
        try:
            res = users.update_item(
                    Key={'uid': uidsList[i]},
                    UpdateExpression=updExp,
                    ExpressionAttributeValues=expAttrVals
                )
        except:
            allUsersUpdateSucceeded = False
    
    if allUsersUpdateSucceeded:
        return {
            'statusCode': 200, 
            'body': json.dumps({
                'chatroomCid': cid, 
                'timestamp': chnkCreateTimestmp
            })
        }
    else:
        return {
            'statusCode': 500,
            'body': json.dumps({'Server-Error Description': 'One or more updates to Users table failed'})
        }