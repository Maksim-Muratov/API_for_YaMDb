from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

CHOICES = (
    ('user', 'Пользователь'),
    ('admin', 'Администратор'),
    ('moderator', 'Модератор'),
)

# Пока не нужен.
# class UserManager(BaseUserManager):
#     """
#     Это менеджер для модели User.
#     Он добавляет новые функции
#     Вроде User.user_manager.create_user
#     """
#     use_in_migration = True  # Это что? Это нужно?
#
#     def create(self, email, role='user', **extra_fields):
#         """
#         Создание объекта User.
#         Добавлено поле role со стандартным значением 'user'
#         """
#         if not email:
#             raise ValueError('Email is Required')
#         user = self.model(email=self.normalize_email(email), **extra_fields)
#         user.role = role  # заполнение поля role
#         user.save(using=self._db)
#         return user


class User(AbstractUser):
    """
    Добавление полей Биографии и Роли для модели User.
    """
    email = models.EmailField(blank=False)
    # Текстовое поле "О пользователе".
    bio = models.TextField(blank=True, null=True)
    # Поле выбора роли из заданных вариантов.
    role = models.CharField(max_length=50, choices=CHOICES, default='user')
    # Поля для хранения кода подтверждения. Обновляется с каждым запросом.
    confirmation_code = models.CharField(max_length=10, blank=True, null=True)
    # Валидатор username выключен.
    username_validator = None

    # Добавление своего менеджера
    # user_manager = UserManager()

    class Meta:
        db_table = 'auth_user'  # Стандартное название таблицы, принудительно.
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
