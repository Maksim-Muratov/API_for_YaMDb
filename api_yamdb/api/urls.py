from django.urls import include, path
from rest_framework import routers

from api.views import RegisterView

v1_router = routers.DefaultRouter()

urlpatterns = [
    path('v1/', include(v1_router.urls)),
    # Регистрация пользователя.
    path('v1/auth/signup/',
         RegisterView.as_view(), name='sign_up'),
]
