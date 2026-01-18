
from utils.database import save_steps, get_user


def handle_message(chat_id, text):
    """Обрабатываем текстовые сообщения"""

    # Проверяем число ли это
    if text.isdigit():
        steps = int(text)

        if steps > 0:
            # Сохраняем шаги
            calories = save_steps(chat_id, steps)

            # Получаем данные пользователя
            user = get_user(chat_id)

            if user:
                goal = int(user['goal'])

                # Сравнение с целью
                if steps >= goal:
                    message = f"🎉 Отлично! Вы достигли цели!\n"
                    message += f"Шаги: {steps:,}\n"
                    message += f"Сожжено калорий: {calories:.0f}\n"
                    message += f"Это примерно {calories / 50:.0f} яблок 🍎"
                else:
                    remaining = goal - steps
                    percentage = (steps / goal) * 100

                    # Создаем прогресс-бар
                    bars = int(percentage / 10)
                    progress_bar = '[' + '=' * bars + '-' * (10 - bars) + ']'

                    message = f"📊 Вы прошли {steps:,} шагов\n"
                    message += f"Прогресс: {progress_bar} {percentage:.0f}%\n"
                    message += f"До цели: {remaining:,} шагов\n"
                    message += f"Калории: {calories:.0f}"
            else:
                message = f"✅ Сохранено: {steps} шагов"
        else:
            message = "Введите положительное число шагов"
    else:
        message = "Отправьте количество шагов (только число)"

    # Импортируем тут чтобы избежать циклического импорта
    import requests
    import os
    from dotenv import load_dotenv

    load_dotenv()
    TOKEN = os.getenv('BOT_TOKEN')
    API_URL = f"https://api.telegram.org/bot{TOKEN}/"

    # Отправляем ответ
    url = f"{API_URL}sendMessage"
    params = {
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown'
    }

    requests.post(url, json=params)


