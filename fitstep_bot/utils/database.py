
import csv
from datetime import datetime
import os

# Создаем папку data если её нет
if not os.path.exists('data'):
    os.makedirs('data')


def save_user(chat_id, username):
    """Сохраняем пользователя в CSV"""
    filename = 'data/users.csv'

    # Проверяем есть ли файл
    if not os.path.exists(filename):
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['chat_id', 'username', 'weight', 'goal', 'registered'])

    # Проверяем есть ли пользователь
    user_exists = False
    users = []

    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        users = list(reader)

        for user in users:
            if user['chat_id'] == str(chat_id):
                user_exists = True
                break

    # Если пользователя нет - добавляем
    if not user_exists:
        with open(filename, 'a', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([chat_id, username, 70, 10000, datetime.now().strftime('%Y-%m-%d')])

        return True
    return False


def get_user(chat_id):
    """Получаем данные пользователя"""
    filename = 'data/users.csv'

    if not os.path.exists(filename):
        return None

    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['chat_id'] == str(chat_id):
                return row

    return None


def save_steps(chat_id, steps):
    """Сохраняем шаги за сегодня"""
    filename = 'data/steps.csv'
    today = datetime.now().strftime('%Y-%m-%d')

    # Создаем файл если нет
    if not os.path.exists(filename):
        with open(filename, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['chat_id', 'date', 'steps', 'calories'])

    # Получаем вес пользователя для расчета калорий
    user = get_user(chat_id)
    weight = int(user['weight']) if user else 70

    # Простая формула расчета калорий
    calories = int(steps) * 0.05 * weight

    # Сохраняем
    with open(filename, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([chat_id, today, steps, round(calories, 2)])

    return calories


def get_daily_report():
    """Генерируем отчет за день для админа"""
    filename = 'data/steps.csv'
    today = datetime.now().strftime('%Y-%m-%d')

    if not os.path.exists(filename):
        return "Нет данных за сегодня"

    total_steps = 0
    user_count = 0

    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['date'] == today:
                total_steps += int(row['steps'])
                user_count += 1

    report = f"📊 Отчет за {today}:\n"
    report += f"Пользователей: {user_count}\n"
    report += f"Всего шагов: {total_steps:,}\n"
    report += f"В среднем на человека: {total_steps // max(user_count, 1):,}"

    return report


