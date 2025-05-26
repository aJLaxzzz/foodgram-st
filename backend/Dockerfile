FROM python:3.9-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /app/media/recipes/images

RUN chmod +x entrypoint.sh

# Выполнение миграций и сборки статики при сборке образа
RUN python manage.py makemigrations
RUN python manage.py migrate --run-syncdb
RUN python manage.py collectstatic --noinput

ENTRYPOINT ["./entrypoint.sh"]

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0.0.0.0:8000"]
