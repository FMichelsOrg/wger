# Generated by Django 3.2.12 on 2022-02-22 19:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20210726_1729'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='current_medical_reasons_not_to_exercise',
            field=models.TextField(
                blank=True, null=True, verbose_name='Current medical reasons not to exercise'
            ),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='current_medication',
            field=models.TextField(blank=True, null=True, verbose_name='Current medication'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='current_physical_problems',
            field=models.TextField(blank=True, null=True, verbose_name='Current physical problems'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='current_used_supplements',
            field=models.TextField(blank=True, null=True, verbose_name='Current used supplements'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='job',
            field=models.CharField(
                blank=True, help_text='The primary job', max_length=60, verbose_name='Job'
            ),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='past_medical_reasons_not_to_exercise',
            field=models.TextField(
                blank=True, null=True, verbose_name='Past medical reasons not to exercise'
            ),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='past_medication',
            field=models.TextField(blank=True, null=True, verbose_name='Past medication'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='past_physical_problems',
            field=models.TextField(blank=True, null=True, verbose_name='Past physical problems'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='past_used_supplements',
            field=models.TextField(blank=True, null=True, verbose_name='Past used supplements'),
        ),
    ]
