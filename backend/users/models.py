import binascii
import os
import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.template.defaultfilters import title
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class StudentClass(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    study_year = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=100)
    credits = models.PositiveSmallIntegerField(default=0)
    hours = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f"{self.study_year} {self.name}"

    class Meta:
        verbose_name = _('Specialization')
        verbose_name_plural = _('Specialization')


class User(AbstractUser):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions and is identified by e-mail address.

    Email and password are required. Other fields are optional.
    """
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        null=True,
        help_text=_('150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[AbstractUser.username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    email = models.EmailField(
        _('email address'),
        unique=True,
        error_messages={
            'unique': _("A user with that e-mail address already exists."),
        },
    )

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    reg = models.CharField(max_length=32, unique=True, null=True, blank=True, default=None, help_text="Număr matricol")


    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        return title(super().get_full_name())

    def __str__(self):
        short_name = self.get_short_name()
        if short_name:
            return title(short_name)
        elif self.first_name or self.last_name:
            return self.get_full_name()
        elif self.username:
            return self.username
        else:
            return super().__str__()


class Token(models.Model):
    """
    An access token that is associated with a user. This is essentially the
    same as the token model from Django REST Framework.
    """
    key = models.CharField(max_length=40, primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tokens")
    created = models.DateTimeField(auto_now_add=True)
    expiration = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
            self.expiration = timezone.now() + timedelta(days=7)
        return super(Token, self).save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key
