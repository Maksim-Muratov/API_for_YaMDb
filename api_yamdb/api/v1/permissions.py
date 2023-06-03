from rest_framework.permissions import SAFE_METHODS, BasePermission

from reviews.models import User


class AdminOnlyPermission(BasePermission):
    """
    Разрешение, которое позволяет доступ только Администраторам.
    user.role('admin') или is_staff.
    """

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        return request.user.role == User.ADMIN or request.user.is_superuser


class AuthOwnerPermission(BasePermission):
    """
    Разрешение только для авторизованного, владельца изменяемых данных.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class CategoryAndGenresPermission(BasePermission):
    """
    Разрешения для категорий и Жанров.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return (request.user.is_authenticated
                and (request.user.role == User.ADMIN
                     or request.user.is_superuser))

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or (request.user.is_authenticated
                    and (request.user.role == User.ADMIN
                         or request.user.is_superuser)))


class TitlesPermission(BasePermission):
    """
    Разрешения для Произведений.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return (request.user.is_authenticated
                and (request.user.role == User.ADMIN
                     or request.user.is_superuser))

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or (request.user.is_authenticated
                    and (request.user.role == User.ADMIN
                         or request.user.is_superuser)))


class ReviewsAndCommentsPermission(BasePermission):
    """
    Разрешения для отзывов.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return (request.user.is_authenticated
                or (request.user.is_authenticated
                    and (request.user.role in [User.ADMIN, User.MODERATOR]
                         or request.user.is_superuser)))

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or (obj.author == request.user)
                or (request.user.is_authenticated
                    and (request.user.role in [User.ADMIN, User.MODERATOR]
                         or request.user.is_superuser)))
