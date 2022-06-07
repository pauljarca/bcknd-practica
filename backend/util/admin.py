from django.contrib import admin
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


def get_nested_filters(label, field):
    class RelatedExistsListFilter(admin.SimpleListFilter):
        title = label.lower()
        parameter_name = f'has_{field}'

        def lookups(self, request, model_admin):
            return (
                ('1', _('filled in')),
                ('0', _('not filled in')),
            )

        def queryset(self, request, queryset):
            if self.value() not in ('0', '1'):
                return queryset

            is_null = Q(**{f'{field}__isnull': True})
            return queryset.filter(is_null if self.value() == '0' else ~is_null).distinct()

    return RelatedExistsListFilter


def add_nested_filters(fields):
    def decorator(cls):
        for field, label in fields:
            RelatedExistsListFilter = get_nested_filters(label, field)
            cls.list_filter = cls.list_filter + (RelatedExistsListFilter,)

        return cls

    return decorator
