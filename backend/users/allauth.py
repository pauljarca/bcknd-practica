import logging

import graphene

from allauth.account import app_settings as allauth_settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError, ImproperlyConfigured, PermissionDenied
from django.db import transaction
from graphene import ClientIDMutation, relay
from graphene_django import DjangoObjectType
from graphql import GraphQLError

from students.models import StudentProfile
from users.backends import logout
from users.models import Token

from users.models import User, StudentClass

from users.backends import do_external_login

logger = logging.getLogger(__name__)

UserModel = get_user_model()


class UserNode(DjangoObjectType):
    class Meta:
        model = UserModel
        interfaces = (relay.Node,)
        exclude_fields = ('password', 'tokens', 'prefill')


class TokenNode(DjangoObjectType):
    class Meta:
        model = Token
        interfaces = (relay.Node,)


def handle_login_response(response):

    if 'eroare' in response:
        # TODO handle each response type
        raise GraphQLError(response['eroare']['descriere'])

    user = get_user_or_create_from_login_props(response['rezultat'])

    token = Token.objects.create(user=user)

    return {'user' : user, 'token': token}



def get_user_or_create_from_login_props(props):

    try:
        user = User.objects.get(reg = props['marca'])
    except User.DoesNotExist:
        user = None

    if user:
        return user

    try:
        study_class = StudentClass.objects.get(name = props['profil'], study_year = props['an'])
    except StudentClass.DoesNotExist:
        raise GraphQLError('Doar studenții din anul 3 de la CTI, CTI Engleză, IS, ' +
                           'respectiv anul 2 IS, IS ID pot trimite aplicații')

    user = User(
        first_name = props['prenume'],
        last_name = props['nume'],
        email = props['email'],
        reg = props['marca'],
        username = props['email'],
        password = ''
    )

    user.save()

    student_profile = StudentProfile(
        study_class = study_class,
        email = props['email'],
        user = user,
        specialization = props['specializare']
    )

    student_profile.save()

    return user



class LoginMutation(ClientIDMutation):
    class Input:
        email = graphene.String(required=True, description="Log in by e-mail address")
        password = graphene.String(required=True, description="The user's password")

    class Meta:
        name = 'Login'

    me = graphene.Field(UserNode, required=True)
    token = graphene.Field(TokenNode, required=True)

    @classmethod
    def mutate_and_get_payload(cls, root, info, email, password):
        response = do_external_login(email,password)

        with transaction.atomic():
            login_info = handle_login_response(response)
            return LoginMutation(me=login_info['user'], token=login_info['token'])


class LogoutMutation(ClientIDMutation):
    class Input:
        token = graphene.String(
            required=False, default_value='',
            description="Token to invalidate. Defaults to the token used to authenticate "
                        "the user making the request (via the Authorization header)."
        )
        all = graphene.Boolean(
            required=False, default_value=False,
            description="If true, invalidates all tokens of the currently logged in "
                        "user except the one used to make the request."
        )

    class Meta:
        name = 'Logout'

    logged_out = graphene.Boolean(
        required=True,
        description="true if the targeted token(s) were deleted, or if no user was logged in to begin with."
    )

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        token = input.get('token', None)
        all_tokens = input.get('all', False)
        if all_tokens and token:
            raise ValidationError("specific token cannot be invalidated when invalidating all tokens")

        with transaction.atomic():
            logged_out = logout(info.context, target_token=token, all_tokens=all_tokens)
            return LogoutMutation(logged_out=logged_out)


__UNSUPPORTED_ALLAUTH_SETTINGS = [
    'CONFIRM_EMAIL_ON_GET',
    'LOGOUT_ON_GET',
]

for setting in __UNSUPPORTED_ALLAUTH_SETTINGS:
    if getattr(allauth_settings, setting, False):
        raise ImproperlyConfigured(f"using graphene-allauth with {setting}=True is not supported")
