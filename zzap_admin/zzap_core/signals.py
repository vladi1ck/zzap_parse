from django.contrib.auth.models import User
from django.db.models.signals import post_migrate
from django.dispatch import receiver

from zzap_core.models import Timeouts, Search


@receiver(post_migrate)
def create_initial_data(sender, **kwargs):
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(username='admin', password='admin')
        print("Суперпользователь 'admin' создан")


    if not Timeouts.objects.exists():
        Timeouts.objects.create(timeout_result=4, timeout_suggest=30)
        print("Таймаут создан")

    if not Search.objects.exists():
        Search.objects.create(search_string='')
        print("Поиск создан")
