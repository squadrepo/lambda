import json, boto3, datetime, base64
from boto3.dynamodb.conditions import Key

## TUTOR REQ-RESP HANDLER: {apiurl}/tutoring/respondToRequest ##
# Created 2023-05-13 | Vegan Lroy
# LastRev 2023-05-13 | Vegan Lroy
#
# Lambda fn for handling tutor responding to tutoring request
#
################################################################

CHUNK_SIZE = 20

def createNewChunk(prevChunk, message): # from: postMessageHandler
    newChatRoom = {
        "cid": prevChunk['cid'],
        "chunkCreateTimestamp": message['timestamp'],
        "roomName": prevChunk['roomName'],
        "ownerUid": prevChunk['ownerUid'],
        "adminUids": prevChunk['adminUids'],
        "modUids": prevChunk['modUids'],
        "memberUids": prevChunk['memberUids'],
        "messageList": [message],
    }

    tableName = "ChatRooms"
    db = boto3.resource("dynamodb").Table(tableName)

    try:
        db.put_item(Item=newChatRoom)
        return 204
    except Exception as e:
        print(e)
        return 500

def postMessage(chatRoomId, message): # from: postMessageHandler
    tableName = "ChatRooms"
    db = boto3.resource("dynamodb").Table(tableName)

    try:
        response = db.query(
            KeyConditionExpression=Key('cid').eq(chatRoomId),
            ScanIndexForward=False,
            Limit=1,
            Select='ALL_ATTRIBUTES'
        )
    except Exception as e:
        print(e)
        return 500

    if 'Items' not in response or len(response['Items']) == 0:
        return 404
    currentChunk = response['Items'][0]

    if len(message['uidsReadBy']) == 0:
        message['uidsReadBy'] = {""}
    else:
        message['uidsReadBy'] = set(
            message['uidsReadBy'])
    message['timestamp'] = int(datetime.datetime.now().timestamp())

    if len(currentChunk['messageList']) >= CHUNK_SIZE:
        return createNewChunk(currentChunk, message)

    try:
        db.update_item(
            Key={'cid': currentChunk['cid'],
                 'chunkCreateTimestamp': currentChunk['chunkCreateTimestamp']},
            UpdateExpression="SET messageList = list_append(messageList, :i)",
            ExpressionAttributeValues={':i': [message]}
        )
    except Exception as e:
        print(e)
        return 500

    return 204

def lambda_handler(event, context):
    if 'isBase64Encoded' in event and event['isBase64Encoded']:
        data = json.loads(base64.b64decode(event['body']))
    else:
        data = json.loads(event['body'])
        
    try:
        cid = data['cid']
        
        responderUid = data['responderUid']
        discipleUid  = data['discipleUid']
        
        timestampRequested = int(data['timestampRequested'])
    except:
        return {
                'statusCode': 400,
                'body': json.dumps({'Client-Error Description': 'Missing responderUid, discipleUid, cid, timestampRequested value; or non-numerical timestampRequested value.'})
            }
    
    dynamodb  = boto3.resource("dynamodb")
    tutors    = dynamodb.Table("TutoringProfiles")
    
    response = tutors.get_item(Key={'uid': responderUid})
    
    if 'Item' in response:
        tutorProfileDoc = response['Item']
        
        disciples = tutorProfileDoc['disciples']
        if len(disciples) == 1 and list(disciples)[0] == "":
            disciples = {discipleUid}
        else:
            disciples.add(discipleUid)
    else:
        return {
            'statusCode': 404,
            'body': json.dumps({
                'Client-Error Description': 'Tutoring profile with uid=' + uid + ' NOT FOUND.'
            })
        }
    
    updExp = "SET disciples=:d"
    expAttrVals = {':d': disciples}
    
    try:
        response = tutors.update_item(
                Key = {'uid': responderUid},
                UpdateExpression = updExp,
                ExpressionAttributeValues = expAttrVals,
                ReturnValues = 'ALL_NEW'
            )
    except:
        return {'statusCode': 500}
        
    message = {
            "attachments": [{
                "cardType": "tutorRequestAccepted",
                "tutor": responderUid,
                "requestor": discipleUid,
                "timestampRequested": timestampRequested
            }],
            "text": "",
            "timestamp": int(datetime.datetime.now().timestamp()),
            "uidSentBy": responderUid,
            "uidsReadBy": []
        }
    
    return {'statusCode': postMessage(cid, message)}