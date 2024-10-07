def strong_password_validation(password):

    # be between 8 and 15 characters = 1
    if len(password) < 8 or len(password) > 15:
        return False, "Password must be between 8 and 15 characters"
    # contain at least 1 uppercase letter = 2
    if not any(char.isupper() for char in password):
        return False, "Password must contain at least 1 uppercase letter"
    # contain at least 1 lowercase letter = 3
    if not any(char.islower() for char in password):
        return False, "Password must contain at least 1 lowercase letter"
    # contain at least 1 digit = 4
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least 1 digit"
    # contain at least 1 special (non-word) character = 5
    if not any(not char.isalnum() for char in password):
        return False, "Password must contain at least 1 special character"

    return True, "Password is strong"
