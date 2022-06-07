import uuid
from operator import itemgetter

from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.models import Group
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.functions import Coalesce
from django.urls import reverse
from django.utils.translation import ugettext as _
from imagekit.cachefiles import ImageCacheFile
from imagekit.models import ImageSpecField
from pilkit.processors import ResizeToFit

from internships.tokens import default_export_token_generator
from util.models import CreatedModifiedMixin


class CompanyContact(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=100)
    phone = models.CharField(max_length=15, null=True, blank=True)
    company = models.ForeignKey('Company', on_delete=models.CASCADE, related_name='contacts')

    def __str__(self):
        return f"{self.email} <{self.phone}>"


class CompanyManager(models.Manager):
    def get_queryset(self):
        return models.QuerySet(self.model) \
            .annotate(total_capacity=Coalesce(models.Sum('internships__capacity'), 0)) \
            .annotate(num_internships=models.Count('internships'))


class CompanyLogoField(ImageSpecField):
    def __init__(self, source, size, **kwargs):
        resizer = ResizeToFit(size, int(size * 0.7), upscale=True, mat_color=(0, 0, 0, 0))
        super().__init__(source=source, processors=[resizer], format='png', **kwargs)


class Company(CreatedModifiedMixin):
    objects = CompanyManager()

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(
        max_length=50, unique=True,
        help_text=_("Used when building the URL for the company's page, "
                    "e.g. https://practica.ligaac.ro/company/{slug}"),
    )
    description = RichTextUploadingField(max_length=8192, help_text=_("Short company description"))
    website = models.URLField(null=True, blank=True, help_text=_("Company website"))
    address = models.CharField(max_length=255, null=True, blank=True)
    visible_for_students = models.BooleanField(default=False,
                                               help_text="When the box is ticked the students can view the company in the application.")

    logo = models.ImageField(null=True, blank=True, upload_to='logos', help_text=_(
        "The company's logo in as high a resolution as possible. The display aspect ratio is 10:7."))
    group = models.OneToOneField(Group, null=True, blank=True, on_delete=models.DO_NOTHING)

    logo_32h = CompanyLogoField(source='logo', size=46)
    logo_300w = CompanyLogoField(source='logo', size=300)
    logo_500w = CompanyLogoField(source='logo', size=500)
    logo_1000w = CompanyLogoField(source='logo', size=1000)

    @property
    def logo_sizes(self):
        result = []
        if not self.logo:
            return result
        for field in dir(self):
            if field.startswith('logo_') and field != 'logo_sizes':
                spec = getattr(self, field, None)
                if isinstance(spec, ImageCacheFile):
                    result.append({'url': spec.url, 'width': spec.width})

        return sorted(result, key=itemgetter('width'), reverse=True)

    @property
    def applicants_export_url(self):
        return "{}?token={}".format(
            reverse('export_company_applicants', args=[self.pk]),
            default_export_token_generator.make_token(self),
        )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Company"


class InternshipTag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'


class FacultyTag(models.Model):
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=5, default='')


class InternshipOffer(CreatedModifiedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, help_text=_("Job title or project name"))
    description = RichTextUploadingField(max_length=4096, null=True, blank=True,
                                         help_text=_("Internship project description"))
    requirements = RichTextUploadingField(max_length=4096, null=True, blank=True,
                                          help_text=_("Technical knowledge required by the company for this job"))
    is_paid = models.BooleanField(help_text=_("Checked if students will be paid for the time "
                                              "worked during this internship program"))
    target_group = models.ForeignKey('FacultyTag', related_name='offer_target_group', on_delete=models.CASCADE)
    capacity = models.IntegerField(
        validators=[MinValueValidator(1)],
        help_text=_("The maximum number of students that will be accepted in this internship program")
    )

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='internships')
    tags = models.ManyToManyField(InternshipTag, null=True, blank=True, related_name="internship_offer")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Offer'
        verbose_name_plural = 'Offers'
