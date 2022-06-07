import os
from datetime import datetime
from tempfile import NamedTemporaryFile

import pytz
import zipseeker
from allauth.utils import build_absolute_uri
from django.core.exceptions import PermissionDenied
from django.http import StreamingHttpResponse
from django.utils.encoding import filepath_to_uri
from django.views.generic.base import View
from django.views.generic.detail import SingleObjectMixin
from import_export import resources
from import_export.formats import base_formats

from internships.models import Company
from internships.tokens import default_export_token_generator
from students.models import StudentProfile
from util.helpers import encode_content_disposition_filename


def get_cv_filename(profile):
    if profile.cv_filename:
        cv_filename = os.path.splitext(profile.cv_filename)
        return f'cv/{cv_filename[0]}@{profile.id}{cv_filename[1]}'

    return None


class ApplicantProfileResource(resources.ModelResource):
    id = resources.Field(attribute='id', readonly=True)
    study_class = resources.Field(column_name='class')
    first_name = resources.Field(attribute='user__first_name', column_name='first_name')
    last_name = resources.Field(attribute='user__last_name', column_name='last_name')
    phone = resources.Field(attribute='phone', column_name='tel')
    email = resources.Field(attribute='user__email', column_name='email')
    cv_filename = resources.Field(column_name='cv_filename')
    cv_url = resources.Field(column_name='cv_url')

    def dehydrate_study_class(self, profile):
        return str(profile.study_class)

    def dehydrate_cv_url(self, profile):
        cv_url = profile.cv_url
        return build_absolute_uri(None, cv_url) if cv_url else ""

    def dehydrate_cv_filename(self, profile):
        return get_cv_filename(profile) or ""

    class Meta:
        model = StudentProfile
        fields = ('id', 'study_class', 'last_name', 'first_name', 'phone', 'email', 'cv_url', 'cv_filename',
                  'facebook', 'linkedin', 'github')
        export_order = fields


class ExportApplicantsView(SingleObjectMixin, View):
    model = Company
    data_export_formats = (base_formats.CSV(), base_formats.XLS(), base_formats.ODS())
    token_generator = default_export_token_generator

    def get_applicant_cv_file(self, applicant):
        cv_filename = get_cv_filename(applicant)
        if not cv_filename:
            return None
        return applicant.cv.path, cv_filename

    def get_export_data_file(self, applicants, timestamp, export_format):
        resource_class = ApplicantProfileResource
        export_data = export_format.export_data(resource_class().export(applicants))
        if hasattr(export_data, 'encode'):
            export_data = export_data.encode('utf-8')

        extension = export_format.get_extension()
        filename = f'date-studenti-{timestamp}.{extension}'
        with NamedTemporaryFile(delete=False) as f:
            f.write(export_data)
            # not deleted on close
        return f.name, filename

    def get_zip_stream(self, zip_files):
        z = zipseeker.ZipSeeker()
        for path, zipname in zip_files:
            z.add(path, zipname)

        return z.size(), z.blocks()

    def get(self, request, pk):
        company = self.get_object()
        if 'token' not in request.GET:
            raise PermissionDenied('missing token')
        token = request.GET['token']
        if not self.token_generator.check_token(company, token):
            raise PermissionDenied('invalid or expired token')

        applicants = company.applicants.all()
        zip_files = []

        timestamp = datetime.now(tz=pytz.timezone('Europe/Bucharest')).strftime('%Y-%m-%d_%H-%M-%S')
        for export_format in self.data_export_formats:
            zip_files.append(self.get_export_data_file(applicants, timestamp, export_format))
        for applicant in applicants:
            cv_file = self.get_applicant_cv_file(applicant)
            if cv_file:
                zip_files.append(cv_file)

        size, data = self.get_zip_stream(zip_files)
        response = StreamingHttpResponse(data, content_type='application/zip')
        export_filename = filepath_to_uri(f'practica-ligaac-ro-{company.slug}-{timestamp}.zip')
        response['Content-Disposition'] = 'attachment; ' + encode_content_disposition_filename(export_filename)
        response['Content-Length'] = size
        return response
