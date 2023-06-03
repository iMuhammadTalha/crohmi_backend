from rest_framework import viewsets, status
from rest_framework.response import Response

from core.models import Member, Project
from . import serializers


class MemberViewSet(viewsets.GenericViewSet):
    """View set for Member model"""

    authentication_classes = []

    permission_classes = []

    serializer_class = serializers.MemberSerializer

    queryset = Member.objects.all()

    def view_member(self, request, *args, **kwargs):
        """Return all members"""
        serializer = self.get_serializer(
            self.get_queryset().order_by('order').all(), many=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProjectViewSet(viewsets.GenericViewSet):
    """View set for Project model"""

    authentication_classes = []

    permission_classes = []

    serializer_class = serializers.ProjectSerializer

    queryset = Project.objects.all()

    def view_project(self, request, *args, **kwargs):
        """Return all projects"""
        serializer = self.get_serializer(
            self.get_queryset(), many=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)
