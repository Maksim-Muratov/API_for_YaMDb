import random
import string
import logging

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from rest_framework import permissions, viewsets, filters
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .permissions import AdminOnlyPermission
from .serializers import UserRegistrationSerializer, TokenSerializer, \
    UserSerializer

User = get_user_model()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] [%(lineno)d строка]  %(message)s '
)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


class RegisterView(CreateAPIView):
    """
    Регистрация нового пользователя.
    /api/v1/auth/token/
    """
    permission_classes = [permissions.AllowAny]  # Регистрация доступна всем.
    serializer_class = UserRegistrationSerializer

    def generate_confirmation_code(self):
        """
        Генерирует случайный код подтверждения.
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
        Запрещает повторную регистрацию.
        """

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        existing_user = User.objects.filter(
            email=serializer.validated_data['email'],
            username=serializer.validated_data['username']
        ).first()
        existing_email = User.objects.filter(
            email=serializer.validated_data['email']
        )
        existing_username = User.objects.filter(
            username=serializer.validated_data['username']
        )

        # Если пользователь уже существует:
        if existing_user:
            # Создает новый код подтверждения.
            confirmation_code = self.generate_confirmation_code()
            # И обновляет его в БД.
            existing_user.confirmation_code = confirmation_code
            existing_user.save()
        elif existing_email:
            response_data = {
                'error': 'Пользователь с таким email уже существует.'
            }
            return Response(
                response_data,
                status=status.HTTP_400_BAD_REQUEST
            )
        elif existing_username:
            response_data = {
                'error': 'Пользователь с таким username уже существует.'
            }
            return Response(
                response_data,
                status=status.HTTP_400_BAD_REQUEST
            )
        # Если нет:
        else:
            # Создает новый код подтверждения.
            confirmation_code = self.generate_confirmation_code()
            # Добавляет confirmation_code в контекст,
            # Сериализатор сохранит его в БД, вместе с новым пользователем.
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


class TokenView(GenericAPIView):
    permission_classes = [permissions.AllowAny]  # Регистрация доступна всем.
    serializer_class = TokenSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        confirmation_code = serializer.validated_data['confirmation_code']

        # Проверяем учетные данные пользователя
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {'username': 'Пользователь не найден.'},
                status=status.HTTP_404_NOT_FOUND)

        if user.confirmation_code == confirmation_code:

            # Если учетные данные верны, создаем пару токенов
            refresh = RefreshToken.for_user(user)

            tokens = {
                'access': str(refresh.access_token),
            }

            return Response(tokens)
        else:
            return Response(
                {'error': 'Предоставлены неверные данные.'},
                status=status.HTTP_400_BAD_REQUEST)


class UsersViewSet(viewsets.ModelViewSet):
    queryset = User.objects.order_by('id')  # Для пагинации нужна сортировка.
    serializer_class = UserSerializer
    permission_classes = [AdminOnlyPermission]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    http_method_names = [  # Метод 'put' исключен.
        'get', 'post', 'patch', 'delete', 'head', 'options']
    lookup_field = 'username'  # /api/v1/users/rea/ вместо /api/v1/users/1/
