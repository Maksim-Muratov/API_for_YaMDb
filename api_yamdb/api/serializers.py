from django.contrib.auth import get_user_model
from django.core.validators import EmailValidator, MaxLengthValidator
from django.db import transaction
from rest_framework.validators import UniqueValidator
from rest_framework import serializers
from reviews.models import Category, Genre, Title
User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для Регистрации Пользователей.
    /api/v1/auth/token/
    """

    email = serializers.EmailField(
        write_only=True,
        required=True,
        # Валидаторы, проверяют что введенный текст - email,
        # Что адрес уникальный и что длина email не превышает 254 символа.
        validators=[EmailValidator(),
                    UniqueValidator(queryset=User.objects.all()),
                    MaxLengthValidator(254)]
    )

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate_username(self, value):
        """
        Проверка и запрет определенных значений для поля `username`.
        """
        # Здесь перечислены запрещенные usernames
        forbidden_usernames = ['admin', 'superuser',
                               'root', 'me']
        if value.lower() in forbidden_usernames:
            raise serializers.ValidationError(
                "Запрещенное значение для username.")
        return value

    def update(self, instance, validated_data):
        """
        Update an existing user instance.
        """
        instance.confirmation_code = self.context['confirmation_code']
        instance.save()
        return instance

    @transaction.atomic  # Записывает в БД, только выполнив всю работу.
    def create(self, validated_data):
        """
        Создание пользователя.
        Сохранение введенных полей email, username и confirmation_code в БД.
        """
        user = User.objects.create(
            email=validated_data['email'],
            username=validated_data['username'],
            confirmation_code=self.context['confirmation_code']
        )
        user.save()
        return user


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий произведений."""

    class Meta:
        model = Category
        fields = ("name", "slug")


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров произведений."""

    class Meta:
        model = Genre
        fields = ("name", "slug")


class PostTitleSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления произведений."""

    category = serializers.SlugRelatedField(
        many=True,
        slug_field="name",
        queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field="slug",
        queryset=Genre.objects.all()
    )

    class Meta:
        model = Title
        fields = ("name", "year", "description", "genre", "category")


class GetTitleSerializer(serializers.ModelSerializer):
    """Сериализатор для получения произведений."""

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    rating = serializers.IntegerField(
         # Тут надо как-то считать средний рейтинг
         read_only=True
    )

    class Meta:
        model = Title
        fields = ("id", "name", "year", "rating", "description", "genre", "category")
