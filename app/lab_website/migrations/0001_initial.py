# Generated by Django 2.2.10 on 2020-04-18 01:45

import core.models
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Member',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('image', models.FileField(upload_to=core.models.upload_file)),
                ('description', models.TextField()),
            ],
            options={
                'default_related_name': 'members',
            },
        ),
        migrations.CreateModel(
            name='MemberAction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('link', models.TextField()),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='member_actions', to='lab_website.Member')),
            ],
            options={
                'default_related_name': 'member_actions',
            },
        ),
    ]