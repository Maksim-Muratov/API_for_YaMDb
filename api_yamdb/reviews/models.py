from django.contrib.auth.models import AbstractUser
from django.db import models
from .validators import validate_year

LEN_NAME = 15

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


class Genre(models.Model):
    """Модель жанров произведений."""

    name = models.CharField(max_length=50, verbose_name="Название жанра")
    slug = models.SlugField(
        max_length=50, verbose_name="Slug жанра", unique=True
    )

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"

    def __str__(self):
        return self.name


class Category(models.Model):
    """Модель категорий произведений."""

    name = models.CharField(max_length=200, verbose_name="Название категории")
    slug = models.SlugField(
        max_length=50, verbose_name="Адрес категории", unique=True
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель названий произведений."""

    name = models.CharField(
        max_length=200, verbose_name="Название"
    )
    year = models.IntegerField(
        validators=[validate_year],
        verbose_name="Год выпуска"
    )
    description = models.TextField(
        null=True, verbose_name="Описание"
    )
    genre = models.ManyToManyField(
        Genre,
        through='TitleGenre',
        verbose_name="Slug жанра"
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="titles",
        verbose_name="Slug категории"
    )

    class Meta:
        ordering = ["-year"]
        verbose_name = "Произведение"
        verbose_name_plural = "Произведения"

    def __str__(self):
        return self.name[:LEN_NAME]


class TitleGenre(models.Model):
    """Модель произведение-жанр."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='titles'
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="genre"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["title", "genre"],
                name="uq_title_genre"
            )
        ]
