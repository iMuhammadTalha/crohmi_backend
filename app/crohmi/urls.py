from django.urls import path, include

from rest_framework.routers import Route

from app.urls import router
from . import views

app_name = 'crohmi'

router.routes += [
    # Agri D Map View Route
    Route(
        url=r'^crohmi{trailing_slash}agrid{trailing_slash}map{trailing_slash}$',
        mapping={
            'post': 'create_agrid_map'
        },
        name='agrid_map-view',
        detail=False,
        initkwargs={'suffix': 'View'}
    ),
    # NDVI Map View Route
    Route(
        url=r'^crohmi{trailing_slash}ndvi{trailing_slash}map{trailing_slash}$',
        mapping={
            'get': 'view_ndvi_map',
            'post': 'create_ndvi_map'
        },
        name='ndvi_map-view',
        detail=False,
        initkwargs={'suffix': 'View'}
    ),

    # NDVI Map Detail View Route
    Route(
        url=r'^crohmi{trailing_slash}ndvi{trailing_slash}map{trailing_slash}'
            r'{lookup}{trailing_slash}$',
        mapping={
            'get': 'view_ndvi_map_by_id',
            'patch': 'update_ndvi_map_by_id',
            'delete': 'destroy_ndvi_map_by_id'
        },
        name='ndvi_map-detail',
        detail=False,
        initkwargs={'suffix': 'Detail'}
    ),

    # Reading View Route
    Route(
        url=r'^crohmi{trailing_slash}reading{trailing_slash}$',
        mapping={
            'get': 'view_reading',
        },
        name='reading-view',
        detail=False,
        initkwargs={'suffix': 'View'}
    ),

    # Air Reading View Route
    Route(
        url=r'^crohmi{trailing_slash}air{trailing_slash}reading'
            r'{trailing_slash}$',
        mapping={
            'get': 'view_air_reading',
            'post': 'create_air_reading',
        },
        name='air_reading-view',
        detail=False,
        initkwargs={'suffix': 'View'}
    ),

    # Satellite Image View Route
    Route(
        url=r'^crohmi{trailing_slash}satellite{trailing_slash}image'
            r'{trailing_slash}$',
        mapping={
            'get': 'view_satellite_image'
        },
        name='satellite_image-view',
        detail=False,
        initkwargs={'suffix': 'View'}
    ),

        # User View Route
    Route(
        url=r'^crohmi{trailing_slash}user{trailing_slash}$',
        mapping={
            'get': 'login_user',
            'post': 'create_user'
        },
        name='user-view',
        detail=False,
        initkwargs={'suffix': 'View'}
    )
]

router.register('crohmi', views.NdviMapViewSet)
router.register('crohmi', views.NdviMapDetailViewSet)
router.register('crohmi', views.ReadingViewSet)
router.register('crohmi', views.AirReadingViewSet)
router.register('crohmi', views.SatelliteImageViewSet)
router.register('crohmi', views.UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
