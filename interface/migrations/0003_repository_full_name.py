# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-03 18:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interface', '0002_pullrequest_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='repository',
            name='full_name',
            field=models.CharField(default='', max_length=300),
            preserve_default=False,
        ),
    ]
