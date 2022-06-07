import os
import uuid

from django.conf import settings
from django.db import models
from django.db.models import URLField
from django.urls import reverse
from django.utils.text import get_valid_filename
from phonenumber_field.modelfields import PhoneNumberField
from private_storage.fields import PrivateFileField

from internships.models import InternshipOffer
from users.models import StudentClass
from util.models import CreatedModifiedMixin


document_types = [
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.oasis.opendocument.text',
    'text/plain',
]


class StudentProfile(CreatedModifiedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student")
    phone = PhoneNumberField(blank=True, null=True)
    specialization = models.CharField(blank=True, null=True, max_length=300)
    github = URLField("GitHub", blank=True, null=True)
    linkedin = URLField("LinkedIn", blank=True, null=True)
    study_class = models.ForeignKey(StudentClass, on_delete=models.PROTECT, related_name='registered_students')
    email = models.EmailField("Email", blank=True, null=True)
    cv = PrivateFileField("CV", upload_to="cv", blank=True, null=True,
                          max_file_size=10 * 1024 * 1024, content_types=document_types)

    @property
    def cv_filename(self):
        if self.cv:
            real_path = self.cv.path
            basename = os.path.basename(real_path) if real_path else ''
            return get_valid_filename(basename)

        return None

    @property
    def cv_url(self):
        if self.cv:
            return reverse('download_student_cv', kwargs={'pk': self.id, 'basename': self.cv_filename})

        return None

    applications = models.ManyToManyField(InternshipOffer, blank=True, related_name='applicants')

    def __str__(self):
        return self.user.get_full_name()

    class Meta:
        verbose_name = 'Application'
        verbose_name_plural = 'Applications'
