from utils.database import get_user
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
API_URL = f"https://api.telegram.org/bot{TOKEN}/"


def send_message(chat_id, text):
    """Вспомогательная функция отправки"""
    import requests
    url = f"{API_URL}sendMessage"
    params = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'Markdown'
    }
    requests.post(url, json=params)


def handle_command(chat_id, command_text):
    """Обрабатываем команды"""

    # Убираем / и разделяем команду и аргументы
    parts = command_text[1:].split('_', 1)
    command = parts[0]
    args = parts[1] if len(parts) > 1 else None

    match command:
        case 'start':
            message = "👋 Привет! Я бот для отслеживания шагов.\n\n"
            message += "📱 *Как использовать:*\n"
            message += "• Просто отправь число - я сохраню его как шаги\n"
            message += "• /me - твоя статистика\n"
            message += "• /goal_10000 - установить цель\n"
            message += "• /weight_70 - установить вес\n"
            message += "• /help - помощь\n\n"
            message += "🚶 *Начни сейчас:* отправь сколько шагов ты прошел сегодня!"

        case 'me':
            user = get_user(chat_id)
            if user:
                import csv
                from datetime import datetime

                today = datetime.now().strftime('%Y-%m-%d')
                steps_today = 0

                # Ищем шаги за сегодня
                if os.path.exists('data/steps.csv'):
                    with open('data/steps.csv', 'r', encoding='utf-8') as f:
                        reader = csv.DictReader(f)
                        for row in reader:
                            if row['chat_id'] == str(chat_id) and row['date'] == today:
                                steps_today = int(row['steps'])
                                break

                goal = int(user['goal'])
                weight = int(user['weight'])

                # Определяем уровень
                match steps_today:
                    case s if s < 5000:
                        level = "Новичок 🐣"
                    case s if s < 10000:
                        level = "Ходок 🚶"
                    case s if s < 15000:
                        level = "Спортсмен 🏃"
                    case s if s < 20000:
                        level = "Мастер 🥇"
                    case _:
                        level = "Легенда 🏆"

                # Прогресс-бар
                percentage = min((steps_today / goal) * 100, 100) if goal > 0 else 0
                bars = int(percentage / 10)
                progress_bar = '[' + '=' * bars + '-' * (10 - bars) + ']'

                message = f"📊 *Твоя статистика*\n\n"
                message += f"🎯 Цель: {goal:,} шагов\n"
                message += f"⚖️ Вес: {weight} кг\n"
                message += f"👣 Сегодня: {steps_today:,} шагов\n"
                message += f"📈 Прогресс: {progress_bar} {percentage:.0f}%\n"
                message += f"🏆 Уровень: {level}"
            else:
                message = "Сначала используй /start"

        case 'help':
            message = "🤖 *Помощь по командам:*\n\n"
            message += "• /start - начать работу\n"
            message += "• /me - моя статистика\n"
            message += "• /goal_10000 - установить цель\n"
            message += "• /weight_70 - установить вес\n"
            message += "• Просто число - сохранить шаги\n"
            message += "• Отправь локацию - увидишь адрес"

        case 'goal' if args and args.isdigit():
            # Обновляем цель пользователя
            goal = int(args)
            import csv

            # Читаем всех пользователей
            users = []
            with open('data/users.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                users = list(reader)

            # Обновляем нужного пользователя
            for user in users:
                if user['chat_id'] == str(chat_id):
                    user['goal'] = str(goal)
                    break

            # Записываем обратно
            with open('data/users.csv', 'w', encoding='utf-8', newline='') as f:
                fieldnames = ['chat_id', 'username', 'weight', 'goal', 'registered']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(users)

            message = f"🎯 Цель обновлена: {goal:,} шагов в день!"

        case 'weight' if args and args.isdigit():
            # Обновляем вес пользователя
            weight = int(args)
            import csv

            users = []
            with open('data/users.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                users = list(reader)

            for user in users:
                if user['chat_id'] == str(chat_id):
                    user['weight'] = str(weight)
                    break

            with open('data/users.csv', 'w', encoding='utf-8', newline='') as f:
                fieldnames = ['chat_id', 'username', 'weight', 'goal', 'registered']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(users)

            message = f"⚖️ Вес обновлен: {weight} кг"

        case _:
            message = "Неизвестная команда. Используй /help"

    send_message(chat_id, message)
