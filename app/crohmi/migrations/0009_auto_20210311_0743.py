# Generated by Django 2.2.19 on 2021-03-11 07:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crohmi', '0008_auto_20200608_0224'),
    ]

    operations = [
        migrations.DeleteModel(
            name='AirReading',
        ),
        migrations.RenameField(
            model_name='reading',
            old_name='pole_no',
            new_name='node_id',
        ),
        migrations.RenameField(
            model_name='reading',
            old_name='created_at',
            new_name='timestamp',
        ),
        migrations.AddField(
            model_name='reading',
            name='c2h5oh',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='reading',
            name='c3h8',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='reading',
            name='c4h10',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='reading',
            name='ch4',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='reading',
            name='co',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='reading',
            name='h2',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='reading',
            name='nh3',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='reading',
            name='no2',
            field=models.FloatField(default=0),
            preserve_default=False,
        ),
    ]
