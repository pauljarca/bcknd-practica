# Generated by Django 3.2.9 on 2021-11-11 21:03

import ckeditor_uploader.fields
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('internships', '0002_many_contacts'),
    ]

    operations = [
        migrations.CreateModel(
            name='InternshipCategory',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.AlterField(
            model_name='internshipoffer',
            name='description',
            field=ckeditor_uploader.fields.RichTextUploadingField(blank=True, help_text='Internship project description', max_length=4096, null=True),
        ),
        migrations.AddField(
            model_name='internshipoffer',
            name='tags',
            field=models.ManyToManyField(related_name='internship_offer', to='internships.InternshipCategory'),
        ),
    ]
