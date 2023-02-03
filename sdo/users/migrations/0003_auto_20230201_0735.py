# Generated by Django 3.2.16 on 2023-02-01 07:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0004_auto_20230201_0735'),
        ('users', '0002_alter_user_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='task_case',
            field=models.ManyToManyField(blank=True, help_text='Папка вопросов', null=True, related_name='users', through='tasks.UserTaskCaseRelation', to='tasks.TaskCase', verbose_name='Группа вопросов'),
        ),
        migrations.AddField(
            model_name='user',
            name='tasks',
            field=models.ManyToManyField(blank=True, help_text='Вопросы', null=True, related_name='users', through='tasks.UserTaskRelation', to='tasks.Task', verbose_name='Вопросы'),
        ),
    ]