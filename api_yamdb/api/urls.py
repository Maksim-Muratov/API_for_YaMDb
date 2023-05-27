from django.urls import include, path
from rest_framework import routers

from api.views import RegisterView, TokenView, UsersViewSet, profile_change

v1_router = routers.DefaultRouter()
v1_router.register('users', UsersViewSet)

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
