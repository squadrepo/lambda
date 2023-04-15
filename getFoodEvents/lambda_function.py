import json, boto3, dynamodbgeo
from boto3.dynamodb.types import TypeDeserializer
from layer import jsonDumpsSetDefault

## GET FOODPOSTS HANDLER: {apiurl}/foodEvent #####
# Created 2023-04-14 | Vegan Lroy
# LastRev 2023-04-14 | Vegan Lroy
#
# Lambda fn for getting food events in radius of
# a specified coordinate (within x miles)
#
##################################################

def unmarshall(dynamo_obj: dict) -> dict: # source: https://stackoverflow.com/a/72725034
    """Convert a DynamoDB dict into a standard dict."""
    deserializer = TypeDeserializer()
    return {k: deserializer.deserialize(v) for k, v in dynamo_obj.items()}

def lambda_handler(event, context):
    data = event['queryStringParameters']
    
    if 'coords' in data:
        coords = data['coords'].split(',')
        coords = [float(coord.strip()) for coord in coords]
    else:
        return {'statusCode': 400}
    
    if len(coords) != 2:
        return {'statusCode': 400}
    
    if 'radius' in data:
        radius = round(int(data['radius']) * 1609.344)
    else:
        radius = 1609
    
    dynamodb = boto3.client('dynamodb')
    config = dynamodbgeo.GeoDataManagerConfiguration(dynamodb, 'FoodEvents')
    
    # Pick a hashKeyLength appropriate to your usage
    config.hashKeyLength = 5
    
    geoDataManager = dynamodbgeo.GeoDataManager(config)
    
    response = geoDataManager.queryRadius(dynamodbgeo.QueryRadiusRequest(
        dynamodbgeo.GeoPoint(coords[0], coords[1]), radius, sort = True))
    
    fEventsFinal = []
    for fEvent in response:
        unmarshalledEvent = unmarshall(fEvent)
        del unmarshalledEvent['comments']
        del unmarshalledEvent['posterUid']
        fEventsFinal.append(unmarshalledEvent)
    
    return {
        'statusCode': 200,
        'body': json.dumps(fEventsFinal, default=jsonDumpsSetDefault)
    }