# Generated by Django 2.2.10 on 2020-05-31 12:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lab_website', '0002_project'),
    ]

    operations = [
        migrations.AddField(
            model_name='member',
            name='order',
            field=models.PositiveSmallIntegerField(default=1),
            preserve_default=False,
        ),
    ]