# Generated by Django 3.2.13 on 2022-06-06 15:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0008_auto_20220404_2136'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='existingemployment',
            name='student',
        ),
        migrations.DeleteModel(
            name='LigaAcLabsLab',
        ),
        migrations.RemoveField(
            model_name='othercondition',
            name='student',
        ),
        migrations.RemoveField(
            model_name='plannedinternship',
            name='student',
        ),
        migrations.RemoveField(
            model_name='studentprofile',
            name='liga_ac_labs',
        ),
        migrations.DeleteModel(
            name='ExistingEmployment',
        ),
        migrations.DeleteModel(
            name='OtherCondition',
        ),
        migrations.DeleteModel(
            name='PlannedInternship',
        ),
    ]
