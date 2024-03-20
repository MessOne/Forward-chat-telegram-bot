import sqlite3
import time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, MessageHandler, CallbackContext, ApplicationBuilder

# Замените 'YOUR_TOKEN' на ваш токен
TOKEN = 'YOUR_TOKEN'
# Замените 'YOUR_ID_CHAT' на ваш токен
DESTINATION_CHAT_ID = 'YOUR_ID_CHAT'

# Функция для инициализации базы данных SQLite
def initialize_database():
    connection = sqlite3.connect('user_data.db')
    cursor = connection.cursor()

    # Создание таблицы для хранения времени отправки сообщения каждого пользователя
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        last_message_sent INTEGER
                    )''')
    
    connection.commit()
    connection.close()

# Функция для обновления времени последнего сообщения пользователя
def update_last_message_sent(user_id):
    connection = sqlite3.connect('user_data.db')
    cursor = connection.cursor()

    current_time = int(time.time())
    cursor.execute("REPLACE INTO users (user_id, last_message_sent) VALUES (?, ?)", (user_id, current_time))

    connection.commit()
    connection.close()

# Функция для проверки, прошло ли уже 24 часа с момента последнего сообщения пользователя
def is_24_hours_passed(user_id):
    connection = sqlite3.connect('user_data.db')
    cursor = connection.cursor()

    cursor.execute("SELECT last_message_sent FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()

    if result:
        last_message_sent_time = result[0]
        current_time = int(time.time())
        return current_time - last_message_sent_time >= 24 * 60 * 60
    else:
        return True  # Возвращаем True, если пользователь не отправлял сообщений ранее

# Функция для обработки команды /start
async def start(update: Update, context: CallbackContext) -> None:
    StartMassageText = """
    YOUR_TEXT
""" # Введите любое сообщение для вывода после нажатия /start
    keyboard = [
        [InlineKeyboardButton("YOUR_BUTTON_TEXT", url="https://example.com")] # Добавляет кнопку под сообщением 
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(text=StartMassageText, reply_markup=reply_markup, parse_mode='Markdown')

# Функция для обработки сообщений с фото и текстом
async def handle_message(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    # Проверяем, прошло ли уже 24 часа с момента последнего сообщения пользователя
    if is_24_hours_passed(user_id):
        photo = update.message.photo[-1]  # Получаем последнюю (самую большую) фотографию
        photo_caption = update.message.caption if update.message.caption else ''
        PhotoAndText = update.message.text if update.message.text else ''
        
        # Отправляем фото с текстом в другой чат
        await context.bot.send_photo(chat_id=DESTINATION_CHAT_ID, photo=photo.file_id, caption=f"{photo_caption}\n{PhotoAndText}", parse_mode='HTML')

        # Обновляем время последнего сообщения пользователя
        update_last_message_sent(user_id)
    else:
        await update.message.reply_text('Вы уже отправляли фото с текстом менее чем 24 часа назад.')

def main() -> None:
    # Инициализируем базу данных
    initialize_database()

    app = ApplicationBuilder().token(TOKEN).build()

    # Обработчики команд
    app.add_handler(CommandHandler("start", start))

    # Обработчик сообщений с фото и текстом
    app.add_handler(MessageHandler(None, handle_message))

    # Запускаем бота
    app.run_polling()
    
if __name__ == '__main__':
    main()
