from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_year(year):
    current_year = timezone.now().year
    if year > current_year:
        raise ValidationError(
            f'Год выпуска не может быть больше текущего ({current_year})')


def validate_score(score):
    if 1 > score > 10:
        raise ValidationError(
            'Оценка должна быть в диапазоне от 1 до 10 включительно')
