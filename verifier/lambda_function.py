import json
import boto3
from layer import isAcademicEmail, getUniversityFromEmail

tableName = "Schools"
db = boto3.resource("dynamodb").Table(tableName)


def lambda_handler(event, context):
    event['response']['autoConfirmUser'] = False

    email = event['request']['userAttributes']['email']
    print(isAcademicEmail(email))
    if isAcademicEmail(email) == False:
        raise Exception(
            "Email must be a .edu email from a verified institution.")

    return event

    # test = isAcademic(event['key1'])
    # test2 = getName(event['key1'])

    # print(test)
    # print(test2)
