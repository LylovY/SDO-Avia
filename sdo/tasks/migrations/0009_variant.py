# Generated by Django 3.2.16 on 2023-02-14 08:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0008_answer_author'),
    ]

    operations = [
        migrations.CreateModel(
            name='Variant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, null=True, verbose_name='Дата создания')),
                ('updated', models.DateTimeField(auto_now=True)),
                ('title', models.CharField(help_text='Название', max_length=100, verbose_name='Заголовок')),
                ('description', models.TextField(help_text='Описание', max_length=2000, verbose_name='Описание')),
                ('text', models.TextField(verbose_name='Вариант')),
                ('correct', models.BooleanField(default=False, verbose_name='Правильный ответ?')),
                ('task', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='variants', to='tasks.task')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
