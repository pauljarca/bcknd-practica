# Generated by Django 3.2.12 on 2022-04-04 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0007_auto_20220206_2115'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentprofile',
            name='specialization',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]