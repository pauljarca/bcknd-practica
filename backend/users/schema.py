import graphene
from django.core.exceptions import ValidationError
from graphene_django import DjangoObjectType
from graphene_django.converter import convert_django_field, convert_field_to_string
from phonenumber_field.modelfields import PhoneNumberField

from users.allauth import UserModel, UserNode, LoginMutation, LogoutMutation
from users.models import StudentClass


# noinspection PyUnresolvedReferences
@convert_django_field.register(PhoneNumberField)
def convert_phone_to_string(field, registry=None):
    return convert_field_to_string(field, registry)


class StudentClassNode(DjangoObjectType):
    class Meta:
        model = StudentClass
        only_fields = ['id', 'name', 'study_year', 'credits', 'hours']



class Query(object):
    me = graphene.Field(UserNode)

    def resolve_me(self, info):
        user = info.context.user
        if isinstance(user, UserModel):
            return user
        else:
            return None


class Mutation(object):
    login = LoginMutation.Field()
    logout = LogoutMutation.Field()
