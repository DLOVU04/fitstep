
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
API_URL = f"https://api.telegram.org/bot{TOKEN}/"
ADMIN_ID = os.getenv('ADMIN_ID')


def send_message(chat_id, text):
    """Функция для отправки сообщений"""
    url = f"{API_URL}sendMessage"
    params = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'
    }

    requests.post(url, json=params, timeout=10)


def morning_task():
    """Утренняя рассылка в 8:00"""
    print("⏰ Выполняем утреннюю рассылку...")

    try:
        # Читаем сообщение из файла
        with open('data/morning_message.txt', 'r', encoding='utf-8') as f:
            message = f.read()

        # Получаем всех пользователей
        from utils.database import get_user
        import csv

        if os.path.exists('data/users.csv'):
            with open('data/users.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                users = list(reader)

                # Отправляем каждому пользователю
                for user in users[:10]:  # Первым 10 чтобы не заблокировали
                    send_message(user['chat_id'], message)
                    import time
                    time.sleep(1)  # Пауза между сообщениями

    except Exception as e:
        print(f"Ошибка в утренней рассылке: {e}")


def evening_task():
    """Вечернее напоминание в 21:00"""
    print("🌙 Отправляем вечернее напоминание...")

    message = "🌆 Не забудьте внести количество шагов за сегодня!\nПросто отправьте число в чат."

    # Тут тоже бы рассылку по пользователям, но для примера просто в лог
    print(message)


def admin_report_task():
    """Отчет админу в 23:55"""
    print("📊 Отправляем отчет админу...")

    from utils.database import get_daily_report
    report = get_daily_report()

    send_message(ADMIN_ID, report)


def setup_scheduler():
    """Настраиваем планировщик задач"""
    scheduler = BackgroundScheduler()

    # Добавляем задачи
    scheduler.add_job(morning_task, 'cron', hour=8, minute=0)
    scheduler.add_job(evening_task, 'cron', hour=21, minute=0)
    scheduler.add_job(admin_report_task, 'cron', hour=23, minute=55)

    # Запускаем
    scheduler.start()
    print("✅ Планировщик запущен")

    return scheduler
