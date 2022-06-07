import inspect
import sys
from importlib import import_module

import graphene
from django.apps import apps
from django.utils.module_loading import module_has_submodule
from graphql import GraphQLNonNull, GraphQLInputObjectType, GraphQLList, GraphQLScalarType
from graphql_relay import from_global_id


def autodiscover_modules(module_name):
    modules = []

    for app_config in apps.get_app_configs():
        # Attempt to import the app's module.
        try:
            module_path = '%s.%s' % (app_config.name, module_name)
            import_module(module_path)
            modules.append(sys.modules[module_path])
        except Exception:
            # Decide whether to bubble up this error. If the app just
            # doesn't have the module in question, we can ignore the error
            # attempting to import it, otherwise we want it to bubble up.
            if module_has_submodule(app_config.module, module_name):
                raise

    return modules


def autodiscover_classes(module_name, class_name):
    modules = autodiscover_modules(module_name)
    classes = []

    for module in modules:
        cls = getattr(module, class_name, None)
        if cls and inspect.isclass(cls):
            classes.append(cls)

    return classes


class Query(*autodiscover_classes('schema', 'Query'), graphene.ObjectType):
    pass


class Mutation(*autodiscover_classes('schema', 'Mutation'), graphene.ObjectType):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)


class RelayIDMiddleware(object):
    def unwrap_gql_nonnull(self, gql_type):
        if isinstance(gql_type, GraphQLNonNull):
            gql_type = gql_type.of_type

        return gql_type

    def decode_relay_id(self, relay_id):
        # we want to handle both the case where a Relay ID was passed
        # and the case where a regular (UUID/integer/etc) ID was passed;
        # the first case is important for code that must be able to pass IDs back to the server after reading them
        # from query types, while the second case is important for usability and debugging - i.e. graphiql
        try:
            # regular integer/integer-like ID - could technically be base64, but probably not
            if int(relay_id) < 1e10:
                return relay_id
        except ValueError:
            pass

        try:
            _type, _id = from_global_id(relay_id)
            return _id
        except (ValueError, LookupError):
            # if global id decoding fails just return as-is
            return relay_id

    def replace_relay_ids(self, gql_type, obj):
        gql_type = self.unwrap_gql_nonnull(gql_type)
        if isinstance(gql_type, GraphQLInputObjectType):
            for field in gql_type.fields.values():
                if field.out_name in obj:
                    field_value = obj[field.out_name]
                    obj[field.out_name] = self.replace_relay_ids(field.type, field_value)
        elif isinstance(gql_type, GraphQLList):
            obj[:] = [self.replace_relay_ids(gql_type.of_type, val) for val in obj]
        elif isinstance(gql_type, GraphQLScalarType) and gql_type.name == 'ID':
            obj = self.decode_relay_id(obj)

        return obj

    def resolve(self, next_resolver, root, info, **args):
        try:
            gql_type = info.parent_type.fields[info.field_name]
            for arg, value in args.items():
                arg_type = gql_type.args[arg].type
                args[arg] = self.replace_relay_ids(arg_type, value)
        except Exception:
            pass

        return next_resolver(root, info, **args)
