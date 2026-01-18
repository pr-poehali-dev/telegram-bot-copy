import json
import os
import requests

def handler(event: dict, context) -> dict:
    '''Настройка webhook для Telegram бота'''
    
    method = event.get('httpMethod', 'GET')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': '',
            'isBase64Encoded': False
        }
    
    try:
        bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        
        if not bot_token:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'TELEGRAM_BOT_TOKEN not configured'}),
                'isBase64Encoded': False
            }
        
        webhook_url = 'https://functions.poehali.dev/b82938a8-2ba3-4b26-bb32-083ef278deee'
        
        if method == 'POST':
            telegram_api_url = f'https://api.telegram.org/bot{bot_token}/setWebhook'
            response = requests.post(telegram_api_url, json={'url': webhook_url})
            result = response.json()
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'success': True,
                    'webhook_url': webhook_url,
                    'telegram_response': result
                }),
                'isBase64Encoded': False
            }
        else:
            telegram_api_url = f'https://api.telegram.org/bot{bot_token}/getWebhookInfo'
            response = requests.get(telegram_api_url)
            result = response.json()
            
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({
                    'webhook_info': result,
                    'expected_webhook': webhook_url
                }),
                'isBase64Encoded': False
            }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)}),
            'isBase64Encoded': False
        }
