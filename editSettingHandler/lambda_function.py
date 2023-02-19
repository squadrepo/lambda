import json
import boto3

### EDIT SETTING HANDLER: {apiurl}/account/editSettings ###
# Created 2023-02-18 | Vegan Lroy
# LastRev 2023-02-19 | Vegan Lroy
#
# Lambda fn for handling update of user settings
# (i.e. university email, password, dob, univExclExp)
#
###########################################################

OLD_EMAIL, NEW_EMAIL = '', ''

# UPDATES DYNAMODB Users TABLE W/NEW USER SETTINGS
def update_user_table(settingJson):
    global OLD_EMAIL, NEW_EMAIL
    
    tableName = "Users"
    db = boto3.resource("dynamodb").Table(tableName)
    
    updExp = "SET "
    expAttrVals = {}
    keys = ['email','dob','univExclExp']
    
    for key in keys:
        if key in settingJson:
            aliasChar = ':' + key[0]
            
            updExp += key + "=" + aliasChar + ", "
            expAttrVals[aliasChar] = settingJson[key]
    
    updExp = updExp[:-2]
    
    try:
        res = db.update_item(
                Key={'uid': settingJson['uid']},
                UpdateExpression=updExp,
                ExpressionAttributeValues=expAttrVals,
                ReturnValues="UPDATED_OLD"
            )
        
        OLD_EMAIL = res['Attributes']['email']
        NEW_EMAIL = settingJson['email']
    except:
        return False
    else:
        return True

# UPDATES COGNITO W/NEW USER EMAIL and/or PASSWORD
def update_cognito(settingJson):
    global OLD_EMAIL, NEW_EMAIL
    
    if OLD_EMAIL.lower() == NEW_EMAIL.lower():
        pass
    
    return True

# ENDPOINT WRAPPER
def lambda_handler(event, context):
    data = json.loads(event['body'])
    
    rc = 204 if (update_user_table(data) and update_cognito(data)) else 500
    return {'statusCode': rc}
