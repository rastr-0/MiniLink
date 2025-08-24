class AuthError(Exception):
    pass


class URLError(Exception):
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


class PermessionDeniedError(AuthError):
    pass


class CustomAliasAlreadyExists(URLError):
    pass


class LinkShorteningError(URLError):
    pass


class ShortUrlNotFound(URLError):
    pass


class InvalidShortUrl(URLError):
    pass


class ShortUrlServiceUnavailable(URLError):
    """Raised when the problem is on the server side with the service"""
    pass


class ShortUrlExpired(URLError):
    pass
