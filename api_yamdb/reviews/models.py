from django.db import models
from django.contrib.auth import get_user_model

from .validators import validate_year, validate_score


LEN_NAME = 15
LEN_TEXT = 30

User = get_user_model()


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
    rating = models.IntegerField(
        blank=True, default=None
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
        validators=[validate_score],
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
