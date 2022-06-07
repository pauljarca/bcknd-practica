import logging
import requests

from django.contrib.auth import get_user_model, logout as django_logout
from django.utils import timezone

from users.models import Token

from django.conf import settings

logger = logging.getLogger(__name__)

UserModel = get_user_model()


def get_token_from_request(request):
    """
    Extract the token from the ``Authorization`` header if the prefix is ``"Bearer"``, or return ``None`` otherwise.
    """
    auth_header = request.META.get('HTTP_AUTHORIZATION', '').split()
    if not auth_header or auth_header[0].lower() != 'bearer':
        return None

    return auth_header[1]


def get_valid_token(token: str):
    """
    Get the Token object associated with the given ``token`` string, and check the expiration date before returning it.
    Expired tokens are deleted and ``None`` is returned in all failure cases (expired, not found, etc).
    """
    if token:
        try:
            t = Token.objects.select_related('user').get(key=token)
            if timezone.now() <= t.expiration:
                return t
            else:
                t.delete()
        except Token.DoesNotExist:
            pass

    return None


def logout(request, target_token=None, all_tokens=False):
    """
    Delete the authorization token from the request, and then logout from
    ``django-allauth``, if installed, or directly from django if not.

    If ``target_token`` is given, that token is deleted instead, and logout of ``request``
    is only performed if its token matches ``target_token``.

    If ``all_tokens`` is True, all tokens associated with ``request.user``, except the token currently in use,
    are deleted. It is not valid to pass both ``all_tokens`` and ``target_token``.

    Tokens can only be deleted if they are owned by ``request.user``.

    Returns True if the targeted token(s) were deleted, or if no user was logged in to begin with.
    """
    assert not (target_token and all_tokens)
    req_token = get_token_from_request(request)
    do_logout = False
    logged_out = not getattr(request.user, 'is_authenticated', True)

    if all_tokens:
        if not logged_out:
            Token.objects.filter(user=request.user).exclude(key=req_token).delete()
            do_logout = True
            logged_out = True
    else:
        if not target_token:
            target_token = req_token

        token_obj = get_valid_token(target_token)
        if token_obj:
            if token_obj.user != request.user:
                logger.warning("%s attempts to delete token owned by %s!", str(request.user), str(token_obj.user))
                return False

            token_obj.delete()
            do_logout = target_token == req_token
            logged_out = True

    if do_logout:
        del request.META['HTTP_AUTHORIZATION']

        try:
            # noinspection PyUnresolvedReferences
            from allauth.account.adapter import get_adapter
            get_adapter(request).logout(request)
        except ImportError:
            django_logout(request)

    return logged_out

def do_external_login(email, password):
    auth_service_request_payload = {"cerere":{"cod":0,"utilizator":email,"parola":password}}
    auth_service_request_headers = {'X-API-KEY': settings.AUTH_SERVICE_API_KEY}

    http_response = requests.post(settings.AUTH_SERVICE_URL,
                                 json=auth_service_request_payload, headers=auth_service_request_headers)

    response = http_response.json()
    return response


class TokenBackend(object):
    def authenticate(self, request, token=None):
        t = get_valid_token(token)
        if not t:
            return None

        return t.user

    def get_user(self, user_id):
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None
