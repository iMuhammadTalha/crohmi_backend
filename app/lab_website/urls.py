from django.urls import path, include

from rest_framework.routers import Route

from app.urls import router
from . import views

app_name = 'lab_website'

router.routes += [
    # Member View Route
    Route(
        url=r'^website{trailing_slash}member{trailing_slash}$',
        mapping={
            'get': 'view_member'
        },
        name='member-view',
        detail=False,
        initkwargs={'suffix': 'View'}
    ),

    # Project View Route
    Route(
        url=r'^website{trailing_slash}project{trailing_slash}$',
        mapping={
            'get': 'view_project',
        },
        name='project-view',
        detail=False,
        initkwargs={'suffix': 'View'}
    )
]

router.register('website', views.MemberViewSet)
router.register('website', views.ProjectViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
