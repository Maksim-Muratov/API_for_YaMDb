from rest_framework import serializers
from reviews.models import Category, Genre, Title




class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий произведений."""

    class Meta:
        model = Category
        fields = ("name", "slug")


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров произведений."""

    class Meta:
        model = Genre
        fields = ("name", "slug")


class PostTitleSerializer(serializers.ModelSerializer):
    """Сериализатор для добавления произведений."""

    category = serializers.SlugRelatedField(
        many=True,
        slug_field="name",
        queryset=Category.objects.all()
    )
    genre = serializers.SlugRelatedField(
        many=True,
        slug_field="slug",
        queryset=Genre.objects.all()
    )
    
    class Meta:
        model = Title
        fields = ("name", "year", "description", "genre", "category")


class GetTitleSerializer(serializers.ModelSerializer):
    """Сериализатор для получения произведений."""

    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(read_only=True, many=True)
    rating = serializers.IntegerField(
         # Тут надо как-то считать средний рейтинг
         read_only=True
    )

    class Meta:
        model = Title
        fields = ("id", "name", "year", "rating", "description", "genre", "category")
