from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.core.validators import (EmailValidator, MaxLengthValidator,
                                    MaxValueValidator, MinValueValidator)
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from reviews.models import Category, Genre, Title, Review, Comment

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для Регистрации Пользователей.
    /api/v1/auth/token/
    """

    username = serializers.CharField(
        validators=[
            UnicodeUsernameValidator(),  # Валидатор для символов ^[\w.@+-]+\Z
            MaxLengthValidator(150),
        ]
    )

    email = serializers.EmailField(
        write_only=True,
        required=True,
        validators=[EmailValidator(),
                    MaxLengthValidator(254)]
    )

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate_username(self, username):
        """
        Проверка и запрет определенных значений для поля `username`.
        """
        # Здесь перечислены запрещенные usernames
        forbidden_usernames = ['admin', 'superuser',
                               'root', 'me']
        if username.lower() in forbidden_usernames:
            raise serializers.ValidationError(
                "Запрещенное значение для username.")
        return username

    @transaction.atomic  # Записывает в БД, только выполнив всю работу.
    def create(self, validated_data):
        """
        Создание пользователя.
        Сохранение введенных полей email, username и confirmation_code в БД.
        """
        email = validated_data['email']
        username = validated_data['username']

        user = User.objects.create(
            email=email,
            username=username,
            confirmation_code=self.context['confirmation_code']
        )
        user.save()
        return user


class TokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name',
                  'last_name', 'bio', 'role')


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий произведений."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров произведений."""

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class PostTitleSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления произведений."""

    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all()
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')


class GetTitleSerializer(serializers.ModelSerializer):
    """Сериализатор для получения произведений."""

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    rating = serializers.IntegerField(
        source='rating_avg',
        read_only=True,
        default=None,
        validators=[
            MinValueValidator(1, 'Оценка не может быть меньше 1'),
            MaxValueValidator(10, 'Оценка не может быть больше 10'),
        ],
    )

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category')


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов на произведения."""

    author = SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    def validate(self, data):
        request = self.context['request']
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if request.method == 'POST':
            if Review.objects.filter(
                    author=request.user,
                    title=title
            ).exists():
                raise ValidationError(
                    'На одно произведение можно оставить только один отзыв'
                )
        return data

    class Meta:
        fields = ('id', 'author', 'score', 'text', 'pub_date')
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев к отзывам."""

    author = SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = ('id', 'author', 'text', 'pub_date')
        model = Comment
