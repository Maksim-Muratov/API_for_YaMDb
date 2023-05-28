from django.urls import include, path
from rest_framework import routers

from api.views import (RegisterView, TokenView, UsersViewSet, profile_change,
                       CategoryViewSet, GenreViewSet, TitleViewSet)

v1_router = routers.DefaultRouter()
v1_router.register('users', UsersViewSet)

v1_router.register(
    r'^genres',
    GenreViewSet,
    basename='genres'
)
v1_router.register(
    r'^categories',
    CategoryViewSet,
    basename='categories'
)
v1_router.register(
    r'^titles',
    TitleViewSet,
    basename='titles'
)

urlpatterns = [
    # Просмотр и изменение своего профиля.
    # Должен быть перед роутером.
    path('v1/users/me/', profile_change, name='profile_change'),
    # Роутер.
    path('v1/', include(v1_router.urls)),
    # Регистрация пользователя.
    path('v1/auth/signup/', RegisterView.as_view(), name='sign_up'),
    # Получение JWT-токена.
    path('v1/auth/token/', TokenView.as_view(), name='token'),
]
