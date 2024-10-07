from wtforms import ValidationError


def length_validation(min=-1, max=-1):
    def validate(form, field):
        if min != -1 and len(field.data) < min:
            raise ValidationError(f"Field must be at least {min} characters long")
        if max != -1 and len(field.data) > max:
            raise ValidationError(f"Field must be at most {max} characters long")

    return validate


def lowercase_validation(form, field):
    if not any(char.islower() for char in field.data):
        raise ValidationError("Field must contain at least 1 lowercase letter")


def uppercase_validation(form, field):
    if not any(char.isupper() for char in field.data):
        raise ValidationError("Field must contain at least 1 uppercase letter")


def digit_validation(form, field):
    if not any(char.isdigit() for char in field.data):
        raise ValidationError("Field must contain at least 1 digit")


def special_character_validation(form, field):
    if not any(not char.isalnum() for char in field.data):
        raise ValidationError("Field must contain at least 1 special character")
