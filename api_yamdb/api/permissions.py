import logging

from rest_framework.permissions import BasePermission

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] [%(lineno)d строка]  %(message)s '
)

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


class AdminOnlyPermission(BasePermission):
    """
    Разрешение, которое позволяет доступ только Администраторам.
    user.role('admin') или is_staff.
    """

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        if request.user.role == 'admin' or request.user.is_superuser:
            logger.debug('Permission is True')
            logger.debug(request.user.role)
            logger.debug(request.user.is_superuser)
            return True
        else:
            logger.debug('Permission is False')
            return False

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin' or request.user.is_superuser:
            logger.debug('has_object_permission is True')
            return True
        logger.debug('has_object_permission is False')


class ModeratorPermission(BasePermission):
    """
    Разрешение, которое позволяет доступ только модераторам и Выше.
    """

    def has_permission(self, request, view):
        return request.user.role == 'moderator' or 'admin'

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'moderator' or 'admin':
            return True
