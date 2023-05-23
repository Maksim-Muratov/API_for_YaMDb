from django.contrib.auth.models import AbstractUser
from django.db import models

CHOICES = (
    ('user', 'Пользователь'),
    ('admin', 'Администратор'),
    ('moderator', 'Модератор'),
)


class User(AbstractUser):
    """
    Добавление полей Биографии и Роли для модели User.
    """
    bio = models.TextField(blank=True)
    role = models.CharField(max_length=50, choices=CHOICES, default='user')
