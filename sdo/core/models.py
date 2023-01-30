from django.db import models


class CreatedModel(models.Model):
    '''Абстрактная модель. Добавляет дату создания'''
    created = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
        blank=True,
        null=True,
    )
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True