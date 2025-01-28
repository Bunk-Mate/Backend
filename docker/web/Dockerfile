FROM python:3.12.4-slim
WORKDIR /app
RUN apt update
RUN apt install -y curl

COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt --no-cache-dir
COPY . .

CMD python manage.py runserver 0.0.0.0:8000
EXPOSE 8000
ENTRYPOINT [ "./docker-entrypoint.sh" ]
