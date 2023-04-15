import json, boto3, dynamodbgeo, datetime, uuid, base64

## CREATE FOODPOST HANDLER: {apiurl}/foodEvent ##
# Created 2023-04-14 | Vegan Lroy
# LastRev 2023-04-14 | Vegan Lroy
#
# Lambda fn for handling creation of food event
#
#################################################

def lambda_handler(event, context):
    if 'isBase64Encoded' in event and event['isBase64Encoded']:
        data = json.loads(base64.b64decode(event['body']))
    else:
        data = json.loads(event['body'])
    
    dynamodb = boto3.client('dynamodb')
    config = dynamodbgeo.GeoDataManagerConfiguration(dynamodb, 'FoodEvents')
    
    # Pick a hashKeyLength appropriate to your usage
    config.hashKeyLength = 5
    
    geoDataManager = dynamodbgeo.GeoDataManager(config)
    
    createTimestmp = str(int(datetime.datetime.now().timestamp()))
    
    try:
        startEndTimestamps = set([int(i) for i in data['startEndTimestamp']])
        coords = [float(i) for i in data['coords']]
        
        if len(startEndTimestamps) != 2:
            return {
                'statusCode': 400,
                'body': json.dumps({'Client-Error Description': 'Incorrect startEndTimestamp length'})
            }
        
        if len(coords) != 2:
            return {
                'statusCode': 400,
                'body': json.dumps({'Client-Error Description': 'Incorrect coords length'})
            }
        
        startEndTimestamps = [str(i) for i in data['startEndTimestamp']]
        coords = [str(i) for i in data['coords']]
    except:
        return {
            'statusCode': 400,
            'body': json.dumps({'Client-Error Description': 'startEndTimestamp or coords incorrect value types'})
        }
    
    PutItemInput = {
        'Item': {
            'eventName': {'S': data['eventName']},
            'bannerUrl': {'S': data['bannerUrl']},
            'desc': {'S': data['desc']},
            'requirements': {'S': data['requirements']},
            'address': {'S': data['address']},
            'posterUid': {'S': data['posterUid']},
            'createTimestamp': {'N': createTimestmp},
            'startEndTimestamp': {'L': [{'N': i} for i in startEndTimestamps]},
            'comments': {'L': []},
            "rating": {"M": {
                "up": {"SS": [""]},
                "down": {"SS": [""]}
                }
            }
        }
    }
    
    geoDataManager.put_Point(dynamodbgeo.PutPointInput(dynamodbgeo.GeoPoint(float(coords[0]), float(coords[1])), str(uuid.uuid4()), PutItemInput))
    
    return {'statusCode': 204}