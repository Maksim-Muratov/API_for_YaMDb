from django.contrib.auth import get_user_model
from django.core.validators import EmailValidator, MaxLengthValidator
from django.db import transaction
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

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
