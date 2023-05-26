from django.urls import include, path
from rest_framework import routers

from api.views import (CategoryViewSet, GenreViewSet,
                       RegisterView, TitleViewSet, TokenView)

v1_router = routers.DefaultRouter()

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
    path('v1/', include(v1_router.urls)),
    # Регистрация пользователя.
    path('v1/auth/signup/',
         RegisterView.as_view(), name='sign_up'),
    # Получение JWT-токена.
    path('v1/auth/token/', TokenView.as_view(), name='token'),
]
