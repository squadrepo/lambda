import json, dynamodbgeo, boto3
from boto3.dynamodb.types import TypeSerializer, TypeDeserializer
from layer import jsonDumpsSetDefault

## RATE FOODPOST HANDLER: {apiurl}/foodEvent/rate ##
# Created 2023-04-15 | Vegan Lroy
# LastRev 2023-04-15 | Vegan Lroy
#
# Lambda fn for handling rating of food events
#
####################################################

def marshall(python_obj: dict) -> dict: # source: https://stackoverflow.com/a/72725034
    """Convert a standard dict into a DynamoDB ."""
    serializer = TypeSerializer()
    return {k: serializer.serialize(v) for k, v in python_obj.items()}
    
def unmarshall(dynamo_obj: dict) -> dict: # source: https://stackoverflow.com/a/72725034
    """Convert a DynamoDB dict into a standard dict."""
    deserializer = TypeDeserializer()
    return {k: deserializer.deserialize(v) for k, v in dynamo_obj.items()}

def lambda_handler(event, context):
    if 'isBase64Encoded' in event and event['isBase64Encoded']:
        data = json.loads(base64.b64decode(event['body']))
    else:
        data = json.loads(event['body'])
    
    try:
        hashKey = int(data['hashKey'])
        rangeKey = data['rangeKey']
        uid = data['uid']
        ratingToAdd = data['rating'].lower()
        
        if ratingToAdd not in {"up", "down"}:
            return {
                'statusCode': 400,
                'body': json.dumps({'Client-Error Description': 'Bad rating value (needs to be "up" or "down")'})
            }
    except:
        return {
                'statusCode': 400,
                'body': json.dumps({'Client-Error Description': 'Bad hashKey, rangeKey, and/or rating value'})
            }
    
    ### GET OLD RATING AND COORDS ###
    db = boto3.resource("dynamodb").Table("FoodEvents")
    response = db.get_item(Key={'hashKey': hashKey, 'rangeKey': rangeKey})
    
    if 'Item' in response:
        fEventDoc = response['Item']
        
        coords = fEventDoc['geoJson'].split(',')
        coords = [float(coord.strip()) for coord in coords]
        rating = fEventDoc['rating']
    else:
        return {
            'statusCode': 404,
            'body': json.dumps({
                'Client-Error Description': 'Food event with hashKey=' + hashKey + ' and rangeKey=' + rangeKey + ' NOT FOUND.'
            })
        }
    
    if uid in rating[ratingToAdd]:
        rating[ratingToAdd].remove(uid)
        
        if len(rating[ratingToAdd]) == 0:
            rating[ratingToAdd].add('')
    elif ratingToAdd == 'up' and uid in rating['down']:
        if len(rating[ratingToAdd]) == 1 and '' in rating[ratingToAdd]:
            rating[ratingToAdd].remove('')
            
        rating[ratingToAdd].add(uid)
        rating['down'].remove(uid)
        
        if len(rating['down']) == 0:
            rating['down'].add('')
    elif ratingToAdd == 'down' and uid in rating['up']:
        if len(rating[ratingToAdd]) == 1 and '' in rating[ratingToAdd]:
            rating[ratingToAdd].remove('')
            
        rating[ratingToAdd].add(uid)
        rating['up'].remove(uid)
        
        if len(rating['up']) == 0:
            rating['up'].add('')
    else:
        if len(rating[ratingToAdd]) == 1 and '' in rating[ratingToAdd]:
            rating[ratingToAdd].remove('')
            
        rating[ratingToAdd].add(uid)
    
    dynamodb = boto3.client('dynamodb')
    config = dynamodbgeo.GeoDataManagerConfiguration(dynamodb, 'FoodEvents')
    
    # Pick a hashKeyLength appropriate to your usage
    config.hashKeyLength = 5
    
    geoDataManager = dynamodbgeo.GeoDataManager(config)
    
    UpdateItemDict = {
        "UpdateExpression": "set rating = :r",
        "ExpressionAttributeValues": {
            ":r": {"M": marshall(rating)}
        },
        "ReturnValues": "ALL_NEW"
    }
    
    response = geoDataManager.update_Point(dynamodbgeo.UpdateItemInput(dynamodbgeo.GeoPoint(coords[0],coords[1]), rangeKey, UpdateItemDict))
    
    newRating = unmarshall(response['Attributes']['rating']['M'])
    
    return {
        'statusCode': 200,
        'body': json.dumps({"newRating": newRating}, default=jsonDumpsSetDefault)
    }