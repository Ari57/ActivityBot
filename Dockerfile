FROM python:3.12.5

WORKDIR /app

copy requirements.txt requirements.txt
COPY bot.py bot.py

RUN pip install -r requirements.txt
CMD ["python", "bot.py"]