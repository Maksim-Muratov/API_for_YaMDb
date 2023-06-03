from django.urls import include, path
from rest_framework import routers

from api.v1.views import (CategoryViewSet, CommentViewSet, GenreViewSet,
                          RegisterView, ReviewViewSet, TitleViewSet, TokenView,
                          UsersViewSet)

v1_router = routers.DefaultRouter()
v1_router.register(
    r'^users',
    UsersViewSet,
    basename='users'
)
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
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
v1_router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)

urlpatterns = [
    # Роутер.
    path('v1/', include(v1_router.urls)),
    # Регистрация пользователя.
    path('v1/auth/signup/', RegisterView.as_view(), name='sign_up'),
    # Получение JWT-токена.
    path('v1/auth/token/', TokenView.as_view(), name='token'),
]
