import json, boto3, datetime
from boto3.dynamodb.conditions import Key
from layer import jsonDumpsSetDefault

##### GETSOCIALEVENTS: {apiurl}/socialEvent/getEvents ######
# Created 2023-03-04 | Vegan Lroy
# LastRev 2023-05-20 | Vegan Lroy
#
# Lambda fn fetch social events from the past week (up to 3)
#
############################################################

NUM_SECS_IN_WK = 604800

# ENDPOINT CODE
def lambda_handler(event, context):
    data = event['queryStringParameters']
    if 'univ' in data and 'city' not in data:
        pKey    = 'univAssoc'
        pKeyVal = data['univ']
    elif 'city' in data:
        pKey    = 'city-createTimestamp-index'
        pKeyVal = data['city']
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'Client-Error Description': 'Neither city nor univ query string provided.'
            })
        }
    
    tableName = "SocialEvents"
    table = boto3.resource("dynamodb").Table(tableName)
    
    if 'fromTime' in data:
        for i in range(1,4):
            try:
                timeFrom = (int(data['fromTime']) - (NUM_SECS_IN_WK * i)) * 1000
            except:
                return {
                    'statusCode': 404,
                    'body': json.dumps({
                        'Client-Error Description': 'Timestamp given included non-numerical characters: ' + data['fromTime']
                    })
                }
            
            if pKey == 'univAssoc':
                response = table.query(
                    KeyConditionExpression=Key(pKey).eq(pKeyVal)&Key('createTimestamp').gt(timeFrom)
                    )
            else:
                response = table.query(
                    IndexName=pKey,
                    KeyConditionExpression=Key('city').eq(pKeyVal)&Key('createTimestamp').gt(timeFrom)
                    )
            
            if 'Items' in response and len(response['Items']) > 0:
                break
    else:
        for i in range(1,4):
            time = (int(datetime.datetime.now().timestamp()) - (NUM_SECS_IN_WK * i)) * 1000
            
            if pKey == 'univAssoc':
                response = table.query(
                    KeyConditionExpression=Key(pKey).eq(pKeyVal)&Key('createTimestamp').gt(time)
                    )
            else:
                response = table.query(
                    IndexName=pKey,
                    KeyConditionExpression=Key('city').eq(pKeyVal)&Key('createTimestamp').gt(time)
                    )
                    
            if 'Items' in response and len(response['Items']) > 0:
                break
    
    try:
        rV = json.dumps(response['Items'], default=jsonDumpsSetDefault)
        
        return {
            'statusCode': 200,
            'body': rV
        }
    except:
        return {'statusCode': 500}