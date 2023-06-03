from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, MaxLengthValidator
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework.relations import SlugRelatedField

from reviews.models import Category, Comment, Genre, Review, Title

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для Регистрации Пользователей.
    v1/auth/signup/
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

    def validate(self, attrs):
        """
        Запрет повторного email и username.
        """
        email = attrs.get('email')
        username = attrs.get('username')

        existing_email = User.objects.filter(email=email).exists()
        existing_username = User.objects.filter(username=username).exists()

        if existing_email and not existing_username:
            raise ValidationError('Пользователь с таким email уже существует.')
        if existing_username and not existing_email:
            raise ValidationError('Пользователь с таким username уже '
                                  'существует.')
        return attrs

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


class TokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')

    def validate(self, attrs):
        """
        Проверка введенного username и confirmation_code.
        """
        username = attrs.get('username')
        confirmation_code = attrs.get('confirmation_code')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise NotFound(
                {'username': 'Пользователь не найден.'}
            )

        if user.confirmation_code != confirmation_code:
            raise serializers.ValidationError(
                {'error': 'Предоставлены неверные данные.'})

        attrs['user'] = user
        return attrs


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
        default=None
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
