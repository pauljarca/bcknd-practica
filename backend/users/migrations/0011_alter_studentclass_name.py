# Generated by Django 3.2.12 on 2022-03-22 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_alter_studentclass_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentclass',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]