import json
import os

def lambda_handler(event, context):
    """
    Lambda-функция
    """
    print(f"Received event: {json.dumps(event)}")

    # Ваша бизнес-логика здесь
    name = event.get('queryStringParameters', {}).get('name', ['Bro'])[0]

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json'
        },
        'body': json.dumps({
            'message': f'Hello, {name}! This is prod environment',
            'method': event.get('httpMethod'),
            'path': event.get('path'),
            'version': '4.0'
        })
    }