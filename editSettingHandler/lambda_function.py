import json, boto3, datetime
from layer import isAcademicEmail, getUniversityFromEmail

### EDIT SETTING HANDLER: {apiurl}/account/editSettings ###
# Created 2023-02-18 | Vegan Lroy
# LastRev 2023-02-24 | Vegan Lroy
#
# Lambda fn for handling update of user settings
# (i.e. university email, password, dob, univExclExp)
#
###########################################################

OLD_EMAIL, NEW_EMAIL, USER_NAME = '', '', ''

# UPDATES DYNAMODB Users TABLE W/NEW USER SETTINGS
def update_user_table(settingJson):
    global OLD_EMAIL, NEW_EMAIL, USER_NAME
    
    tableName = "Users"
    db = boto3.resource("dynamodb").Table(tableName)
    
    updExp = "SET "
    expAttrVals = {}
    keys = ['email','dob','univExclExp']
    
    updatingAtLeastOne = False
    for key in keys:
        if key in settingJson:
            updatingAtLeastOne = True
            if key == 'email':
                updExp += 'univ=:c, '
                expAttrVals[':c'] = getUniversityFromEmail(settingJson[key])
                
                updExp += 'emailLastVerifiedDate=:v, '
                expAttrVals[':v'] = int(datetime.datetime.now().timestamp())
                
            aliasChar = ':' + key[0]
            
            updExp += key + "=" + aliasChar + ", "
            expAttrVals[aliasChar] = settingJson[key]
    
    if updatingAtLeastOne:
        updExp = updExp[:-2]
        
        try:
            res = db.update_item(
                    Key={'uid': settingJson['uid']},
                    UpdateExpression=updExp,
                    ExpressionAttributeValues=expAttrVals,
                    ReturnValues="ALL_OLD"
                )
            
            USER_NAME = res['Attributes']['username']
            
            if 'email' in settingJson:
                OLD_EMAIL = res['Attributes']['email']
                NEW_EMAIL = settingJson['email']
        except:
            return False
        else:
            return True
    else:
        return True

# UPDATES COGNITO W/NEW USER EMAIL and/or PASSWORD
def update_cognito(settingJson):
    global OLD_EMAIL, NEW_EMAIL, USER_NAME
    
    client = boto3.client('cognito-idp')
    poolId = "us-east-1_qKu4owaQ6"
    
    if 'email' in settingJson and OLD_EMAIL.lower() != NEW_EMAIL.lower():
        try:
            res = client.admin_update_user_attributes(
                UserPoolId=poolId,
                Username=USER_NAME,
                UserAttributes=[{'Name':'email','Value':NEW_EMAIL}]
            )
        except:
            return False
    
    if 'password' in settingJson:
        try:
            res = client.admin_set_user_password(
                UserPoolId=poolId,
                Username=USER_NAME,
                Password=settingJson['password'],
                Permanent=True
            )
        except:
            return False
    
    return True

# ENDPOINT WRAPPER
def lambda_handler(event, context):
    data = json.loads(event['body'])
    
    if 'email' in data and not isAcademicEmail(data['email']):
        return {
            'statusCode': 400,
            'body': json.dumps({'Client-Error Description': 'Not academic email'})
        }
    
    rc = 204 if (update_user_table(data) and update_cognito(data)) else 500
    return {'statusCode': rc}