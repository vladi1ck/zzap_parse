# Generated by Django 4.2.17 on 2024-12-19 11:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Search',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('search_string', models.TextField()),
                ('search_time', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Поиск',
                'verbose_name_plural': 'Поиски',
                'ordering': ['id'],
            },
        ),
    ]
