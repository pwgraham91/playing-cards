# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0002_auto_20141015_2216'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='ties',
            field=models.IntegerField(default=0, max_length=3),
            preserve_default=True,
        ),
    ]
