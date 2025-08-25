from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo


# Главное меню
main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="💼 Личный кабинет"),
            KeyboardButton(text="📊 Посмотреть портфель")
        ],
        [
            KeyboardButton(text="➕ Добавить монету"),
            KeyboardButton(text="🌐 Веб-приложение", web_app=WebAppInfo(url="https://your-ngrok-url.ngrok-free.app"))
        ]
    ],
    resize_keyboard=True
)

# Клавиатура для добавления монеты
add_coin_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="❌ Отмена")
        ]
    ],
    resize_keyboard=True
) 