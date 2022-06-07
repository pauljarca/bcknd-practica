from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import ugettext_lazy as _
from import_export import resources
from import_export.admin import ImportExportMixin, ExportActionModelAdmin
from import_export.forms import ImportForm
from import_export.tmp_storages import TempFolderStorage

from students.admin import StudentListAdminMixin, StudentProfileInlineAdmin
from users.models import StudentClass, User


class UnicodeTempFolderStorage(TempFolderStorage):
    def open(self, mode='r'):
        if self.name and 'b' not in mode:
            return open(self.get_full_path(), mode, encoding='utf-8')

        return super().open(mode)


@admin.register(StudentClass)
class StudentClassAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)


@admin.register(User)
class ProfileUserAdmin(UserAdmin):
    inlines = (StudentProfileInlineAdmin,)
    list_display = UserAdmin.list_display + ('date_joined',)
