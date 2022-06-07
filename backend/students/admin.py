from allauth.utils import build_absolute_uri
from django.contrib import admin
from django.contrib.admin import StackedInline
from django.db.models import Q, Count
from django.urls import reverse
from django.utils.html import escape, format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from import_export import resources
from import_export.admin import ImportExportMixin, ExportActionModelAdmin

from students.models import StudentProfile
from util.admin import add_nested_filters
from django.http import HttpResponseForbidden


class ProfileCompletionListFilter(admin.SimpleListFilter):
    title = _('profile status')
    parameter_name = 'profile_complete'

    def lookups(self, request, model_admin):
        return (
            ('1', _('completed')),
            ('0', _('not completed')),
        )

    def queryset(self, request, queryset):
        if self.value() not in ('0', '1'):
            return queryset

        cv_q = (Q(cv__isnull=False) & ~Q(cv__exact='')) | (Q(linkedin__isnull=False) & ~Q(linkedin__exact=''))
        app_q = Q(applications__isnull=False) & cv_q
        fq = app_q
        return queryset.filter(fq if self.value() == '1' else ~fq).distinct()


class StudentListAdminMixin(object):
    list_display = ('__str__', 'study_class')
    search_fields = ('user__email', 'user__first_name', 'user__last_name', 'applications__title')


practica_fields = (
    ('employment', 'employment'),
    ('internship', 'internship'),
    ('applications', 'applications')
)


def add_resource_fields(fields):
    def decorator(cls):
        for field, label in fields:
            cls.fields[field] = resources.Field(column_name=field)

            def dehydrate(attr):
                def _dehydrate(self, obj):
                    rel = getattr(obj, attr, None)
                    if rel is not None:
                        try:
                            return ",".join(map(str, rel.all()))
                        except Exception:
                            return str(rel)

                    return ""

                return _dehydrate

            setattr(cls, f'dehydrate_{field}', dehydrate(field))

        return cls

    return decorator


class StudentProfileResource(resources.ModelResource):
    id = resources.Field(attribute='id', readonly=True)
    first_name = resources.Field(attribute='user__first_name', column_name='first_name')
    last_name = resources.Field(attribute='user__last_name', column_name='last_name')
    phone = resources.Field(attribute='phone', column_name='tel')
    email = resources.Field(attribute='user__email', column_name='email')
    study_class = resources.Field(attribute='study_class_id', column_name='serie')
    cv_url = resources.Field(attribute='cv_url', column_name='cv')
    user = None

    def get_queryset(self, request):
        self.user = request.user
        qs = super().get_queryset(request).distinct()
        if self.user.is_staff and not self.user.is_superuser:
            groups = self.user.groups.all()
            qs = qs.filter(applications__company__group__in=groups)
            # userul vede doar studentii care au aplicat la internshipurile companiei din grupul in care e asignat
        return qs

    def dehydrate_study_class(self, profile):
        return str(profile.study_class)

    def dehydrate_cv_url(self, profile):
        cv_url = profile.cv_url
        return build_absolute_uri(None, cv_url) if cv_url else ""

    # def dehydrate_applications(self, profile):
    #     user = request.user
    #     groups = user.groups.all()
    #     return '\n'.join([p.title for p in profile.applications.filter(company__group__in=groups)])

    class Meta:
        model = StudentProfile
        fields = ('study_class', 'last_name', 'first_name', 'phone', 'email', 'cv_url',
                  'linkedin', 'github', 'applications')
        export_order = fields


# noinspection PyTypeChecker
@admin.register(StudentProfile)
class StudentProfileAdmin(StudentListAdminMixin, admin.ModelAdmin):
    list_display = StudentListAdminMixin.list_display + ( 'phone', 'email', 'get_cv_url',
                  'get_linkedin_url', 'get_github_url', 'get_applications','created_date', )
    resource_class = StudentProfileResource
    change_list_template = 'admin/import_export/change_list_export.html'
    filter_horizontal = ('applications',)

    user = None

    def get_queryset(self, request):
        self.user = request.user
        qs = super().get_queryset(request).distinct()
        if self.user.is_staff and not self.user.is_superuser:
            groups = self.user.groups.all()
            qs = qs.filter(applications__company__group__in=groups)
            # userul vede doar studentii care au aplicat la internshipurile companiei din grupul in care e asignat
        return qs

    def get_list_display_links(self, request, list_display):
        if request.user.is_staff and not request.user.is_superuser:
            return None
        return super(StudentProfileAdmin, self).get_list_display_links(request, list_display)

    def get_applications(self, obj,):
        applications = obj.applications.all()
        if self.user.is_staff and not self.user.is_superuser:
            groups = self.user.groups.all()
            applications = applications.filter(company__group__in=groups)
        return format_html("<br/>".join([p.title for p in applications]))

    def get_cv_url(self, obj,):
        if obj.cv_url:
            return format_html("<a href=\"" +  obj.cv_url + "\" target=\"_blank\">View</a>")
        return ""

    def get_linkedin_url(self, obj,):
        if obj.linkedin:
            return format_html("<a href=\"" +  obj.linkedin + "\" target=\"_blank\">View</a>")
        return ""

    def get_github_url(self, obj,):
        if obj.github:
            return format_html("<a href=\"" +  obj.github + "\" target=\"_blank\">View</a>")
        return ""

    def get_object(self, request, object_id, from_field=None):
        # Hook obj for use in formfield_for_manytomany
        # self.obj = super(StudentProfileAdmin, self).get_object(request, object_id, from_field)
        if request.user.is_staff and not request.user.is_superuser:
            return None
        else:
            return super(StudentProfileAdmin,self).get_object(request, object_id, from_field)
        # return self.obj

    # def formfield_for_manytomany(self, db_field, request, **kwargs):
    #     if db_field.name == "applications" and getattr(self, 'obj', None):
    #         if request.user.is_staff and not request.user.is_superuser:
    #             groups = request.user.groups.all()
    #             kwargs["queryset"] = self.obj.applications.filter(company__group__in=groups)
    #             import ipdb; ipdb.set_trace()
    #     return super(StudentProfileAdmin, self).formfield_for_manytomany(
    #         db_field, request, **kwargs)

    get_applications.allow_tags = True
    get_applications.short_description = "applications"
    get_cv_url.allow_tags = True
    get_cv_url.short_description = "CV"
    get_linkedin_url.allow_tags = True
    get_linkedin_url.short_description = "Linkedin"
    get_github_url.allow_tags = True
    get_github_url.short_description = "Github"


class StudentProfileInlineAdmin(StackedInline):
    model = StudentProfile

    def has_delete_permission(self, *args, **kwargs):
        return False

    def has_add_permission(self, *args, **kwargs):
        return False
