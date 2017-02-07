# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-07 12:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('server', '0003_groupinfo_userinfo'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='groups',
            field=models.CharField(max_length=800, null=True),
        ),
        migrations.AlterField(
            model_name='groupinfo',
            name='permission',
            field=models.CharField(max_length=800),
        ),
        migrations.AlterField(
            model_name='userinfo',
            name='permission',
            field=models.CharField(max_length=800),
        ),
    ]
