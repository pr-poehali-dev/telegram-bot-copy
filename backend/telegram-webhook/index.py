import json
import os
import psycopg2
from datetime import datetime, timedelta
import requests

def handler(event: dict, context) -> dict:
    '''Webhook для обработки сообщений от Telegram бота'''
    
    method = event.get('httpMethod', 'POST')
    
    if method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': '',
            'isBase64Encoded': False
        }
    
    if method != 'POST':
        return {
            'statusCode': 405,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Method not allowed'}),
            'isBase64Encoded': False
        }
    
    try:
        body = json.loads(event.get('body', '{}'))
        
        if 'message' not in body:
            return {
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'ok': True}),
                'isBase64Encoded': False
            }
        
        message = body['message']
        chat_id = message['chat']['id']
        user_id = message['from']['id']
        username = message['from'].get('username', '')
        first_name = message['from'].get('first_name', '')
        text = message.get('text', '')
        
        db_url = os.environ.get('DATABASE_URL')
        bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        cur.execute(
            "SELECT telegram_id, is_premium, premium_until, free_requests_used, free_requests_limit FROM users WHERE telegram_id = %s",
            (user_id,)
        )
        user_data = cur.fetchone()
        
        if not user_data:
            cur.execute(
                "INSERT INTO users (telegram_id, username, first_name) VALUES (%s, %s, %s)",
                (user_id, username, first_name)
            )
            conn.commit()
            user_data = (user_id, False, None, 0, 2)
        
        telegram_id, is_premium, premium_until, requests_used, requests_limit = user_data
        
        if premium_until and datetime.now() > premium_until:
            cur.execute(
                "UPDATE users SET is_premium = FALSE WHERE telegram_id = %s",
                (user_id,)
            )
            conn.commit()
            is_premium = False
        
        if text == '/start':
            response_text = (
                f"👋 Привет, {first_name}!\n\n"
                f"Я Neiro Bot — твой помощник для генерации изображений и текстов с помощью нейросети.\n\n"
                f"📊 Твой статус:\n"
                f"{'🔥 Premium подписка' if is_premium else f'🆓 Бесплатный тариф ({requests_used}/{requests_limit} запросов)'}\n\n"
                f"Доступные команды:\n"
                f"/help — помощь\n"
                f"/premium — оформить Premium\n"
                f"/stats — моя статистика\n\n"
                f"Просто отправь мне запрос, и я его обработаю!"
            )
            send_telegram_message(bot_token, chat_id, response_text)
        
        elif text == '/help':
            response_text = (
                "ℹ️ Помощь по боту\n\n"
                "Отправь мне текстовый запрос, и я обработаю его с помощью нейросети.\n\n"
                "🆓 Бесплатный тариф: 2 запроса в день\n"
                "👑 Premium: безлимитные запросы\n\n"
                "Команды:\n"
                "/start — начать работу\n"
                "/premium — оформить Premium\n"
                "/stats — статистика"
            )
            send_telegram_message(bot_token, chat_id, response_text)
        
        elif text == '/premium':
            response_text = (
                "👑 Premium подписка\n\n"
                "Преимущества:\n"
                "✅ Безлимитные запросы\n"
                "✅ Приоритетная обработка\n"
                "✅ Расширенная поддержка\n"
                "✅ Полная история запросов\n\n"
                "💳 Стоимость: 499 ₽/месяц\n\n"
                "Для оплаты переведите 499 ₽ на карту:\n"
                "2200 7019 9538 11\n\n"
                "После оплаты напишите в поддержку."
            )
            send_telegram_message(bot_token, chat_id, response_text)
        
        elif text == '/stats':
            cur.execute(
                "SELECT COUNT(*) FROM requests WHERE user_id = %s",
                (user_id,)
            )
            total_requests = cur.fetchone()[0]
            
            response_text = (
                f"📊 Твоя статистика\n\n"
                f"Статус: {'👑 Premium' if is_premium else '🆓 Бесплатный'}\n"
                f"Всего запросов: {total_requests}\n"
                f"{'Безлимитный доступ' if is_premium else f'Использовано сегодня: {requests_used}/{requests_limit}'}"
            )
            send_telegram_message(bot_token, chat_id, response_text)
        
        else:
            if not is_premium and requests_used >= requests_limit:
                response_text = (
                    "❌ Лимит бесплатных запросов исчерпан\n\n"
                    "Оформите Premium подписку для безлимитного доступа: /premium"
                )
                send_telegram_message(bot_token, chat_id, response_text)
            else:
                cur.execute(
                    "INSERT INTO requests (user_id, request_text, status) VALUES (%s, %s, %s) RETURNING id",
                    (user_id, text, 'completed')
                )
                request_id = cur.fetchone()[0]
                
                if not is_premium:
                    cur.execute(
                        "UPDATE users SET free_requests_used = free_requests_used + 1, updated_at = CURRENT_TIMESTAMP WHERE telegram_id = %s",
                        (user_id,)
                    )
                
                response_text = f"✅ Запрос обработан!\n\n📝 Ваш запрос:\n{text}\n\n💬 Ответ:\nОтвет нейросети (ID: {request_id})"
                
                cur.execute(
                    "UPDATE requests SET response_text = %s, completed_at = CURRENT_TIMESTAMP WHERE id = %s",
                    (response_text, request_id)
                )
                
                conn.commit()
                send_telegram_message(bot_token, chat_id, response_text)
        
        cur.close()
        conn.close()
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'ok': True}),
            'isBase64Encoded': False
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': str(e)}),
            'isBase64Encoded': False
        }


def send_telegram_message(bot_token: str, chat_id: int, text: str):
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    data = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    requests.post(url, json=data)
