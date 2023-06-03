from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import validate_year

LEN_NAME = 15
LEN_TEXT = 30


class User(AbstractUser):
    """
    Добавление полей Биографии и Роли для модели User.
    """
    USER = 'user'
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    CHOICES = (
        (USER, 'Пользователь'),
        (ADMIN, 'Администратор'),
        (MODERATOR, 'Модератор'),
    )
    email = models.EmailField(blank=False, unique=True)
    # Текстовое поле "О пользователе".
    bio = models.TextField(blank=True, null=True)
    # Поле выбора роли из заданных вариантов.
    role = models.CharField(max_length=50, choices=CHOICES, default='user')
    # Поля для хранения кода подтверждения. Обновляется с каждым запросом.
    confirmation_code = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        ordering = ['id']
        db_table = 'auth_user'  # Стандартное название таблицы, принудительно.
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Genre(models.Model):
    """Модель жанров произведений."""

    name = models.CharField(max_length=50, verbose_name='Название жанра')
    slug = models.SlugField(
        max_length=50, verbose_name='Slug жанра', unique=True
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

    def __str__(self):
        return self.name


class Category(models.Model):
    """Модель категорий произведений."""

    name = models.CharField(max_length=200, verbose_name='Название категории')
    slug = models.SlugField(
        max_length=50, verbose_name='Адрес категории', unique=True
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель названий произведений."""

    name = models.CharField(
        max_length=200, verbose_name='Название'
    )
    year = models.IntegerField(
        validators=[validate_year],
        verbose_name='Год выпуска'
    )
    description = models.TextField(
        null=True, verbose_name='Описание'
    )
    genre = models.ManyToManyField(
        Genre,
        through='TitleGenre',
        verbose_name='Slug жанра'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='titles',
        verbose_name='Slug категории'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

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
        related_name='genre'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'genre'],
                name='uq_title_genre'
            )
        ]


class Review(models.Model):
    """Модель отзыва на произведение."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    text = models.TextField(
        verbose_name='Отзыв'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.IntegerField(
        validators=[
            MinValueValidator(1, 'Оценка не может быть меньше 1'),
            MaxValueValidator(10, 'Оценка не может быть больше 10'),
        ],
        verbose_name='Оценка произведения (По десятибальной шкале)'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        ordering = ['-pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='uq_title_author'
            )
        ]

    def __str__(self):
        return self.text[:LEN_TEXT]


class Comment(models.Model):
    """Модель комментария к отзыву."""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(
        verbose_name='Комментарий'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        ordering = ['-pub_date']

    def __str__(self):
        return self.text[:LEN_TEXT]
