import boto3


def layerTestPrint():
    print("Accessed Lambda layer function")


def isAcademicEmail(email):
    tableName = "Schools"
    db = boto3.resource("dynamodb").Table(tableName)
    email = email.strip()
    email = email.lower()
    temp = email.split("@")
    temp2 = temp[1].split(".")
    domainName = temp2[0]
    domain = temp2[1]
    if domain != "edu":
        return False
    try:
        response = db.get_item(
            Key={'domain': domainName}
        )
        if len(response["Item"]) == 0:
            return False
    except:
        return False

    return True


def getUniversityFromEmail(email):
    tableName = "Schools"
    db = boto3.resource("dynamodb").Table(tableName)
    email = email.strip()
    email = email.lower()
    temp = email.split("@")
    temp2 = temp[1].split(".")
    domainName = temp2[0]

    exp = 'name'
    try:
        response = db.get_item(
            Key={'domain': domainName}
        )
    except:
        return 'error: could not retrieve'
    return response['Item']['name']
