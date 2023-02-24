import time
import boto3
from boto3.dynamodb.conditions import Attr

NUM_SECONDS_IN_DAY = 86400  # seconds in a day
NUM_DAYS_TO_REVERIFY = 730.5  # currently 2 years
USER_POOL_ID = "us-east-1_qKu4owaQ6"


def lambda_handler(event, context):
    tableName = "Users"
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(tableName)

    reverificationCutoffTime = int(time.time(
    ) - (NUM_DAYS_TO_REVERIFY * NUM_SECONDS_IN_DAY))

    filterExp = Attr('emailLastVerifiedDate').lt(
        reverificationCutoffTime)

    response = table.scan(FilterExpression=filterExp)
    usersToReVerify = response['Items']

    while 'LastEvaluatedKey' in response:
        response = table.scan(FilterExpression=filterExp,
                              ExclusiveStartKey=response['LastEvaluatedKey'])
        usersToReVerify.extend(response['Items'])

    cognito = boto3.client('cognito-idp')

    for user in usersToReVerify:
        print(user["username"])
        try:
            # Set email to one of our emails, so that we can trigger re-verification by setting back to their email
            cognito.admin_update_user_attributes(
                UserPoolId=USER_POOL_ID,
                Username=user['username'],
                UserAttributes=[
                    {
                        'Name': 'email',
                        'Value': 'squad.app.aws@gmail.com',
                    },
                    {
                        'Name': 'email_verified',
                        'Value': 'true',
                    },
                ],
            )

            # Set email back to their actual email to trigger reverification
            cognito.admin_update_user_attributes(
                UserPoolId=USER_POOL_ID,
                Username=user['username'],
                UserAttributes=[
                    {
                        'Name': 'email',
                        'Value': user["email"],
                    },
                ],
            )
        except Exception as e:
            print(e)
            pass

    return event['time']
