# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-04 23:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interface', '0003_repository_full_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='pullrequest',
            name='branch',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
    ]
