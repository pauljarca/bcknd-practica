# Generated by Django 2.0.3 on 2018-04-01 21:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields
import private_storage.fields
import private_storage.storage.files
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0005_prefill_related_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentProfile',
            fields=[
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('reg', models.CharField(help_text='Număr matricol', max_length=32, unique=True)),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True)),
                ('cv', private_storage.fields.PrivateFileField(blank=True, null=True, storage=private_storage.storage.files.PrivateFileSystemStorage(), upload_to='cv', verbose_name='CV')),
                ('study_class', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='registered_students', to='users.StudentClass')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='student', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
