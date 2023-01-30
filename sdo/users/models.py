from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse

from core.models import CreatedModel


class User(AbstractUser):
    username = models.CharField(
        unique=True,
        max_length=150,
        verbose_name='Ник пользователя',
        db_index=True,
    )
    email = models.EmailField(
        max_length=254,
        verbose_name='email',
        unique=True,
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя пользователя',
        blank=True,
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия пользователя',
        blank=True,
    )
    image = models.ImageField(
        'Фото профиля',
        default='default/User.png',
        upload_to="profiles/%Y/%m/%d/",
        help_text='Добавьте изображение к профилю',
        null=True,
        blank=True,
    )
    description = models.TextField(
        'О себе',
        blank=True,
        max_length=500
    )

    class Meta:
        verbose_name = 'Пользователи'
        verbose_name_plural = 'Пользователи'
        ordering = ['-date_joined']

    def __str__(self):
        return self.username

    def get_absolute_url(self):
        return reverse("posts:profile", kwargs={"username": self.username})

# Create your models here.
