# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SupportedResourceType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('resource_name', models.CharField(db_index=True, unique=True, max_length=256)),
                ('json_schema', models.TextField(help_text='{} indicates no schema.', default='{}', max_length=5120)),
            ],
        ),
    ]
