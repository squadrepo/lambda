import json, boto3, datetime, uuid

## CREATECHATROOM HANDLER: {apiurl}/messages/createChatroom ##
# Created 2023-02-27 | Vegan Lroy
# LastRev 2023-02-27 | Vegan Lroy
#
# Lambda fn for handling creation of chatroom
#
##############################################################

# TRIGGER CODE
def lambda_handler(event, context):
    data = json.loads(event['body'])
    
    userUids = set([data['requesterUid']] + data['memberUids'])
    numberOfMembers = len(userUids)
    
    users     = boto3.resource("dynamodb").Table("Users")
    chatrooms = boto3.resource("dynamodb").Table("ChatRooms")

    # GENERATE CHATROOM INFO
    chnkCreateTimestmp = int(datetime.datetime.now().timestamp())
    cid = str(uuid.uuid4())
    
    newChatroom = {
        "cid": cid,
        "chunkCreateTimestamp": chnkCreateTimestmp,
        "roomName": data['roomName'],
        "ownerUid": "",
        "adminUids": {""},
        "modUids": {""},
        "memberUids": {""},
        "messageList": [],
        }
    
    if   numberOfMembers == 1:
        return {
            'statusCode': 400,
            'body': json.dumps({'Client-Error Description': 'Invalid number of members; only 1 unique uid in request'})
        }
    elif numberOfMembers == 2:
        newChatroom['memberUids'] = userUids
    else:
        newChatroom['ownerUid']   = data['requesterUid']
        newChatroom['memberUids'] = set(data['memberUids'])
    
    if 'openingMessage' in data:
        if len(data['openingMessage']['attachments']) == 0:
            data['openingMessage']['attachments'] = {""}
        else:
            data['openingMessage']['attachments'] = set(data['openingMessage']['attachments'])
        
        if len(data['openingMessage']['uidsReadBy']) == 0:
            data['openingMessage']['uidsReadBy'] = {""}
        else:
            data['openingMessage']['uidsReadBy'] = set(data['openingMessage']['uidsReadBy'])
        
        data['openingMessage']['timestamp'] = chnkCreateTimestmp
        
        newChatroom['messageList'] = [data['openingMessage']]
    
    chatrooms.put_item(Item=newChatroom)
    
    allUsersUpdateSucceeded = True
    # UPDATE chatroomIds FOR USERS IN CHATROOM
    for uid in userUids:
        userDoc = users.get_item(Key={'uid': uid})
        chatroomIds = userDoc['Item']['chatroomCids']
        if len(chatroomIds) == 1 and list(chatroomIds)[0] == "":
            chatroomIds = {cid}
        else:
            chatroomIds.add(cid)
        
        updExp = "SET chatroomCids=:c"
        expAttrVals = {':c': chatroomIds}
        
        try:
            res = users.update_item(
                    Key={'uid': uid},
                    UpdateExpression=updExp,
                    ExpressionAttributeValues=expAttrVals
                )
        except:
            allUsersUpdateSucceeded = False
    
    if allUsersUpdateSucceeded:
        return {'statusCode': 204}
    else:
        return {
            'statusCode': 500,
            'body': json.dumps({'Server-Error Description': 'One or more updates to Users table failed'})
        }