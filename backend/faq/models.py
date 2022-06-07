import uuid

from ckeditor_uploader.fields import RichTextUploadingField
from django.db import models
from ordered_model.models import OrderedModel

from util.models import CreatedModifiedMixin


class Faq(OrderedModel, CreatedModifiedMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.CharField(max_length=512)
    answer = RichTextUploadingField(max_length=4096)

    def __str__(self):
        return self.question

    class Meta:
        verbose_name = "FAQ"
        verbose_name_plural = "FAQ"
