from django.contrib import admin
from ordered_model.admin import OrderedModelAdmin
from reversion_compare.admin import CompareVersionAdmin

from faq.models import Faq


@admin.register(Faq)
class FaqAdmin(CompareVersionAdmin, OrderedModelAdmin):
    list_display = ('__str__', 'move_up_down_links')
    ordering = ('order',)
