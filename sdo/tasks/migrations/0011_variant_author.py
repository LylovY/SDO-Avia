# Generated by Django 3.2.16 on 2023-02-14 09:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('tasks', '0010_auto_20230214_0906'),
    ]

    operations = [
        migrations.AddField(
            model_name='variant',
            name='author',
            field=models.ForeignKey(blank=True, default=1, on_delete=django.db.models.deletion.CASCADE, related_name='variants', to='users.user'),
            preserve_default=False,
        ),
    ]