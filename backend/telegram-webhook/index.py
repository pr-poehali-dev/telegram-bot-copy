import json
import os
import psycopg2
from datetime import datetime
import requests

def handler(event: dict, context) -> dict:
    '''Webhook для обработки сообщений Telegram бота с AI генерацией'''
    
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
            return {'statusCode': 200, 'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}, 'body': json.dumps({'ok': True}), 'isBase64Encoded': False}
        
        message = body['message']
        chat_id = message['chat']['id']
        user_id = message['from']['id']
        username = message['from'].get('username', '')
        first_name = message['from'].get('first_name', '')
        text = message.get('text', '')
        
        db_url = os.environ.get('DATABASE_URL')
        bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
        openai_key = os.environ.get('OPENAI_API_KEY', '')
        
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        
        cur.execute("SELECT telegram_id, is_premium, premium_until, free_requests_used, free_requests_limit, updated_at FROM users WHERE telegram_id = %s", (user_id,))
        user_data = cur.fetchone()
        
        if not user_data:
            cur.execute("INSERT INTO users (telegram_id, username, first_name) VALUES (%s, %s, %s)", (user_id, username, first_name))
            conn.commit()
            user_data = (user_id, False, None, 0, 2, datetime.now())
        
        telegram_id, is_premium, premium_until, requests_used, requests_limit, last_updated = user_data
        
        if last_updated:
            today = datetime.now().date()
            last_date = last_updated.date() if isinstance(last_updated, datetime) else datetime.strptime(str(last_updated), '%Y-%m-%d').date()
            
            if today > last_date and not is_premium:
                cur.execute("UPDATE users SET free_requests_used = 0, updated_at = CURRENT_TIMESTAMP WHERE telegram_id = %s", (user_id,))
                conn.commit()
                requests_used = 0
        
        if text == '/start':
            response_text = f"👋 Привет, {first_name}!\n\nЯ Neiro Bot — AI помощник.\n\n📊 Статус: {'🔥 Premium' if is_premium else f'🆓 Бесплатный ({requests_used}/{requests_limit} сегодня)'}\n\nКоманды:\n/help\n/premium\n/stats"
            send_message(bot_token, chat_id, response_text)
        
        elif text == '/help':
            response_text = "ℹ️ Помощь\n\n🆓 Бесплатно: 2 запроса/день\n👑 Premium: безлимит\n\nОтправь запрос, и я отвечу!"
            send_message(bot_token, chat_id, response_text)
        
        elif text == '/premium':
            response_text = "👑 Premium\n\n✅ Безлимитные запросы\n✅ Приоритет\n\n💳 499₽/мес\nКарта: 2200 7019 9538 11"
            send_message(bot_token, chat_id, response_text)
        
        elif text == '/stats':
            cur.execute("SELECT COUNT(*) FROM requests WHERE user_id = %s", (user_id,))
            total = cur.fetchone()[0]
            response_text = f"📊 Статистика\n\nСтатус: {'👑 Premium' if is_premium else '🆓 Бесплатный'}\nВсего: {total}\n{'Безлимит' if is_premium else f'Сегодня: {requests_used}/{requests_limit}'}"
            send_message(bot_token, chat_id, response_text)
        
        else:
            if not is_premium and requests_used >= requests_limit:
                send_message(bot_token, chat_id, "❌ Лимит исчерпан\n\nОбновится завтра или /premium")
            else:
                send_message(bot_token, chat_id, "⏳ Генерирую...")
                
                cur.execute("INSERT INTO requests (user_id, request_text, status) VALUES (%s, %s, %s) RETURNING id", (user_id, text, 'processing'))
                request_id = cur.fetchone()[0]
                conn.commit()
                
                ai_response = generate_response(openai_key, text)
                
                if not is_premium:
                    cur.execute("UPDATE users SET free_requests_used = free_requests_used + 1, updated_at = CURRENT_TIMESTAMP WHERE telegram_id = %s", (user_id,))
                
                cur.execute("UPDATE requests SET response_text = %s, status = %s, completed_at = CURRENT_TIMESTAMP WHERE id = %s", (ai_response, 'completed', request_id))
                conn.commit()
                
                send_message(bot_token, chat_id, f"✅ Ответ:\n\n{ai_response}")
        
        cur.close()
        conn.close()
        
        return {'statusCode': 200, 'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}, 'body': json.dumps({'ok': True}), 'isBase64Encoded': False}
    
    except Exception as e:
        return {'statusCode': 500, 'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'}, 'body': json.dumps({'error': str(e)}), 'isBase64Encoded': False}


def generate_response(api_key: str, prompt: str) -> str:
    if not api_key:
        return "⚠️ API ключ не настроен"
    
    try:
        url = 'https://api.openai.com/v1/chat/completions'
        headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
        data = {'model': 'gpt-3.5-turbo', 'messages': [{'role': 'system', 'content': 'Ты AI-ассистент. Отвечай кратко на русском.'}, {'role': 'user', 'content': prompt}], 'max_tokens': 500}
        
        response = requests.post(url, headers=headers, json=data, timeout=25)
        response.raise_for_status()
        
        return response.json()['choices'][0]['message']['content'].strip()
    except:
        return "❌ Ошибка генерации"


def send_message(bot_token: str, chat_id: int, text: str):
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    requests.post(url, json={'chat_id': chat_id, 'text': text}, timeout=5)
