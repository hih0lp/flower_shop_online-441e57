FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN python manage.py collectstatic --noinput 2>/dev/null || true
EXPOSE 8000
CMD python manage.py migrate &&     python -c "import django, os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flower_shop_online.settings'); django.setup(); from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin', 'admin@test.com', 'admin')" &&     gunicorn flower_shop_online.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
