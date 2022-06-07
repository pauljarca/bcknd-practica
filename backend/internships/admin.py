from allauth.utils import build_absolute_uri
from django.conf import settings
from django.contrib import admin
from django.contrib.sites.shortcuts import get_current_site
from django.core import mail
from django.core.exceptions import PermissionDenied
from django.core.mail import EmailMessage
from django.db.models import Count
from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.urls import reverse, path
from django.utils.html import format_html
from imagekit.admin import AdminThumbnail
from import_export import resources
from import_export.admin import ExportActionModelAdmin
from reversion_compare.admin import CompareVersionAdmin

from .models import Company, InternshipOffer, CompanyContact, InternshipTag


class InternshipAdmin(admin.TabularInline):
    model = InternshipOffer
    extra = 0


class CompanyContactAdmin(admin.TabularInline):
    model = CompanyContact
    extra = 0


class CompanyResource(resources.ModelResource):
    id = resources.Field(attribute='id', readonly=True)
    total_capacity = resources.Field(column_name='total_capacity')
    applicant_count = resources.Field(column_name='applicant_count')
    export_url = resources.Field(column_name='export_url')
    contacts = resources.Field(column_name='contacts')

    def dehydrate_total_capacity(self, company):
        return company.total_capacity

    def dehydrate_applicant_count(self, company):
        return company.applicants.count()

    def dehydrate_export_url(self, company):
        return build_absolute_uri(None, company.applicants_export_url)

    def dehydrate_contacts(self, company):
        return ';'.join(f'{contact.name} <{contact.email}>' for contact in company.contacts.all())

    class Meta:
        model = Company
        fields = ('id', 'name', 'total_capacity', 'applicant_count', 'export_url', 'contacts')
        export_order = fields


@admin.register(Company)
class CompanyAdmin(ExportActionModelAdmin, CompareVersionAdmin):
    inlines = [CompanyContactAdmin,]
    list_display = ('logo_thumbnail', '__str__', 'visible_for_students', 'preview')
    list_display_links = ('logo_thumbnail', '__str__')
    logo_thumbnail = AdminThumbnail(image_field='logo_32h')
    resource_class = CompanyResource
    change_list_template = 'admin/import_export/change_list_export.html'

    def get_queryset(self, request):
        user = request.user
        qs = super(CompanyAdmin, self).get_queryset(request).distinct()
        if user.is_staff and not user.is_superuser:
            groups = user.groups.all()
            qs = qs.filter(group__in=groups)  # userul vede doar companiile din grupul in care e assignat
        return qs

    def get_fields(self, request, obj=None):
        fields = super(CompanyAdmin, self).get_fields(request, obj)
        if obj:
            fields_to_remove = []
            if not request.user.is_superuser:
                fields_to_remove = ['group', 'slug']
            for field in fields_to_remove:
                fields.remove(field)
        return fields

    def preview(self, obj):
        if not obj.visible_for_students:
            return None

        url = settings.EXTERNAL_URL + '/company/' + obj.slug
        return format_html(f'<a href={url}>Preview your company page</a>')

    preview.allow_tags = True

    # def get_urls(self):
    #     urls = super().get_urls()
    #     custom_urls = [
    #         path(
    #             '<str:company_id>/send_applicants/',
    #             self.admin_site.admin_view(self.send_emails_view),
    #             name='send_applicants_email',
    #         ),
    #     ]
    #     return custom_urls + urls
    #
    # def get_applicants_emails(self, request, company):
    #     if not request.user.is_superuser:
    #         raise PermissionDenied('Not authorized to send e-mails')
    #
    #     mail_context = {
    #         "export_url": request.build_absolute_uri(company.applicants_export_url),
    #         "current_site": get_current_site(request),
    #         "company": company,
    #     }
    #     template_name = 'practica/email/company_applicants'
    #
    #     subject = render_to_string(f'{template_name}_subject.txt', mail_context)
    #     message = render_to_string(f'{template_name}_message.txt', mail_context)
    #     recipients = [f'{contact.name} <{contact.email}>' for contact in company.contacts.all()]
    #     return [EmailMessage(subject, message, to=[recipient], cc=[settings.DEFAULT_FROM_EMAIL])
    #             for recipient in recipients]
    #
    # def send_applicants_emails(self, request, emails):
    #     sent = mail.get_connection().send_messages(emails)
    #
    #     if sent and sent >= len(emails):
    #         self.message_user(request, 'Success')
    #     else:
    #         self.message_user(request, 'Some messages failed to send')
    #     url = reverse(
    #         'admin:internships_company_changelist',
    #         current_app=self.admin_site.name,
    #     )
    #     return HttpResponseRedirect(url)
    #
    # def send_emails_view(self, request, company_id):
    #     company = self.get_object(request, company_id)
    #
    #     if request.method == 'POST':
    #         emails = self.get_applicants_emails(request, company)
    #         return self.send_applicants_emails(request, emails)
    #
    #     context = self.admin_site.each_context(request)
    #     context['opts'] = self.model._meta
    #     context['company'] = company
    #     context['title'] = 'Send applicants e-mail'
    #
    #     return TemplateResponse(request, 'admin/practica/company_applicants_email_action.html', context)
    #
    # def company_actions(self, obj):
    #     action_format = '<a class="button" href="{}">Export applicants</a>'
    #     action_args = [obj.applicants_export_url]
    #     if obj.contacts.count() > 0:
    #         action_format += '&nbsp;<a class="button" href="{}">Send applicants e-mails</a>'
    #         action_args.append(reverse('admin:send_applicants_email', args=[obj.pk]))
    #
    #     return format_html(action_format, *action_args)
    #
    # company_actions.short_description = ''
    # company_actions.allow_tags = True
    #
    # def send_emails_bulk_action(self, request, queryset):
    #     """
    #     Exports the selected rows using file_format.
    #     """
    #     emails = sum((self.get_applicants_emails(request, company) for company in queryset), [])
    #     return self.send_applicants_emails(request, emails)
    #
    # send_emails_bulk_action.short_description = 'Send applicant data to selected %(verbose_name_plural)s'
    #
    # actions = [send_emails_bulk_action]

    class Media:
        css = {'all': ('admin/css/practica/company_admin_changelist.css',)}


@admin.register(InternshipOffer)
class InternshipOfferAdmin(ExportActionModelAdmin, CompareVersionAdmin):
    list_display = ('__str__', 'company', 'internship_tags', )
    list_display_links = ('__str__', 'company')
    search_fields = ('title', 'tags__name' )
    filter_horizontal = ('tags',)

    def get_queryset(self, request):
        user = request.user
        qs = super().get_queryset(request).distinct()
        if user.is_staff and not user.is_superuser:
            groups = user.groups.all()
            qs = qs.filter(company__group__in=groups)
            # userul vede doar internshipurile companiei din grupul in care e asignat
        return qs

    def internship_tags(self, obj):
        return ", ".join([p.name for p in obj.tags.all()])

    def get_form(self, request, obj=None, **kwargs):
        user = request.user
        form = super(InternshipOfferAdmin, self).get_form(request, obj, **kwargs)
        if user.is_staff and not user.is_superuser:
            groups = user.groups.all()
            form.base_fields['company'].queryset = Company.objects.filter(group__in=groups)
        return form


@admin.register(InternshipTag)
class InternshipTagAdmin(ExportActionModelAdmin, CompareVersionAdmin):
    pass


