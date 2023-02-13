import json
from layer import layerTestPrint

def lambda_handler(event, context):
    # TODO implement
    layerTestPrint()
    return {
        'statusCode': 200,
        'body': json.dumps(event)
    }