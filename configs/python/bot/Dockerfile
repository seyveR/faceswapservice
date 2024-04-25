FROM python:3.11-slim as bot

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./callback_server.py ./tg_bot.py /code/

EXPOSE 8080

CMD ["python", "callback_server.py"]