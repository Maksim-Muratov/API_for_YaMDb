
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets 
from rest_framework.pagination import PageNumberPagination

from reviews.models import Category, Genre, Title
from .serializers import (CategorySerializer, GenreSerializer, PostTitleSerializer,
                          GetTitleSerializer)



class CreateListDestory(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    pass


class GenreViewSet(CreateListDestory):
    """View-функция для жанров произведений."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    # permission_classes = ...
    pagination_class = PageNumberPagination
    search_fields = ['=name']


class CategoryViewSet(CreateListDestory):
    """View-функция для категорий произведений."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    #permission_classes = ...
    pagination_class = PageNumberPagination
    search_fields = ['=name']


class TitleViewSet(viewsets.ModelViewSet):
    """View-функция для произведений."""

    queryset = (Title.objects.all().select_related("category")
                .prefetch_related("genre")
                #.annotate(rating=Avg('reviews__score'))
            )
    # permission_classes = ...
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name', 'year', 'category', 'genre')

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return GetTitleSerializer
        return PostTitleSerializer
                  