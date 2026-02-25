# backend/Dockerfile
FROM python:3.11-slim

# system deps مورد نیاز (مثلاً برای build برخی پکیج‌ها) - کمی سبک نگه داشته شده
RUN apt-get update && apt-get install -y build-essential libpq-dev curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# copy requirements and install
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# copy app code
COPY . /app

# copy wait-for-it (اگر روی میزبان موجوده)
# اگر فایل روی هاست هست و در mount گذاشتیم، این خط optional است
COPY wait-for-it.sh /app/wait-for-it.sh
RUN chmod +x /app/wait-for-it.sh

ENV PYTHONUNBUFFERED=1
# command توسط docker-compose override میشه، ولی default هم داشته باشیم
CMD ["sh", "-c", "./wait-for-it.sh db:5432 -- python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]