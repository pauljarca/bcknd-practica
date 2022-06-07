import graphene
from django.core.exceptions import PermissionDenied
from django.db import transaction
from graphene import relay
from graphene.utils.str_converters import to_camel_case, to_snake_case
from graphene_django import DjangoObjectType, DjangoConnectionField
from rest_framework import serializers
from rest_framework.fields import MultipleChoiceField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer

from internships.models import InternshipOffer
from students.models import StudentProfile
from users.schema import StudentClassNode
from util.schema import SerializerMutation
from graphql import GraphQLError
from uuid import UUID
from graphql_relay import from_global_id

class StudentProfileNode(DjangoObjectType):
    study_class = graphene.Field(StudentClassNode, required=True)

    class Meta:
        model = StudentProfile
        interfaces = (relay.Node,)

    def resolve_cv(self, info):
        profile = self  # type: StudentProfile
        return profile.cv_url


class StudentProfileSerializer(ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ('phone', 'github', 'linkedin')

    # applications = PrimaryKeyRelatedField(queryset=InternshipOffer.objects, required=False, many=True)


    def update_nested(self, instance, validated_data, nested_name):
        nested_data = validated_data.pop(nested_name, None)
        if nested_data:
            nested_instance = getattr(instance, nested_name, None)
            save_kwargs = {}
            if not nested_instance:
                save_kwargs['student'] = instance

            nested_serializer_class = type(self.fields[nested_name])
            nested_serializer = nested_serializer_class(data=nested_data, instance=nested_instance)
            if nested_serializer.is_valid():
                nested_serializer.save(**save_kwargs)
            else:
                # should never happen... data was already validated by the same serializer
                raise serializers.ValidationError(nested_serializer.errors)

    def update(self, instance, validated_data):
        with transaction.atomic():
            return super().update(instance, validated_data)


class StudentProfileMutation(SerializerMutation):
    class Meta:
        serializer_class = StudentProfileSerializer

    profile = graphene.Field(StudentProfileNode, required=False)

    @classmethod
    def get_serializer(cls, root, info, **input):
        user = info.context.user
        profile = getattr(user, 'student', None)  # type: StudentProfile
        if not profile:
            raise PermissionDenied("no student profile associated with current user")
        return cls._meta.serializer_class(data=input, instance=profile)

    @classmethod
    def get_success_result(cls, instance, info):
        return cls(profile=instance)


class AddApplicationMutation(graphene.Mutation):
    class Arguments:
        # The input arguments for this mutation
        internshipId = graphene.ID()

    profile = graphene.Field(StudentProfileNode)

    @classmethod
    def mutate(cls, root, info, internshipId):
        if not info.context.user.is_authenticated:
            raise PermissionDenied("Authentication required")

        user = info.context.user
        if not user:
            raise PermissionDenied("Authentication required")

        profile = StudentProfile.objects.get(user=user)

        if not profile:
            raise PermissionDenied("no student profile associated with current user")
        internship = InternshipOffer.objects.get(id=internshipId)

        if not internship:
            raise GraphQLError("Invalid internshipId!")

        if profile.applications.filter(id=internshipId).exists():
            raise GraphQLError("Already applied!")

        profile.applications.add(internship)
        print('User ' + user.email + ' added application for ' + internship.title)

        # Notice we return an instance of this mutation
        return AddApplicationMutation(profile=profile)


class RemoveApplicationMutation(graphene.Mutation):
    class Arguments:
        # The input arguments for this mutation
        internshipId = graphene.ID()

    profile = graphene.Field(StudentProfileNode)

    @classmethod
    def mutate(cls, root, info, internshipId):
        if not info.context.user.is_authenticated:
            raise PermissionDenied("Authentication required")

        user = info.context.user
        if not user:
            raise PermissionDenied("Authentication required")

        profile = StudentProfile.objects.get(user=user)

        if not profile:
            raise PermissionDenied("no student profile associated with current user")
        internship = InternshipOffer.objects.get(id=internshipId)

        if not internship:
            raise GraphQLError("Invalid internshipId!")

        if not profile.applications.filter(id=internshipId).exists():
            raise GraphQLError("Not applied!")

        profile.applications.remove(internship)
        print('User ' + user.email + ' removed application for ' + internship.title)
        # Notice we return an instance of this mutation
        return AddApplicationMutation(profile=profile)

class Mutation(object):
    update_profile = StudentProfileMutation.Field()
    add_application = AddApplicationMutation.Field()
    remove_application = RemoveApplicationMutation.Field()