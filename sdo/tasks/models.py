from django.db import models

from core.models import CreatedModel, CreatedTaskModel
from users.models import User


class TaskCase(CreatedTaskModel):
    author = models.ForeignKey(
        User,
        related_name='taskcase_author',
        on_delete=models.SET_NULL,
        null=True
    )

    def __str__(self) -> str:
        return self.title


class Task(CreatedTaskModel):
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

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Вопросы'
        verbose_name_plural = 'Вопросы'

    def __str__(self) -> str:
        return self.title


class UserTaskCaseRelation(CreatedModel):
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


class UserTaskRelation(CreatedModel):
    NEW = 'NEW'
    ON_CHECK = 'CHECK'
    FOR_REVISION = 'REVISION'
    ACCEPT = 'ACCEPT'
    TASK_STATUS = [
        (NEW, 'Новый'),
        (ON_CHECK, 'На проверке'),
        (FOR_REVISION, 'На доработку'),
        (ACCEPT, 'Принято'),
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
    answer = models.TextField(
        'Ответ',
        blank=True,
    )

    status = models.CharField(
        max_length=10,
        choices=TASK_STATUS,
        default=NEW,
    )


# class Answer(CreatedModel):
#     author = models.ForeignKey(
#         User,
#         related_name='answers',
#         on_delete=models.CASCADE,
#     )
#     text = models.TextField(
#         'Ответ'
#     )
#     task = models.ForeignKey(
#         Task,
#         related_name='answers',
#         on_delete=models.CASCADE
#     )
#     approoved = models.BooleanField(default=False)


