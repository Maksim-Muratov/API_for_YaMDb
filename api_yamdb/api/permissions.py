from rest_framework.permissions import BasePermission


class AdminOnlyPermission(BasePermission):
    """
    Разрешение, которое позволяет доступ только Администраторам.
    user.role('admin') или is_staff.
    """

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.role == 'admin' or request.user.is_superuser:
            return True


class AuthOwnerPermission(BasePermission):
    """
    Разрешение только для авторизованного владельца obj.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user


class CategoryAndGenresPermission(BasePermission):
    """
    Разрешения для категорий и Жанров.
    """

    def has_permission(self, request, view):
        if view.action in ['list']:
            return True
        if hasattr(request.user, 'role'):
            return request.user.role == ('admin' or
                                         request.user.is_superuser)

    def has_object_permission(self, request, view, obj):
        if hasattr(request.user, 'role'):
            return request.user.role == ('admin' or
                                         request.user.is_superuser)


class TitlesPermission(BasePermission):
    """
    Разрешения для Произведений.
    """

    def has_permission(self, request, view):
        if view.action in ['list', 'retrieve']:
            return True
        if hasattr(request.user, 'role'):
            return request.user.role == ('admin' or
                                         request.user.is_superuser)

    def has_object_permission(self, request, view, obj):
        if view.action in ['list', 'retrieve']:
            return True
        if hasattr(request.user, 'role'):
            return request.user.role == ('admin' or
                                         request.user.is_superuser)


class ReviewsAndCommentsPermission(BasePermission):
    """
    Разрешения для отзывов.
    """

    def has_permission(self, request, view):
        if view.action in ['list', 'retrieve']:
            return True
        elif view.action in ['create'] and request.user.is_authenticated:
            return True
        obj = view.get_object()
        if hasattr(request.user, 'role'):
            return (request.user.role == ('admin' or 'moderator' or
                                          request.user.is_superuser)
                    or obj.author == request.user)

    def has_object_permission(self, request, view, obj):
        if view.action in ['retrieve']:
            return True
        if hasattr(request.user, 'role'):
            return (request.user.role == ('admin' or 'moderator' or
                                          request.user.is_superuser)
                    or obj.author == request.user)
