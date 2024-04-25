FROM python:3.11-slim

WORKDIR /code

RUN apt-get update && apt-get install -y build-essential && apt-get install -y ffmpeg && apt-get install -y git-all
RUN pip install --upgrade pip

COPY ./home/roop/roop/requirements-headless.txt /code/roop-requirements.txt
RUN pip install --no-cache-dir --upgrade --break-system-packages -r /code/roop-requirements.txt

COPY ./server/requirements.txt /code/server-requirements.txt
RUN pip install --no-cache-dir --upgrade --break-system-packages -r /code/server-requirements.txt


EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "80"]