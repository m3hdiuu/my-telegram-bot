FROME python:3.9-slim
WORKDIR \app
COPY requirements.txt
COPY . .
CMD ["python", "bot.py"]
