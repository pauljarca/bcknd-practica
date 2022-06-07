from itertools import chain

from django.contrib import admin
from django.contrib.admin.utils import flatten_fieldsets


class ReadOnlyModelAdmin(admin.ModelAdmin):
    """
    ModelAdmin class that prevents modifications through the admin.

    The changelist and the detail view work, but a 403 is returned
    if one actually tries to edit an object.

    Source:
    https://gist.github.com/aaugustin/1388243
    https://djangosnippets.org/snippets/10539/
    """
    change_form_template = "admin/view.html"

    # We cannot call super().get_fields(request, obj) because that method calls
    # get_readonly_fields(request, obj), causing infinite recursion. Ditto for
    # super().get_form(request, obj). So we assume the default ModelForm.
    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in obj._meta.get_fields()
                if not field.one_to_many]

    def has_add_permission(self, request):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    # Allow viewing objects but not actually changing them.
    def has_change_permission(self, request, obj=None):
        return request.method in ['GET', 'HEAD'] and super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, *args, **kwargs):
        pass

    def delete_model(self, *args, **kwargs):
        pass

    def save_related(self, *args, **kwargs):
        pass
