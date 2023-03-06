import json
import boto3
import datetime
import base64
from boto3.dynamodb.conditions import Key

CHUNK_SIZE = 20


def createNewChunk(prevChunk, message):
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


def postMessage(chatRoomId, message):
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

    if len(message['attachments']) == 0:
        message['attachments'] = {""}
    else:
        message['attachments'] = set(
            message['attachments'])

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

    if 'cid' not in data or 'message' not in data:
        return {'statusCode': 400}

    responseStatus = postMessage(
        data['cid'], data['message'])
    return {'statusCode': responseStatus}
