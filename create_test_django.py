import os
import zipfile

project_dir = 'test_django_project'
os.makedirs(project_dir, exist_ok=True)
os.makedirs(os.path.join(project_dir, 'test_project'), exist_ok=True)
os.makedirs(os.path.join(project_dir, 'app'), exist_ok=True)

manage_py = '''#!/usr/bin/env python
import os
import sys

def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'test_project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed/virtualenv activated?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
'''

settings_py = '''
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'django-insecure-test'
DEBUG = True
ALLOWED_HOSTS = []
INSTALLED_APPS = ['django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes', 'app']
ROOT_URLCONF = 'test_project.urls'
WSGI_APPLICATION = 'test_project.wsgi.application'
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'}}
'''

urls_py = '''
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('app.urls')),
]
'''

app_models_py = '''
from django.db import models

class Item(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name
'''

app_views_py = '''
from django.shortcuts import render
from django.http import HttpResponse
from .models import Item

def home(request):
    items = Item.objects.all()
    return render(request, 'home.html', {'items': items})

def about(request):
    return HttpResponse("About us")
'''

app_urls_py = '''
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
]
'''

with open(f'{project_dir}/manage.py', 'w') as f: f.write(manage_py)
with open(f'{project_dir}/test_project/__init__.py', 'w') as f: pass
with open(f'{project_dir}/test_project/settings.py', 'w') as f: f.write(settings_py)
with open(f'{project_dir}/test_project/urls.py', 'w') as f: f.write(urls_py)
with open(f'{project_dir}/app/__init__.py', 'w') as f: pass
with open(f'{project_dir}/app/models.py', 'w') as f: f.write(app_models_py)
with open(f'{project_dir}/app/views.py', 'w') as f: f.write(app_views_py)
with open(f'{project_dir}/app/urls.py', 'w') as f: f.write(app_urls_py)

zip_path = 'django_test_project.zip'
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, _, files in os.walk(project_dir):
        for file in files:
            file_path = os.path.join(root, file)
            zipf.write(file_path, os.path.relpath(file_path, project_dir))

print(f'Test Django project ZIP created at: {os.path.abspath(zip_path)}')
