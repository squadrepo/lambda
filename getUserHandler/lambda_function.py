import json, boto3
from layer import jsonDumpsSetDefault

### GETUSER HANDLER: {apiurl}/account/user?uid={UUIDv4} ###
# Created 2023-02-25 | Vegan Lroy
# LastRev 2023-02-25 | Vegan Lroy
#
# Lambda fn for handling getting user document from Users
# table based on a user's UUID v4
#
###########################################################

# ENDPOINT CODE
def lambda_handler(event, context):
    data = event['queryStringParameters']
    uid  = data['uid']
    
    tableName = "Users"
    db = boto3.resource("dynamodb").Table(tableName)
    
    response = db.get_item(Key={'uid': uid})
    
    if 'Item' in response:
        userDoc  = response['Item']
        
        if "tutorRating" in userDoc:
            userDoc['tutorRating'] = float(userDoc['tutorRating'])
        
        try:
            userDocJson = json.dumps(userDoc, default=jsonDumpsSetDefault)
            
            return {
                'statusCode': 200,
                'body': userDocJson
            }
        except:
            return {'statusCode': 500}
    else:
        return {
            'statusCode': 404,
            'body': json.dumps({
                'Client-Error Description': 'User with uid=' + uid + ' NOT FOUND.'
            })
        }