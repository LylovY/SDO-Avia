# Generated by Django 3.2.16 on 2023-02-09 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20230201_0735'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='tasks',
        ),
        migrations.AddField(
            model_name='user',
            name='parol',
            field=models.CharField(blank=True, max_length=15, null=True, verbose_name='Пароль_админ'),
        ),
    ]
