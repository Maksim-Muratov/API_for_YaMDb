import random
import string

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (permissions, status, filters, mixins, viewsets)
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Genre, Title, Review, Comment
from .mixins import CreateListDestroy
from .permissions import AdminOnlyPermission, OwnerOnlyPermission, \
    CategoryAndGenresPermission, ReviewsAndCommentsPermission, TitlesPermission
from .serializers import (CategorySerializer, GenreSerializer,
                          GetTitleSerializer, PostTitleSerializer,
                          ReviewSerializer, CommentSerializer)
from .serializers import (UserRegistrationSerializer, TokenSerializer,
                          UserSerializer)
from .filters import FilterTitleSet

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
    """
    Получения Токена.
    """
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

            return Response({'error': 'Предоставлены неверные данные.'},
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


@api_view(['GET', 'PATCH'])
@permission_classes([OwnerOnlyPermission, permissions.IsAuthenticated])
def profile_change(request):
    """
    Получение и Изменение своего профиля.
    """
    user = request.user
    msg = 'У вас нет разрешения изменять роль пользователя.'

    if request.method == 'PATCH':
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            # Менять user.role может только admin.
            if 'role' in serializer.validated_data and user.role != 'admin':
                return Response({'detail': msg},
                                status=status.HTTP_403_FORBIDDEN)

            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    # Метод GET.
    serializer = UserSerializer(user)
    return Response(serializer.data)


class GenreViewSet(CreateListDestroy):
    """View-функция для жанров произведений."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [CategoryAndGenresPermission]
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ['=name']
    lookup_field = 'slug'


class CategoryViewSet(CreateListDestroy):
    """View-функция для категорий произведений."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [CategoryAndGenresPermission]
    pagination_class = PageNumberPagination
    filter_backends = (filters.SearchFilter,)
    search_fields = ['=name']
    # Вариант перенаправления с http://127.0.0.1:8000/api/v1/categories/1/
    # На http://127.0.0.1:8000/api/v1/categories/{slug}/
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """View-функция для произведений."""

    queryset = (Title.objects.all().select_related('category')
                .prefetch_related('genre')
                .annotate(rating_avg=Avg('reviews__score'))
                .order_by('id'))
    permission_classes = [TitlesPermission]
    filter_backends = (DjangoFilterBackend,)
    filterset_class = FilterTitleSet

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return GetTitleSerializer
        return PostTitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """View-функция для отзывов."""

    serializer_class = ReviewSerializer

    permission_classes = [ReviewsAndCommentsPermission]

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """View-функция для комментариев."""

    serializer_class = CommentSerializer

    permission_classes = [ReviewsAndCommentsPermission]

    def get_queryset(self):
        review = get_object_or_404(Comment, id=self.kwargs.get('post_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)
