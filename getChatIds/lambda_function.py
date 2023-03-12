import json
import boto3
from boto3.dynamodb.conditions import Key
from layer import jsonDumpsSetDefault

# input: list of chatcids, output: a list of the cid + chatroom name + last msg for each cid


def getChat(chatdata):
    tableName = "ChatRooms"
    db = boto3.resource("dynamodb").Table(tableName)
    getOutPut = []
    temp = {}

    for x in chatdata:
        try:
            response = db.query(
                KeyConditionExpression=Key('cid').eq(
                    x) & Key('chunkCreateTimestamp').gte(1),
                ScanIndexForward=False,
                Limit=1,
                Select='ALL_ATTRIBUTES'
            )
        except:
            return 'Error: cid does not exist'

        else:
            chatInfo = response['Items'][0]
            room = chatInfo['roomName']
            msglen = len(chatInfo['messageList'])
            lastMSG = chatInfo['messageList'][msglen-1]
            temp.update({'cid': x})
            temp.update({'roomName': room})
            temp.update({'messageList': lastMSG})
            getOutPut.append(temp)

    return getOutPut


def lambda_handler(event, context):
    # TODO implement
    data = event['queryStringParameters']['chatroomCids']
    # data = event['chatroomCids']
    sendBack = getChat(data)

    try:
        chatdoc = json.dumps(sendBack, default=jsonDumpsSetDefault)
        return {
            'statusCode': 200,
            'body': chatdoc
        }
    except:
        return {
            'statusCode': 500
        }
