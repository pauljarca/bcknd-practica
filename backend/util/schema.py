import graphene
from graphene import ClientIDMutation, InputField
from graphene.types.mutation import MutationOptions
from graphene.types.utils import yank_fields_from_attrs
from graphene_django.rest_framework.mutation import fields_for_serializer
from graphene_django.rest_framework.serializer_converter import get_graphene_type_from_serializer_field
from rest_framework import serializers


class ErrorType(graphene.ObjectType):
    field = graphene.String()
    messages = graphene.List(graphene.NonNull(graphene.String))


@get_graphene_type_from_serializer_field.register(serializers.PrimaryKeyRelatedField)
def convert_serializer_field_to_id(field: serializers.PrimaryKeyRelatedField):
    return graphene.ID


@get_graphene_type_from_serializer_field.register(serializers.ManyRelatedField)
def convert_serializer_field_to_related_list(field: serializers.ManyRelatedField):
    return graphene.List, get_graphene_type_from_serializer_field(field.child_relation)


class SerializerMutationOptions(MutationOptions):
    serializer_class = None


class SerializerMutation(ClientIDMutation):
    class Meta:
        abstract = True

    errors = graphene.List(
        ErrorType,
        description='May contain more than one error for same field.'
    )

    @classmethod
    def __init_subclass_with_meta__(cls, serializer_class=None,
                                    only_fields=(), exclude_fields=(), **options):
        if not serializer_class:
            raise Exception('serializer_class is required for the SerializerMutation')

        serializer = serializer_class()
        input_fields = fields_for_serializer(serializer, only_fields, exclude_fields, is_input=True)

        _meta = SerializerMutationOptions(cls)
        _meta.serializer_class = serializer_class

        input_fields = yank_fields_from_attrs(
            input_fields,
            _as=InputField,
        )
        super(SerializerMutation, cls).__init_subclass_with_meta__(_meta=_meta, input_fields=input_fields, **options)

    @classmethod
    def mutate_and_get_payload(cls, root, info, **input):
        serializer = cls.get_serializer(root, info, **input)

        if serializer.is_valid():
            try:
                instance = cls.perform_mutate(serializer, info)
                return cls.get_success_result(instance, info)
            except serializers.ValidationError as e:
                errors = e.detail
                if not isinstance(errors, dict):
                    errors = {'__all__': errors}
        else:
            errors = serializer.errors

        errors = [
            ErrorType(field=key, messages=value)
            for key, value in errors.items()
        ]

        return cls.get_error_result(errors, info)

    @classmethod
    def get_serializer(cls, root, info, **input):
        return cls._meta.serializer_class(data=input)

    @classmethod
    def perform_mutate(cls, serializer, info):
        return serializer.save()

    @classmethod
    def get_success_result(cls, instance, info):
        return cls(errors=None)

    @classmethod
    def get_error_result(cls, errors, info):
        return cls(errors=errors)
