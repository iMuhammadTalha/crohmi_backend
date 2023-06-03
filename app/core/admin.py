import re

from django.core.files.images import ImageFile
from django.contrib import admin
from django.db import transaction
from django.utils import timezone
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.admin import ModelAdmin

from crohmi import ndvi_algorithm

import pandas as pd

from . import models


class UserAdmin(BaseUserAdmin):
    ordering = ['email']
    list_display = ['email']

    fieldsets = (
        (None, {'fields': ('email', 'password', 'name', 'title', 'avatar')}),
        ('Permissions',
         {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login',)})
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2')
        }),
    )


class NdviMapAdmin(ModelAdmin):

    readonly_fields = ('month', 'health_map', 'ndvi_image')

    def save_model(self, request, obj, form, change):
        obj.month = obj.created_at.month
        obj.save()

        # Get np array
        ndvi_array = ndvi_algorithm.ndvi_array_calc(obj.nri_image)

        # Calc ndvi image
        ndvi_image = ImageFile(ndvi_algorithm.ndvi_image(obj.nri_image,
                                                         ndvi_array,
                                                         obj.month,
                                                         obj.created_at.year))
        obj.ndvi_image.save(f'{obj.id}_ndvi_map.png', ndvi_image)

        # Calc health map
        health_map = ImageFile(ndvi_algorithm.health_image(ndvi_array,
                                                           obj.month,
                                                           obj.created_at.year))
        obj.health_map.save(f'{obj.id}_health_map.png', health_map)


# User
admin.site.register(models.User, UserAdmin)

# Crohmi
admin.site.register(models.Reading)
admin.site.register(models.NdviMap, NdviMapAdmin)
admin.site.register(models.SatelliteImage)

# Lab Website


class MemberActionInline(admin.StackedInline):
    """Inline for Member Action model"""

    model = models.MemberAction
    extra = 1


class MemberAdmin(admin.ModelAdmin):
    """Admin for Member model"""

    model = models.Member
    inlines = [MemberActionInline]


admin.site.register(models.Member, MemberAdmin)
admin.site.register(models.Project)


# Core
class DataMigrationAdmin(admin.ModelAdmin):
    """Admin for Data Migration model"""

    ordering = ['name', ]

    actions = ['add_readings', 'add_air_readings']

    def add_readings(self, request, queryset):
        """Add readings from CSV files"""
        for obj in queryset:
            with transaction.atomic():
                pd_csv = pd.read_csv(obj.file)
                pd_csv.fillna(0, inplace=True)
                readings = []
                for row in pd_csv.itertuples():
                    if not (row.air_moisture and row.air_temperature and
                            row.soil_moisture and row.soil_temperature):
                        continue
                    readings.append(models.Reading(
                        air_moisture=row.air_moisture,
                        air_temperature=row.air_temperature,
                        soil_moisture=row.soil_moisture,
                        soil_temperature=row.soil_temperature,
                        node_id=row.pole_no,
                        created_at=timezone.datetime.strptime(
                            row.datetime, '%Y.%m.%d %H:%M:%S'
                        )
                    ))

                models.Reading.objects.bulk_create(readings)

    def add_air_readings(self, request, queryset):
        """Add air readings from crohmi downloaded data"""
        for obj in queryset:
            with transaction.atomic():
                obj.file.open(mode='r')
                data_str = obj.file.readlines()[0]
                data_array = re.split(',|, ', data_str)

                multiple = 0
                air_readings = []
                for counter in range(len(data_array) // 12):
                    air_readings.append(models.Reading(
                        timestamp=timezone.datetime.strptime(
                            data_array[1 + multiple].strip('"'),
                            '%Y.%m.%d %H:%M:%S'),
                        nh3=data_array[2 + multiple],
                        co=data_array[3 + multiple],
                        no2=data_array[4 + multiple],
                        c3h8=data_array[5 + multiple],
                        c4h10=data_array[6 + multiple],
                        ch4=data_array[7 + multiple],
                        h2=data_array[8 + multiple],
                        c2h5oh=data_array[9 + multiple],
                        node_id=data_array[12 + multiple].split()[0]
                    ))
                    multiple += 12

                models.Reading.objects.bulk_create(air_readings)

    add_readings.short_description = 'Add readings from selected data ' \
                                     'migrations'
    add_air_readings.short_description = 'Add air readings from selected ' \
                                         'data migrations (Text Based)'


admin.site.register(models.DataMigration, DataMigrationAdmin)
