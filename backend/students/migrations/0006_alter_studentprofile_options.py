# Generated by Django 3.2.11 on 2022-02-06 18:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0005_alter_studentprofile_applications'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='studentprofile',
            options={'verbose_name': 'Application', 'verbose_name_plural': 'Applications'},
        ),
    ]
