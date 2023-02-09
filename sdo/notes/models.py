from django.db import models

from core.models import CreatedModel
from users.models import User


class Note(CreatedModel):
    """Модель заметок"""
    author = models.ForeignKey(
        User,
        related_name='note_author',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User,
        related_name='notes',
        on_delete=models.CASCADE
    )
    text = models.TextField(
        'Заметка'
    )
