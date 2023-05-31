import json
import boto3 
from boto3.dynamodb.conditions import Key 
from layer import jsonDumpsSetDefault
#input: one cid, one date, output: chunk of same cidbut the date before that 


def getPrevMSG(cid, time):
    tableName = "ChatRooms"
    db = boto3.resource("dynamodb").Table(tableName)
    getOutPut = []
    
    try:
        response = db.query(
            KeyConditionExpression=Key('cid').eq(cid) & Key('chunkCreateTimestamp').eq(int(time)),
            ScanIndexForward=False,
            Limit=1,
            Select='ALL_ATTRIBUTES'
        )
    except:
        return False
    else:
        if not response['Items']:
            return '404'
        else:
            time = response['Items'][0]['chunkCreateTimestamp']
            msgList = response['Items'][0]['messageList']
            #time.append(msgList)
            #getOutPut.append(time)
            getOutPut.append(msgList)
            return getOutPut
        


def lambda_handler(event, context):
    # TODO implement
    print(event['queryStringParameters'])
    msg = getPrevMSG(event['queryStringParameters']['cid'], event['queryStringParameters']['chunkCreateTimestamp'])
    
    if msg == False:
        return {
        'statusCode': 500,
        'body': 'issue with either keys provided. format is cid:string, chunkCreateTimestamp:number'
        }
    else:
        if msg == '404':
            return {
            'statusCode': 404,
            "body" : "No more old messages"
            }
        else:
            try:
                msgdoc = json.dumps(msg, default=jsonDumpsSetDefault)
                return {
                'statusCode': 200,
                'body': msgdoc
                }
            except:
                return {
                'statusCode': 500
                }