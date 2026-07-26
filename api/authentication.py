from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework.authentication import TokenAuthentication


class BearerTokenAuthentication(TokenAuthentication):
    """Accept ``Authorization: Bearer <key>`` in addition to DRF's default
    ``Token <key>``.

    This lets standard API clients work out of the box -- e.g. Postman's
    "Bearer Token" auth type, and OAuth-style ``Bearer`` clients -- without
    changing anything on the client side.
    """

    keyword = 'Bearer'


class BearerTokenScheme(OpenApiAuthenticationExtension):
    """Describe BearerTokenAuthentication to drf-spectacular as its own
    ``bearerAuth`` security scheme, so it doesn't collide with the default
    ``tokenAuth`` scheme and Swagger's Authorize dialog offers both."""

    target_class = 'api.authentication.BearerTokenAuthentication'
    name = 'bearerAuth'

    def get_security_definition(self, auto_schema):
        return {'type': 'http', 'scheme': 'bearer', 'bearerFormat': 'Token'}
