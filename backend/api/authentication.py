from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed


class CustomTokenAuthentication(TokenAuthentication):
    """Кастомная токенная аутентификация, возвращающая 401 вместо 403."""

    def authenticate_credentials(self, key):
        """Аутентификация по токену."""
        try:
            return super().authenticate_credentials(key)
        except AuthenticationFailed:
            raise AuthenticationFailed('Неверный токен аутентификации.')
