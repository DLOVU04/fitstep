import os
import json
import time
import requests
from dotenv import load_dotenv

# Загружаем настройки
load_dotenv()

with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# Берем токен из .env
TOKEN = os.getenv('BOT_TOKEN')
API_URL = f"https://api.telegram.org/bot{TOKEN}/"
ADMIN_ID = os.getenv('ADMIN_ID')

# Импортируем наши модули
from utils.database import save_user, get_user, save_steps
from utils.scheduler import setup_scheduler
from handlers.messages import handle_message
from handlers.commands import handle_command


def get_updates(offset=None):
    """Получаем обновления от Telegram"""
    url = f"{API_URL}getUpdates"
    params = {'timeout': 30, 'offset': offset}

    try:
        response = requests.get(url, params=params, timeout=35)
        return response.json().get('result', [])
    except Exception as e:
        print(f"Ошибка при получении updates: {e}")
        return []


def send_message(chat_id, text):
    """Отправляем сообщение пользователю"""
    url = f"{API_URL}sendMessage"
    params = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'
    }

    requests.post(url, json=params)


def process_update(update):
    """Обрабатываем одно обновление"""
    if 'message' not in update:
        return

    message = update['message']
    chat_id = message['chat']['id']
    user_info = message.get('from', {})

    # Сохраняем пользователя если его нет
    save_user(chat_id, user_info.get('username', 'Нет имени'))

    # Определяем тип сообщения
    if 'text' in message:
        text = message['text']

        # Проверяем команду
        if text.startswith('/'):
            handle_command(chat_id, text)
        else:
            # Если это число - сохраняем как шаги
            handle_message(chat_id, text)

    elif 'location' in message:
        # Обработка геолокации
        lat = message['location']['latitude']
        lon = message['location']['longitude']

        # Получаем адрес (упрощенная версия)
        try:
            response = requests.get(
                f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json",
                headers={'User-Agent': 'FitStepBot/1.0'}
            )
            address = response.json().get('display_name', 'Адрес не определен')
            send_message(chat_id, f"📍 Вы находитесь: {address}")
        except:
            send_message(chat_id, "📍 Спасибо за локацию!")


def main():
    """Главный цикл бота"""
    print("🤖 Бот запущен...")
    offset = 0

    # Запускаем планировщик задач
    setup_scheduler()

    # Главный цикл опроса
    while True:
        try:
            updates = get_updates(offset)

            for update in updates:
                process_update(update)
                offset = update['update_id'] + 1

                # Делаем паузу между обработкой сообщений
                time.sleep(1)

        except Exception as e:
            print(f"Ошибка в main: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
