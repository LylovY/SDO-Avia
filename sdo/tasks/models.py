from django.db import models
from django_summernote.models import AbstractAttachment

from core.models import CreatedModel, CreatedTaskModel
from users.models import User


class TaskCase(CreatedTaskModel):
    """Модель группы вопросов """
    author = models.ForeignKey(
        User,
        related_name='taskcase_author',
        on_delete=models.SET_NULL,
        null=True
    )
    is_test = models.BooleanField(
        'Тест',
        default=False
    )

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Блоки'
        verbose_name_plural = 'Блоки'


class Task(CreatedTaskModel):
    """Модель вопросов"""
    author = models.ForeignKey(
        User,
        related_name='task_author',
        on_delete=models.SET_NULL,
        null=True
    )
    answer = models.TextField(
        'Решение',
        blank=True
    )
    task_case = models.ManyToManyField(
        TaskCase,
        related_name='tasks',
        verbose_name='Группа вопросов',
        blank=True
    )
    is_test = models.BooleanField(
        'Тест',
        default=False
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Вопросы'
        verbose_name_plural = 'Вопросы'

    def __str__(self) -> str:
        return self.title


class MyAttachment(AbstractAttachment):
    task = models.ForeignKey(
        Task,
        related_name='task',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    created = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
        blank=True,
        null=True,
    )


class UserTaskCaseRelation(CreatedModel):
    """Модель связи группы вопросов с пользователями"""
    user = models.ForeignKey(
        User,
        related_name='task_case_relation',
        on_delete=models.CASCADE
    )
    task_case = models.ForeignKey(
        TaskCase,
        related_name='task_case_relation',
        on_delete=models.CASCADE
    )
    complete = models.BooleanField(
        'Выполнение',
        default=False
    )
    review = models.BooleanField(
        'Для проверки',
        default=False
    )


class UserTaskRelation(CreatedModel):
    """Модель связи вопросов с пользователями"""
    NEW = 'NEW'
    ON_CHECK = 'CHECK'
    FOR_REVISION = 'REVISION'
    ACCEPT = 'ACCEPT'
    WRONG = 'WRONG'
    TASK_STATUS = [
        (NEW, 'Новый'),
        (ON_CHECK, 'На проверке'),
        (FOR_REVISION, 'На доработку'),
        (ACCEPT, 'Принято'),
        (WRONG, 'Ошибка')
    ]
    user = models.ForeignKey(
        User,
        related_name='task_relation',
        on_delete=models.CASCADE
    )
    task = models.ForeignKey(
        Task,
        related_name='task_relation',
        on_delete=models.CASCADE
    )

    status = models.CharField(
        max_length=10,
        choices=TASK_STATUS,
        default=NEW,
    )


class Answer(CreatedModel):
    """Модель ответов"""
    relation = models.ForeignKey(
        UserTaskRelation,
        related_name='answers',
        on_delete=models.CASCADE,
    )
    text = models.TextField(
        'Ответ'
    )
    author = models.ForeignKey(
        User,
        related_name='answers',
        on_delete=models.CASCADE,
    )


class Review(CreatedModel):
    "Модель замечаний к ответам"
    answer = models.ForeignKey(
        Answer,
        related_name='reviews',
        on_delete=models.CASCADE,
    )
    text = models.TextField(
        'Правки'
    )

    def __str__(self) -> str:
        return self.text


class Variant(CreatedModel):
    task = models.ForeignKey(
        Task,
        related_name='variants',
        on_delete=models.CASCADE,
    )
    text = models.TextField(
        'Вариант'
    )
    correct = models.BooleanField(
        'Правильный ответ?',
        default=False
    )

    def __str__(self) -> str:
        return self.text