from django.conf import settings
from django.contrib import auth
from django.contrib.sessions.middleware import SessionMiddleware as DjangoSessionMiddleware

from users.backends import get_token_from_request


class TokenMiddleware(DjangoSessionMiddleware):
    """
    Middleware that authenticates against a token in the http authorization
    header and blocks cookies on token endpoints.
    """

    def is_api_view(self, request):
        return request.path == '/graphql' or request.path.startswith('/upload/')

    def process_request(self, request):
        if self.is_api_view(request):
            request.COOKIES.clear()
            request.META.pop('HTTP_COOKIE', None)

            user = self.authorize_header(request)
            if user:
                request.user = request._cached_user = user

        super().process_request(request)

    def authorize_header(self, request):
        token = get_token_from_request(request)
        if not token:
            return None

        return auth.authenticate(token=token)

    def process_response(self, request, response):
        if self.is_api_view(request):
            response.cookies.clear()

        response = super().process_response(request, response)

        if self.is_api_view(request):
            response.cookies.clear()
            del response['Set-Cookie']

        return response
