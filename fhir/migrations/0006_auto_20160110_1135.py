# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fhir', '0005_auto_20160109_2017'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supportedresourcetype',
            name='create',
            field=models.BooleanField(verbose_name='create', default=False, help_text='FHIR Interaction Type'),
        ),
        migrations.AlterField(
            model_name='supportedresourcetype',
            name='delete',
            field=models.BooleanField(verbose_name='delete', default=False, help_text='FHIR Interaction Type'),
        ),
        migrations.AlterField(
            model_name='supportedresourcetype',
            name='get',
            field=models.BooleanField(verbose_name='get', default=False, help_text='FHIR Interaction Type'),
        ),
        migrations.AlterField(
            model_name='supportedresourcetype',
            name='history',
            field=models.BooleanField(verbose_name='_history', default=False, help_text='FHIR Interaction Type'),
        ),
        migrations.AlterField(
            model_name='supportedresourcetype',
            name='json_schema',
            field=models.TextField(default='{}', max_length=5120, help_text='{} indicates no schema.'),
        ),
        migrations.AlterField(
            model_name='supportedresourcetype',
            name='put',
            field=models.BooleanField(verbose_name='put', default=False, help_text='FHIR Interaction Type'),
        ),
        migrations.AlterField(
            model_name='supportedresourcetype',
            name='read',
            field=models.BooleanField(verbose_name='read', default=False, help_text='FHIR Interaction Type'),
        ),
        migrations.AlterField(
            model_name='supportedresourcetype',
            name='search',
            field=models.BooleanField(verbose_name='search', default=False, help_text='FHIR Interaction Type'),
        ),
        migrations.AlterField(
            model_name='supportedresourcetype',
            name='update',
            field=models.BooleanField(verbose_name='update', default=False, help_text='FHIR Interaction Type'),
        ),
        migrations.AlterField(
            model_name='supportedresourcetype',
            name='vread',
            field=models.BooleanField(verbose_name='vread', default=False, help_text='FHIR Interaction Type'),
        ),
    ]
