import os
import unicodedata

from django import forms
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, JsonResponse
from django.views import View
from private_storage.models import PrivateFile
from private_storage.views import PrivateStorageDetailView

from students.models import StudentProfile
from util.helpers import encode_content_disposition_filename


class StudentCVDownloadView(PrivateStorageDetailView):
    model = StudentProfile
    model_file_field = 'cv'
    content_disposition = 'inline'

    def can_access_file(self, private_file: PrivateFile):
        # this would require cookie login in order to work on file URLs;
        # until a better solution, just leave the files publicly accesible
        # return private_file.request.user.is_superuser or private_file.request.user == private_file.parent_object.user
        return True

    def get_content_disposition_filename(self, private_file: PrivateFile):
        full_name = private_file.parent_object.user.get_full_name()
        if full_name:
            extension = os.path.splitext(os.path.basename(private_file.relative_name))[1]
            return f"{full_name}{extension}"
        else:
            return super().get_content_disposition_filename(private_file)

    def _encode_filename_header(self, filename):
        return encode_content_disposition_filename(filename).encode('utf-8')


class StudentCVUploadForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ('cv',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cv'].required = True


class StudentCVUploadView(View):
    http_method_names = ('post', 'options')

    def post(self, request, *args, **kwargs):
        user = request.user
        if not user or not user.student:
            raise PermissionDenied()

        form = StudentCVUploadForm(request.POST, request.FILES, instance=user.student)
        if form.is_valid():
            student = form.save()

            response = HttpResponse(status=201)
            response['Location'] = student.cv_url
            return response

        return JsonResponse(form.errors, status=400)
