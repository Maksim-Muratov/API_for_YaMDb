from rest_framework.permissions import BasePermission


class AdminOnlyPermission(BasePermission):
    """
    Разрешение, которое позволяет доступ только Администраторам.
    user.role('admin') или is_staff.
    """

    def has_permission(self, request, view):
        if request.user.is_anonymous or request.user.role == ('user',
                                                              'moderator'):
            return False
        if request.user.role == 'admin' or request.user.is_superuser:
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin' or request.user.is_superuser:
            return True


class ModeratorPermission(BasePermission):
    """
    Разрешение, которое позволяет доступ только модераторам и Выше.
    """

    def has_permission(self, request, view):
        return request.user.role == ('moderator' or
                                     'admin' or
                                     request.user.is_superuser)

    def has_object_permission(self, request, view, obj):
        if request.user.role == ('moderator' or
                                 'admin' or
                                 request.user.is_superuser):
            return True


class OwnerOnlyPermission(BasePermission):
    """
    Разрешение только для владельца.
    """

    def has_object_permission(self, request, view, obj):
        return obj.author == request.user
