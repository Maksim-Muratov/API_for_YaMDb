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
    GET all - AllowAny
    POST - Admin
    DEL - Admin
    PATCH, PUT, GET one - forbidden
    """

    def has_permission(self, request, view):
        if view.action == 'list':
            return True
        elif view.action in ['create', 'destroy']:
            if hasattr(request.user, 'role'):
                return request.user.role == ('admin' or
                                             request.user.is_superuser)
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if view.action == 'list':
            return True
        elif view.action in ['create', 'destroy']:
            if hasattr(request.user, 'role'):
                return request.user.role == ('admin' or
                                             request.user.is_superuser)
        else:
            return False


class TitlesPermission(BasePermission):
    """
    Разрешения для Произведений.
    GET one and all - AllowAny
    POST - admin
    PATCH - admin
    DELETE - admin
    PUT - forbidden
    """

    def has_permission(self, request, view):
        if view.action in ['list', 'retrieve']:
            return True
        elif view.action in ['create', 'partial_update',
                             'destroy']:
            if hasattr(request.user, 'role'):
                return request.user.role == ('admin' or
                                             request.user.is_superuser)
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if view.action in ['list', 'retrieve']:
            return True
        elif view.action in ['create', 'partial_update',
                             'destroy']:
            if hasattr(request.user, 'role'):
                return request.user.role == ('admin' or
                                             request.user.is_superuser)
        else:
            return False


class ReviewsAndCommentsPermission(BasePermission):
    """
    Разрешения для отзывов.
    GET one, all - AllowAny
    POST - is_authenticated
    PATCH - author, moder, admin
    DELETE - author, moder, admin
    PUT - forbidden
    """

    def has_permission(self, request, view):
        if view.action in ['list', 'retrieve']:
            return True
        elif view.action in ['create']:
            if request.user.is_authenticated:
                return True
        elif view.action in ['destroy', 'partial_update']:
            obj = view.get_object()
            if hasattr(request.user, 'role'):
                return (request.user.role == ('admin' or 'moderator' or
                                              request.user.is_superuser)
                        or obj.author == request.user)
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if view.action in ['list', 'retrieve']:
            return True
        elif view.action in ['create']:
            if request.user.is_authenticated:
                return True
        elif view.action in ['destroy', 'partial_update']:
            if hasattr(request.user, 'role'):
                return (request.user.role == ('admin' or 'moderator' or
                                              request.user.is_superuser)
                        or obj.author == request.user)
        else:
            return False
