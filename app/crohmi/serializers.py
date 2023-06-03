from django.db.models import Avg
from rest_framework import serializers

from core.models import NdviMap, Reading, SatelliteImage, UserLogin


class NdviMapSerializer(serializers.ModelSerializer):
    """Serializer for Ndvi Map model"""

    class Meta:
        model = NdviMap
        fields = ('id', 'nri_image', 'ndvi_image', 'health_map', 'created_at',
                  'month', 'year')
        read_only_fields = ('id', 'created_at')


class ReadingSerializer(serializers.ModelSerializer):
    """Serializer for Reading model"""

    class Meta:
        model = Reading
        fields = ('node_id', 'timestamp', 'air_temperature',
                  'air_moisture', 'soil_temperature', 'soil_moisture')


class AirReadingSerializer(serializers.ModelSerializer):
    """Serializer for Air Reading model"""

    class Meta:
        model = Reading
        fields = ('timestamp', 'node_id', 'nh3', 'co', 'c3h8', 'no2',
                  'c4h10', 'ch4', 'h2', 'c2h5oh',)


class AirReadingPostSerializer(serializers.ModelSerializer):
    """Serializer for creating Air Reading model"""

    class Meta:
        model = Reading
        fields = ('node_id', 'timestamp', 'air_temperature',
                  'air_moisture', 'soil_temperature', 'soil_moisture',
                  'timestamp', 'node_id', 'nh3', 'co', 'c3h8', 'no2',
                  'c4h10', 'ch4', 'h2', 'c2h5oh',
                  )


class LastSevenDaysActionSerializer(serializers.Serializer):
    """Serializer for Last Seven Days Action"""

    air_temperature = serializers.SerializerMethodField('get_air_temperature')
    air_moisture = serializers.SerializerMethodField('get_air_moisture')
    soil_temperature = serializers.SerializerMethodField('get_soil_'
                                                         'temperature')
    soil_moisture = serializers.SerializerMethodField('get_soil_moisture')
    datetime = serializers.SerializerMethodField('get_datetime')

    def get_datetime(self, obj):
        return obj.first().timestamp

    def get_air_temperature(self, obj):
        return obj.aggregate(avg=Avg('air_temperature'))['avg']

    def get_air_moisture(self, obj):
        return obj.aggregate(avg=Avg('air_moisture'))['avg']

    def get_soil_temperature(self, obj):
        return obj.aggregate(avg=Avg('soil_temperature'))['avg']

    def get_soil_moisture(self, obj):
        return obj.aggregate(avg=Avg('soil_moisture'))['avg']

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class SatelliteImageSerializer(serializers.ModelSerializer):
    """Serializer for Satellite Image model"""

    class Meta:
        model = SatelliteImage
        fields = ('id', 'month', 'file_preprocessed', 'file')
        read_only_fields = ('id',)


class UserReadingSerializer(serializers.ModelSerializer):
    """Serializer for Air Reading model"""

    class Meta:
        model = UserLogin
        fields = ('email', 'password', 'is_superuser'
                  )

class UserPostSerializer(serializers.ModelSerializer):
    """Serializer for creating Air Reading model"""

    class Meta:
        model = UserLogin
        fields = ('email', 'password', 'is_superuser'
                  )
