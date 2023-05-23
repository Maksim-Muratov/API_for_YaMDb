from django.urls import include, path
from rest_framework import routers

v1_router = routers.DefaultRouter()

urlpatterns = [
    path('v1/', include(v1_router.urls)),
]
