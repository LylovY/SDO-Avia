from django.db import models


class CreatedModel(models.Model):
    """Абстрактная модель. Добавляет дату создания"""
    created = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
        blank=True,
        null=True,
    )
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CreatedTaskModel(CreatedModel):
    """Абстрактная модель. Добавляет дату создания, название и описание"""
    title = models.CharField(
        'Заголовок',
        max_length=100,
        help_text='Название'
    )
    description = models.TextField(
        'Описание',
        max_length=2000,
        help_text='Описание'
    )

    class Meta:
        abstract = True
