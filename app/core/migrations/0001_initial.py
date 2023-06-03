# Generated by Django 2.2.10 on 2020-05-24 13:03

import core.models
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DataMigration',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('file', models.FileField(upload_to=core.models.upload_file)),
            ],
            options={
                'default_related_name': 'data_migrations',
            },
        ),
    ]