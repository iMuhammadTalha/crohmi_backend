from uuid import uuid4

from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, \
    BaseUserManager
from django.core.validators import MaxValueValidator, MinValueValidator


def upload_file(instance, file_name):
    return file_name


class UserManager(BaseUserManager):
    """Manager for User model"""

    def create_user(self, email, password, **kwargs):
        """Creates and saves the user"""
        if not email:
            raise ValueError("User must have an email address")
        user = self.model(email=email.lower(), **kwargs)
        user.set_password(password)

        user.save()

        return user

    def create_superuser(self, email, password):
        """Creates and saves the superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True

        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User model"""
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        app_label = 'user'
        default_related_name = 'users'

    def __str__(self):
        return self.email


def ndvi_image_path(instance, file_name):
    """File path for NDVI"""
    return file_name


class NdviMap(models.Model):
    """Model for NDVI Map"""
    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    nri_image = models.ImageField(upload_to=ndvi_image_path)
    ndvi_image = models.ImageField(null=True, upload_to=ndvi_image_path, blank=True)
    month = models.PositiveSmallIntegerField(default=1, blank=True, validators=[MaxValueValidator(12), MinValueValidator(1)])
    year = models.IntegerField(default=2019,validators=[MinValueValidator(2018)])
    health_map = models.ImageField(null=True, upload_to=ndvi_image_path, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        app_label = 'crohmi'
        default_related_name = 'ndvi_maps'

    def __str__(self):
        return f'NDVI Map: {self.created_at}'


class Reading(models.Model):
    """Reading model"""
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)

    timestamp = models.DateTimeField(default=timezone.now)
    air_moisture = models.FloatField(validators=[MaxValueValidator(101), MinValueValidator(0.0)])
    air_temperature = models.FloatField(validators=[MaxValueValidator(101), MinValueValidator(0.0)])
    soil_moisture = models.FloatField(validators=[MaxValueValidator(101), MinValueValidator(0.0)])
    soil_temperature = models.FloatField(validators=[MaxValueValidator(101), MinValueValidator(0.0)])
    nh3 = models.FloatField(validators=[MaxValueValidator(2000), MinValueValidator(0.0)])
    co = models.FloatField(validators=[MaxValueValidator(5000), MinValueValidator(0.0)])
    no2 = models.FloatField(validators=[MaxValueValidator(5000), MinValueValidator(0.0)])
    c3h8 = models.FloatField(validators=[MaxValueValidator(5000), MinValueValidator(0.0)])
    c4h10 = models.FloatField(validators=[MaxValueValidator(5000), MinValueValidator(0.0)])
    ch4 = models.FloatField(validators=[MaxValueValidator(5000), MinValueValidator(0.0)])
    h2 = models.FloatField(validators=[MaxValueValidator(5000), MinValueValidator(0.0)])
    c2h5oh = models.FloatField(validators=[MaxValueValidator(5000), MinValueValidator(0.0)])
    node_id = models.PositiveSmallIntegerField(validators=[MaxValueValidator(9), MinValueValidator(1)])

    class Meta:
        app_label = 'crohmi'
        default_related_name = 'readings'

    def __str__(self):
        return f'{self.created_at} - {self.node_id}'


class SatelliteImage(models.Model):
    """Satellite Image model"""

    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    month = models.PositiveSmallIntegerField(unique=True)
    file_preprocessed = models.ImageField(upload_to=upload_file)
    file = models.FileField(upload_to=upload_file, blank=True, null=True)

    class Meta:
        app_label = 'crohmi'
        default_related_name = 'satellite_images'

    def __str__(self):
        return f'Satellite Image: {self.month}'

class UserLogin(models.Model):
    """User Image model"""

    id = models.UUIDField(default=uuid4, primary_key=True, editable=False)
    email = models.CharField(unique=True,max_length=255)
    password = models.CharField(max_length=255)
    is_superuser = models.BooleanField(default=False)

    class Meta:
        app_label = 'crohmi'
        default_related_name = 'user'

    def __str__(self):
        return f'User: {self.created_at}'

class Member(models.Model):
    """Member model"""

    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)
    name = models.CharField(max_length=255)
    image = models.FileField(upload_to=upload_file)
    order = models.PositiveSmallIntegerField()
    description = models.TextField()

    class Meta:
        app_label = 'lab_website'
        default_related_name = 'members'

    def __str__(self):
        return self.name


class MemberAction(models.Model):
    """Member Action model"""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=255)
    link = models.TextField()

    member = models.ForeignKey(Member, on_delete=models.CASCADE)

    class Meta:
        app_label = 'lab_website'
        default_related_name = 'member_actions'

    def __str__(self):
        return f'{self.member.name} - {self.name}'


class Project(models.Model):
    """Project model"""

    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=255)
    image = models.FileField(upload_to=upload_file)
    description = models.TextField()

    class Meta:
        app_label = 'lab_website'
        default_related_name = 'projects'

    def __str__(self):
        return self.name


class DataMigration(models.Model):
    """Data Migration model"""
    id = models.UUIDField(primary_key=True, editable=False, default=uuid4)

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to=upload_file)

    class Meta:
        app_label = 'core'
        default_related_name = 'data_migrations'

    def __str__(self):
        return self.name
