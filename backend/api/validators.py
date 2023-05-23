from django.core.exceptions import ValidationError

MIN_COOKING_TIME = 1
MIN_AMOUNT = 1


def validate_amount(value):
    """Валидация поля количества."""
    if value < MIN_AMOUNT:
        raise ValidationError(
            f'Количество не должно быть менее {MIN_AMOUNT}'
        )


def validate_cooking_time(value):
    """Валидация поля время приготовления."""
    if value < MIN_COOKING_TIME:
        raise ValidationError(
            f'Время приготовления не должно быть менее {MIN_COOKING_TIME} мин.'
        )
