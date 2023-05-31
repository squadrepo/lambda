import json, boto3
from layer import jsonDumpsSetDefault

## RATE TUTOR HANDLER: {apiurl}/tutoring/rate ##
# Created 2023-04-22 | Vegan Lroy
# LastRev 2023-04-22 | Vegan Lroy
#
# Lambda fn for handling rating of tutors
#
################################################

def lambda_handler(event, context):
    if 'isBase64Encoded' in event and event['isBase64Encoded']:
        data = json.loads(base64.b64decode(event['body']))
    else:
        data = json.loads(event['body'])
    
    try:
        tutorUid = data['tutorUid']
        discipleUid = data['discipleUid']
        ratingToAdd = int(data['rating'])
        
        if ratingToAdd not in range(1,6):
            return {
                'statusCode': 400,
                'body': json.dumps({'Client-Error Description': 'Bad rating value (needs to be integer value 1-5)'})
            }
        
        ratingToAdd = str(ratingToAdd)
    except:
        return {
                'statusCode': 400,
                'body': json.dumps({'Client-Error Description': 'Bad rating value (needs to be integer value 1-5)'})
            }
    
    ### GET OLD RATING AND CHECK IF DISCIPLE EXISTS ###
    db = boto3.resource("dynamodb").Table("TutoringProfiles")
    response = db.get_item(Key={'uid': tutorUid})
    
    if 'Item' in response:
        profDoc = response['Item']
        
        rating    = profDoc['rating']
        disciples = profDoc['disciples']
    else:
        return {
            'statusCode': 404,
            'body': json.dumps({
                'Client-Error Description': 'Tutoring profile with uid=' + tutorUid + ' NOT FOUND.'
            })
        }
    
    ### CHANGE RATING DICT ###
    if discipleUid in disciples:
        if discipleUid in rating[ratingToAdd]:
            rating[ratingToAdd].remove(discipleUid)
            
            if len(rating[ratingToAdd]) == 0:
                rating[ratingToAdd].add('')
        else:
            if len(rating[ratingToAdd]) == 1 and '' in rating[ratingToAdd]:
                rating[ratingToAdd].remove('')
                
            rating[ratingToAdd].add(discipleUid)
            
            otherRatings = ["1","2","3","4","5"]
            otherRatings.remove(ratingToAdd)
            
            for r in otherRatings:
                rating[r].discard(discipleUid)
        
                if len(rating[r]) == 0:
                    rating[r].add('')
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({"Client-Error Description": "Disciple uid not in set of disciples"})
        }
    
    ### UPDATE TABLE ###
    try:
        response = db.update_item(
            Key={'uid': tutorUid},
            UpdateExpression="set rating=:r",
            ExpressionAttributeValues={
                ':r': rating
            },
            ReturnValues="ALL_NEW"
        )
        
        newRating = response['Attributes']['rating']
        
        return {
            'statusCode': 200,
            'body': json.dumps({"newRating": newRating}, default=jsonDumpsSetDefault)
        }
    except:
        return {
            'statusCode': 500,
            'body': json.dumps({"Server-Error Description": "Update to TutoringProfiles failed"})
        }