FROM python:3.12.2-slim

WORKDIR /quotes-otd-telegram-bot

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY BOT_USERNAME .
COPY TOKEN .
COPY main.py .

CMD ["python", "./main.py"]