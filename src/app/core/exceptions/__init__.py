class AuthError(Exception):
    pass


class UserNotFoundError(AuthError):
    pass


class InvalidPasswordError(AuthError):
    pass


class TokenCreationError(AuthError):
    pass


class UserAlreadyExists(AuthError):
    pass


class RegisterUserError(AuthError):
    pass
