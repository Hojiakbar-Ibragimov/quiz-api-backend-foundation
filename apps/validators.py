from .exceptions import ValidationError

def validate_id(ids, error_title):
    if not str(ids).isdigit():
        raise ValidationError(error_title)

    if int(ids) < 1:
        raise ValidationError(error_title)