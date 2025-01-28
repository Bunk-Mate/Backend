FROM python:3.12.4-slim
WORKDIR /app

COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt --no-cache-dir

COPY . .
CMD celery -A tasks worker -l info
