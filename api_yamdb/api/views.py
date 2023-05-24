import random
import string

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework import permissions, status
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from .serializers import UserRegistrationSerializer

User = get_user_model()


class RegisterView(CreateAPIView):
    """
    Регистрация нового пользователя.
    /api/v1/auth/token/
    """
    permission_classes = [permissions.AllowAny]  # Регистрация доступна всем.
    serializer_class = UserRegistrationSerializer

    def generate_confirmation_code(self):
        """
        Генерирует код подтверждения.
        """
        code_length = 10  # Длина кода подтверждения
        characters = string.ascii_letters + string.digits
        code = ''.join(random.choice(characters) for _ in range(code_length))
        return code

    def create(self, request, *args, **kwargs):
        """
        Создание пользователя.
        Изменен HTTP status со стандартного 201 на 200.
        Возвращает username и email.
        Отправляет email.
        Генерирует код подтверждения.
        """

        # Запуск сериализатора.
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # Генерация код подтверждения.
        # confirmation_code = self.generate_confirmation_code()
        # Добавляем confirmation_code в контекст
        # serializer.context['confirmation_code'] = confirmation_code
        # self.perform_create(serializer)

        existing_user = User.objects.filter(
            email=serializer.validated_data['email'],
            username=serializer.validated_data['username']
        ).first()

        # TODO: вписать этот код сюда.
        # Если пользователь уже существует:
        if existing_user:
            # Создает новый код подтверждения.
            confirmation_code = self.generate_confirmation_code()
            # И обновляет его в БД.
            existing_user.confirmation_code = confirmation_code
            existing_user.save()
        # Если нет:
        else:
            # Создает новый код подтверждения.
            confirmation_code = self.generate_confirmation_code()
            # Добавляет confirmation_code в контекст
            serializer.context['confirmation_code'] = confirmation_code
            # Создается сериализатор и пользователь.
            self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        response_data = {
            'username': serializer.validated_data['username'],
            'email': serializer.validated_data['email']
        }

        send_mail(
            from_email=None,
            message=f'Код подтверждения: {confirmation_code}',
            subject='Confirmation Code',
            recipient_list=(serializer.validated_data['email'],)
        )
        return Response(response_data,
                        status=status.HTTP_200_OK, headers=headers)

# TODO: Можно генерировать код подтверждения сколько угодно раз.
