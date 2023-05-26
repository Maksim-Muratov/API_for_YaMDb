from rest_framework.permissions import BasePermission


class AdminOnlyPermission(BasePermission):
    """
    Разрешение, которое позволяет доступ только администраторам.
    """

    def has_permission(self, request, view):
        return request.user.role == 'admin'


class ModeratorPermission(BasePermission):
    """
    Разрешение, которое позволяет доступ только модераторам и Выше.
    """

    def has_permission(self, request, view):
        return request.user.role == 'moderator', 'admin'
