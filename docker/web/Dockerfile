FROM python:3.12.4-alpine
WORKDIR /app
COPY requirements.txt .
# required dependencies for building psycopg
RUN \
	apk add --no-cache python3 postgresql-libs && \
	apk add --no-cache --virtual .build-deps gcc python3-dev musl-dev postgresql-dev && \
	python3 -m pip install -r requirements.txt --no-cache-dir && \
	apk --purge del .build-deps
COPY . .
CMD python manage.py runserver 0.0.0.0:8000
EXPOSE 8000
ENTRYPOINT [ "./docker-entrypoint.sh" ]
