@echo off
python -m venv venv
venv\Scripts\pip.exe install -i https://pypi.tuna.tsinghua.edu.cn/simple --trusted-host pypi.tuna.tsinghua.edu.cn --timeout 120 -r requirements.txt
venv\Scripts\python.exe manage.py makemigrations core
venv\Scripts\python.exe manage.py migrate
venv\Scripts\python.exe -c "import django,os;os.environ.setdefault('DJANGO_SETTINGS_MODULE','flower_shop_online.settings');django.setup();from core.models import User;User.objects.filter(username='admin').exists() or User.objects.create_superuser('admin','admin@test.com','admin')"
echo Server: http://127.0.0.1:8000  Admin: admin/admin
venv\Scripts\python.exe manage.py runserver