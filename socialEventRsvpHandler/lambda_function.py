import json, boto3, datetime, base64
from boto3.dynamodb.conditions import Key
from layer import jsonDumpsSetDefault

## CREATECHATROOM HANDLER: {apiurl}/socialEvent/rsvp ##
# Created 2023-03-06 | Vegan Lroy
# LastRev 2023-04-07 | Vegan Lroy
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
    
    # Flag for tracking whether we added or removed uid from event-related entities
    uidRemoved = False
    
    users        = boto3.resource("dynamodb").Table("Users")
    chatrooms    = boto3.resource("dynamodb").Table("ChatRooms")
    socialEvents = boto3.resource("dynamodb").Table("SocialEvents")
    
    # UPDATE SOCIAL EVENT TO ADD/REMOVE USER TO RSVP OR INTERESTED LIST
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
    
    if tentative:
        if len(uidsInterested) == 1 and list(uidsInterested)[0] == "":
            uidsInterested = {userId}
        else:
            if userId in uidsInterested:
                uidRemoved = True
                if len(uidsInterested) == 1:
                    uidsInterested = {""}
                else:
                    uidsInterested.remove(userId)
            else:
                uidsInterested.add(userId)
        
        if userId in uidsRsvp:
            if len(uidsRsvp) == 1:
                uidsRsvp = {""}
            else:
                uidsRsvp.remove(userId)
    else:
        if len(uidsRsvp) == 1 and list(uidsRsvp)[0] == "":
            uidsRsvp = {userId}
        else:
            if userId in uidsRsvp:
                uidRemoved = True
                if len(uidsRsvp) == 1:
                    uidsRsvp = {""}
                else:
                    uidsRsvp.remove(userId)
            else:
                uidsRsvp.add(userId)
        
        if userId in uidsInterested:
            if len(uidsInterested) == 1:
                uidsInterested = {""}
            else:
                uidsInterested.remove(userId)
    
    updExp = "SET uidsInterested=:m, uidsRsvp=:y"
    expAttrVals = {
        ':m': uidsInterested,
        ':y': uidsRsvp
    }
    
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
        if uidRemoved:
            if len(members) == 1:
                members = {""}
            else:
                members.remove(userId)
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
    
    # ADD CHATROOM ID TO USER'S CHATROOM ID SET, ADD EID TO RSVP OR INTERESTED SET
    response = users.get_item(Key={'uid':userId})
    
    if 'Item' in response:
        userDoc = response['Item']
        chatroomCids = userDoc['chatroomCids']
        
        if len(chatroomCids) == 1 and list(chatroomCids)[0] == "":
            chatroomCids = {cid}
        else:
            if uidRemoved:
                if len(chatroomCids) == 1:
                    chatroomCids = {""}
                else:
                    chatroomCids.remove(cid)
            else:
                chatroomCids.add(cid)
        
        updExp = "SET chatroomCids=:c, eidsInterested=:m, eidsRsvpd=:y"
        eidsInterested = userDoc['eidsInterested']
        eidsRsvpd = userDoc['eidsRsvpd']
        
        if tentative:
            if len(eidsInterested) == 1 and list(eidsInterested)[0] == "":
                eidsInterested = {eventId}
            else:
                if eventId in eidsInterested:
                    if len(eidsInterested) == 1:
                        eidsInterested = {""}
                    else:
                        eidsInterested.remove(eventId)
                else:
                    eidsInterested.add(eventId)
            
            if eventId in eidsRsvpd:
                if len(eidsRsvpd) == 1:
                    eidsRsvpd = {""}
                else:
                    eidsRsvpd.remove(eventId)
        else:
            if len(eidsRsvpd) == 1 and list(eidsRsvpd)[0] == "":
                eidsRsvpd = {eventId}
            else:
                if eventId in eidsRsvpd:
                    if len(eidsRsvpd) == 1:
                        eidsRsvpd = {""}
                    else:
                        eidsRsvpd.remove(eventId)
                else:
                    eidsRsvpd.add(eventId)
            
            if eventId in eidsInterested:
                if len(eidsInterested) == 1:
                    eidsInterested = {""}
                else:
                    eidsInterested.remove(eventId)
        
        expAttrVals = {':c': chatroomCids, ':m': eidsInterested, ':y': eidsRsvpd}
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
    
    if uidRemoved:
        return {'statusCode': 204}
    else:
        return {'statusCode': 200, 'body': json.dumps({'newCid': cid}, default=jsonDumpsSetDefault)}