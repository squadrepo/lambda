import json, boto3, datetime, base64
from boto3.dynamodb.conditions import Key

## CREATECHATROOM HANDLER: {apiurl}/socialEvent/rsvp ##
# Created 2023-03-06 | Vegan Lroy
# LastRev 2023-03-06 | Vegan Lroy
#
# Lambda fn for handling adding user to social event
#
#######################################################

def lambda_handler(event, context):
    if 'isBase64Encoded' in event and event['isBase64Encoded']:
        data = json.loads(base64.b64decode(event['body']))
    else:
        data = json.loads(event['body'])
    
    eventId = data['eid']
    userId  = data['uid']
    tentative = data['tentative']
    
    users        = boto3.resource("dynamodb").Table("Users")
    chatrooms    = boto3.resource("dynamodb").Table("ChatRooms")
    socialEvents = boto3.resource("dynamodb").Table("SocialEvents")
    
    # UPDATE SOCIAL EVENT TO ADD USER TO RSVP OR INTERESTED LIST
    response = socialEvents.query(
            IndexName='eid-index',
            KeyConditionExpression=Key('eid').eq(eventId)
        )
        
    if len(response['Items']) == 1:
        uidsRsvp = response['Items'][0]['uidsRsvp']
        uidsInterested = response['Items'][0]['uidsInterested']
        pk = response['Items'][0]['univAssoc']
        sk = response['Items'][0]['createTimestamp']
    else:
        return {'statusCode': 500}
    
    updExp = "SET "
    expAttrVals = {}
    if tentative:
        if len(uidsInterested) == 1 and list(uidsInterested)[0] == "":
            uidsInterested = {userId}
        else:
            uidsInterested.add(userId)
            
        updExp += 'uidsInterested=:u'
        expAttrVals[':u'] = uidsInterested
    else:
        if len(uidsRsvp) == 1 and list(uidsRsvp)[0] == "":
            uidsRsvp = {userId}
        else:
            uidsRsvp.add(userId)
            
        updExp += 'uidsRsvp=:u'
        expAttrVals[':u'] = uidsRsvp
    
    try:
        response = socialEvents.update_item(
                Key = {'univAssoc': pk, 'createTimestamp': sk},
                UpdateExpression = updExp,
                ExpressionAttributeValues = expAttrVals,
                ReturnValues = 'ALL_NEW'
            )
        
        cid = response['Attributes']['chatroomCid']
    except:
        return {'statusCode': 500}
    
    # ADD USER TO CHATROOM, ADDS TO LATEST CHUNK
    response = chatrooms.query(
            KeyConditionExpression=Key('cid').eq(cid)&Key('chunkCreateTimestamp').lte(int(datetime.datetime.now().timestamp())),
            ScanIndexForward=False,
            Limit=1
        )
    
    if len(response['Items']) == 1:
        members = response['Items'][0]['memberUids']
        pk = cid
        sk = response['Items'][0]['chunkCreateTimestamp']
    else:
        return {'statusCode': 500}
    
    if len(members) == 1 and list(members)[0] == "":
        members = {userId}
    else:
        members.add(userId)
    updExp = "SET memberUids=:m"
    expAttrVals = {':m': members}
    
    try:
        response = chatrooms.update_item(
                Key = {'cid': pk, 'chunkCreateTimestamp': sk},
                UpdateExpression = updExp,
                ExpressionAttributeValues = expAttrVals,
                ReturnValues = 'NONE'
            )
    except:
        return {'statusCode': 500}
    
    # ADD CHATROOM ID TO USER'S CHATROOM ID SET
    response = users.get_item(Key={'uid':userId})
    
    if 'Item' in response:
        userDoc = response['Item']
        chatroomCids = userDoc['chatroomCids']
        
        if len(chatroomCids) == 1 and list(chatroomCids)[0] == "":
            chatroomCids = {cid}
        else:
            chatroomCids.add(cid)
            
        updExp = "SET chatroomCids=:c"
        expAttrVals = {':c': chatroomCids}
    else:
        return {'statusCode': 500}
    
    try:
        response = users.update_item(
                Key = {'uid': userId},
                UpdateExpression = updExp,
                ExpressionAttributeValues = expAttrVals,
                ReturnValues = 'NONE'
            )
    except:
        return {'statusCode': 500}
    
    return {
        'statusCode': 200,
        'body': json.dumps({'newCid': cid})
    }