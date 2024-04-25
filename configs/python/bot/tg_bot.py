import logging
import os

import requests
import telebot
from telebot.types import Message

logging.basicConfig(level=logging.INFO,
                    format="\033[93m%(levelname)s\033[0m: %(message)s - function: %(funcName)s - line: %(lineno)d - %(asctime)s", datefmt="%Y-%m-%d %H:%M:%S")


# Задаем параметры для Telegram бота
bot_token = os.environ.get('token')
bot = telebot.TeleBot(bot_token)


@bot.message_handler(content_types=['text'])
@bot.message_handler(commands=['start'])
def start(message: Message):
    bot.reply_to(
        message,  "Привет! Отправь мне два сообщения.\n1. Фото лица, которое хотите перенести.\n2. Фото, куда хотите перенести.")


prev_image_user: dict[int, str] = {}


@bot.message_handler(content_types=['photo'])
def photo_handler(message: Message):
    """Обработчик фотографий от пользователя"""
    # Получаем информацию о фотографии
    photo = message.photo[-1]  # Берем фотографию наибольшего размера
    file_id = photo.file_id
    # Получаем прямую ссылку на файл
    url = bot.get_file_url(file_id)
    chat_id = message.chat.id
    prev_image_url = prev_image_user.pop(chat_id, None)
    if prev_image_url is None:
        prev_image_user[chat_id] = url
        return

    # Отправляем POST запрос на ваш сервер с URL фотографии
    data = {'secret': 'tgbotToFaceBotSecret',
            'sourceUrl': prev_image_url,
            'targetUrl': url,
            'callbackUrl': 'http://callbackserver:8080/tg/sendMessageCallBack',
            'callbackTemplate': {'secret': 'faceBotToCallbackServerSecret',
                                 'user': chat_id,
                                 'response_message': message.message_id
                                 }
            }  # Отправляем список с одним URL
    response = requests.post('http://facebot:80/api/swap', json=data).json()

    # Отправляем ответ пользователю в Telegram
    bot.reply_to(message, "_В это изображение будет производиться перемещение. Процесс добавлен в очередь._", parse_mode='Markdown')


# Запуск бота
def start_telebot_polling():
    print("Bot starting...")
    bot.infinity_polling()
