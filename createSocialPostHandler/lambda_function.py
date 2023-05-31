import json, boto3, datetime, uuid

def lambda_handler(event, context):
    #TODO implement
    print(event)
    data = json.loads(event['body'])
    
    tableName = "SocialEvents"
    db = boto3.resource("dynamodb").Table(tableName)
    
    tableName2 = "ChatRooms"
    db2 = boto3.resource("dynamodb").Table(tableName2)
    
    CreateTimestmp = int(datetime.datetime.now().timestamp()*1000)
    eid = str(uuid.uuid4())
    cid = str(uuid.uuid4())
    
    #maybe empty
    
    if 'bannerUrl' not in data:
        banner = ''
    else:
        banner = data['bannerUrl']
        
    if len(data['tags']) == 0:
        tag = {""}
    else:
        tag = data['tags']
        
    
    newPost = {
        'univAssoc': data['univAssoc'],
        'createTimestamp':CreateTimestmp,
        'bannerUrl': banner, 
        'chatroomCid': cid,
        'city': data['city'],
        'comments': [],
        'desc': '', # handler?
        'eid': eid,
        'eventName': data['eventName'],
        'eventTimestamp': data['eventTimestamp'],
        'posterUid': data['posterUid'],
        'state': data['state'],
        'streetAddress': data['streetAddress'],
        'tags': tag, 
        'uidsInterested': {""}, 
        'uidsRsvp': {""}, 
        'univExcl': data['univExcl'],
        'zip': data['zip'],
    }
    
    newChat = {
        "cid": cid,
        "chunkCreateTimestamp": CreateTimestmp//1000,
        "roomName": data['eventName'],
        "ownerUid": data['posterUid'],
        "adminUids": {""},
        "modUids": {""},
        "memberUids": {""},
        "messageList": [],
    }
    
    try:
        db.put_item(Item=newPost)
        db2.put_item(Item=newChat)
        return {'statusCode': 204}
    except:
        return {
            'statusCode': 500,
            'body': json.dumps({'failed to create a post'})
        }