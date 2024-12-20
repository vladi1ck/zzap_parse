import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zzap_admin.settings')
app = Celery('zzap_admin')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()