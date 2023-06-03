from rest_framework import serializers

from core.models import Member, MemberAction, Project


class MemberSerializer(serializers.ModelSerializer):
    """Serializer for Member model"""

    actions = serializers.SerializerMethodField('get_actions')

    def get_actions(self, obj):
        """Return actions"""
        return MemberActionSerializer(obj.member_actions.all(), many=True).data

    class Meta:
        model = Member
        fields = ('id', 'name', 'image', 'description', 'actions')
        read_only_fields = ('id', )


class MemberActionSerializer(serializers.ModelSerializer):
    """Serializer for Member Action model"""

    class Meta:
        model = MemberAction
        fields = ('id', 'name', 'link')
        read_only_fields = ('id', )


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for Project Model"""

    class Meta:
        model = Project
        fields = ('id', 'name', 'image', 'description')
        read_only_fields = ('id', )
