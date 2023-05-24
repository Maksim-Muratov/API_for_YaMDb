from reviews.models import Category, Genre, Title
from .serializers import (CategorySerializer, GenreSerializer,
                          PostTitleSerializer, GetTitleSerializer)


class GenreViewSet(ModelSetCLD):
    """View-функция для жанров произведений."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    # permission_classes = ...
    filter_backends = [filters.SearchFilter]
    pagination_class = PageNumberPagination
    search_fields = ['=name']
    lookup_field = 'slug'


class CategoryViewSet(ModelSetCLD):
    """View-функция для категорий произведений."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    #permission_classes = ...
    filter_backends = [filters.SearchFilter]
    pagination_class = PageNumberPagination
    search_fields = ['=name']
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    """View-функция для произведений."""

    queryset = Title.objects.all().annotate(Avg('reviews__score'))
    # permission_classes = ...
    filter_backends = (DjangoFilterBackend,)
    filterset_class = FilterForTitle

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return GetTitleSerializer
        return PostTitleSerializer