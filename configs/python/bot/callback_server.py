from threading import Thread
from typing import Annotated

import uvicorn
from fastapi import FastAPI, File, Form, UploadFile
from telebot.types import ReplyParameters
from tg_bot import bot, start_telebot_polling

callback_server = FastAPI()


@callback_server.post("/tg/sendMessageCallBack", tags=['tg'])
def sendMessageCallBack(user: Annotated[int, Form()], response_message: Annotated[int | None, Form()] = None,
                        additional: Annotated[str | None, Form()] = None, image: Annotated[UploadFile | None, File()] = None,
                        imageUrl: Annotated[str | None, Form()] = None):

    # print('PostCallBack', additional, flush=True)
    # print('PostCallBack', imageUrl, flush=True)
    if response_message:
        response_message = ReplyParameters(message_id=response_message)

    # FIXME new names of params
    if image is None:
        bot.send_message(chat_id=user, text=f"*{additional}*", parse_mode='Markdown',
                         reply_parameters=response_message)
    else:
        bot.send_photo(chat_id=user, reply_parameters=response_message,
                       photo=image.file, caption="Результат к запросу 👆")
    return {'message': 'done'}


if __name__ == "__main__":
    # Start telebot polling in a separate thread
    telebot_thread = Thread(target=start_telebot_polling)
    telebot_thread.start()

    # Start the FastAPI app using Uvicorn
    uvicorn.run("callback_server:callback_server",
                host="0.0.0.0", port=8080, reload=True)

    bot.stop_polling()
    telebot_thread.join()
    print('Bot stopped')
