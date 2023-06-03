from django.core.files.images import ImageFile
from django.utils import timezone

from rest_framework import viewsets, status, mixins
from rest_framework.response import Response

from core.models import NdviMap, Reading, SatelliteImage, UserLogin
from . import ndvi_algorithm
from . import serializers
# from . import resnet_algorithm

# import torch
import torch

model = torch.load("/app/crohmi/resnet_test_model_new.pt",map_location=torch.device('cpu'))
model.eval()

class NdviMapViewSet(viewsets.GenericViewSet,
                     mixins.CreateModelMixin):
    """View set for Ndvi Map"""

    authentication_classes = []

    permission_classes = []

    serializer_class = serializers.NdviMapSerializer

    queryset = NdviMap.objects.all()

    def get_queryset(self):
        """Order queryset"""
        queryset = super(NdviMapViewSet, self).get_queryset(). \
            order_by('-created_at').all()
        distinct = self.request.GET.get('distinct', None)
        if distinct is not None:
            if distinct == 'month':
                months = set(queryset.values_list(distinct, flat=True))
                distinct_months = []
                for month in months:
                    distinct_months.append(queryset.filter(
                        month=month
                    ).first())
                queryset = queryset.filter(
                    id__in=[obj.id for obj in distinct_months]
                ).all()
        return queryset

    def view_ndvi_map(self, request, *args, **kwargs):
        """Return all objects"""
        serializer = self.get_serializer(
            self.get_queryset(), many=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create_ndvi_map(self, request, *args, **kwargs):
        """Create and run algorithm"""
        serializer = self.create(request, *args, **kwargs)
        ndvi_map = serializer.save()

        # Get np array
        ndvi_array = ndvi_algorithm.ndvi_array_calc(ndvi_map.nri_image)

        # Calc ndvi image
        ndvi_image = ImageFile(ndvi_algorithm.ndvi_image(ndvi_map.nri_image,
                                                         ndvi_array,
                                                         ndvi_map.month,
                                                         ndvi_map.year))
        ndvi_map.ndvi_image.save(f'{ndvi_map.id}_ndvi_map.png', ndvi_image)

        # Calc health map
        health_map = ImageFile(ndvi_algorithm.health_image(ndvi_array,
                                                           ndvi_map.month,
                                                           ndvi_map.year))
        ndvi_map.health_map.save(f'{ndvi_map.id}_health_map.png', health_map)

        # Return response
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED,
                        headers=headers)

    def create_agrid_map(self, request, *args, **kwargs):
        """Create and run algorithm"""
        serializer = self.create(request, *args, **kwargs)
        agrid_map = serializer.save()

        predict = model(agrid_map.image.path)

        pred = torch.max(predict.data,1)
        values,indices = pred
        if indices == 0:
            a = "HEALTHY"
        elif indices == 1:
            a = "RESISTANT"
        elif indices == 2:
            a = "SUSCEPTIBLE"

         # Return response
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, result=a,
                        headers=headers)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return serializer


class NdviMapDetailViewSet(viewsets.GenericViewSet,
                           mixins.RetrieveModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.DestroyModelMixin):
    """Detail view set for NdviMap"""

    authentication_classes = []

    permission_classes = []

    serializer_class = serializers.NdviMapSerializer

    queryset = NdviMap.objects.all()

    def view_ndvi_map_by_id(self, request, *args, **kwargs):
        """Wrapper around retrieve method for view set distinction"""
        return self.retrieve(request, *args, **kwargs)

    def update_ndvi_map_by_id(self, request, *args, **kwargs):
        """Wrapper around update method for view set distinction"""
        return self.partial_update(request, *args, **kwargs)

    def destroy_ndvi_map_by_id(self, request, *args, **kwargs):
        """Wrapper around destroy method for view set distinction"""
        return self.destroy(request, *args, **kwargs)


class ReadingViewSet(viewsets.GenericViewSet):
    """View Set for Reading model"""

    authentication_classes = []

    permission_classes = []

    serializer_class = serializers.ReadingSerializer

    queryset = Reading.objects.all()

    def get_last_x(self, start_date, end_date, timedelta, points, node=None):
        """Get last x records"""
        queryset = self.get_queryset()
        if not (node is None or node == 'all'):
            queryset = queryset.filter(
                node_id=node
            ).all()

        queryset = queryset.filter(
            timestamp__range=(start_date, end_date)
        ).order_by('timestamp').all()

        start_interval = queryset.first().timestamp
        end_interval = start_interval + timedelta

        groups = []

        for counter in range(points):
            interval_queryset = queryset.filter(
                timestamp__range=(start_interval, end_interval)
            ).all()

            if interval_queryset.count() == 0:
                start_interval = end_interval
                end_interval = start_interval + timedelta
                continue

            groups.append(interval_queryset)

            start_interval = end_interval
            end_interval = start_interval + timedelta

        return groups

    def view_reading(self, request, *args, **kwargs):
        """Return readings based on query parameters"""
        action = self.request.GET.get('action', None)

        if action is not None:
            if action == 'last_seven_days':
                
                selected_date = request.GET.get('selectedDate', None)
                if selected_date is not None:
                    selected_date = timezone.datetime.strptime(
                        selected_date, '%Y-%m-%d'
                    )
                    end_date = selected_date
                else :
                    end_date = timezone.now()

                # end_date = timezone.now()
                start_date = end_date - timezone.timedelta(days=7)

                queryset = self.get_queryset().filter(
                    timestamp__range=(start_date, end_date)
                ).filter(
                    soil_moisture__range=(0, 101)
                ).filter(
                    soil_temperature__range=(0, 51)
                ).order_by('timestamp').all()

                start_interval = queryset.first().timestamp
                end_interval = start_interval + timezone.timedelta(hours=1)

                groups = []

                for counter in range(48):
                    interval_queryset = queryset.filter(
                        timestamp__range=(start_interval, end_interval)
                    ).filter(
                        soil_moisture__range=(0, 101)
                    ).filter(
                        soil_temperature__range=(0, 51)
                    ).all()
                    if interval_queryset.count() == 0:
                        start_interval = end_interval
                        end_interval = start_interval + timezone.timedelta(
                            hours=1
                        )
                        continue
                    groups.append(interval_queryset)

                    start_interval = end_interval
                    end_interval = start_interval + timezone.timedelta(
                        hours=1
                    )

                serializer = serializers.LastSevenDaysActionSerializer(
                    groups, many=True
                )
                return Response(serializer.data, status=status.HTTP_200_OK)
            elif action == 'last_day':
                
                selected_date = request.GET.get('selectedDate', None)
                if selected_date is not None:
                    selected_date = timezone.datetime.strptime(
                        selected_date, '%Y-%m-%d'
                    )
                    end_date = selected_date
                else :
                    end_date = timezone.now()
                    
                # end_date = timezone.now()
                start_date = end_date - timezone.timedelta(days=1)

                queryset = self.get_queryset().filter(
                    timestamp__range=(start_date, end_date)
                ).filter(
                    soil_moisture__range=(0, 101)
                ).filter(
                    soil_temperature__range=(0, 51)
                ).order_by('timestamp').all()

                start_interval = queryset.first().timestamp
                end_interval = start_interval + timezone.timedelta(hours=1)

                groups = []

                for counter in range(24):
                    interval_queryset = queryset.filter(
                        timestamp__range=(start_interval, end_interval)
                    ).filter(
                        soil_moisture__range=(0, 101)
                    ).filter(
                        soil_temperature__range=(0, 51)
                    ).all()
                    if interval_queryset.count() == 0:
                        start_interval = end_interval
                        end_interval = start_interval + timezone.timedelta(
                            hours=1
                        )
                        continue
                    groups.append(interval_queryset)

                    start_interval = end_interval
                    end_interval = start_interval + timezone.timedelta(
                        hours=1
                    )

                serializer = serializers.LastSevenDaysActionSerializer(
                    groups, many=True
                )
                return Response(serializer.data, status=status.HTTP_200_OK)
            elif action == 'node':
                queryset = self.get_queryset()
                node = request.GET.get('node', None)

                if node is not None:
                    queryset = queryset.filter(
                        node_id=node
                    ).filter(
                        soil_moisture__range=(0, 101)
                    ).filter(
                        soil_temperature__range=(0, 51)
                    ).order_by('-timestamp').all()[:100:-1]

                serializer = self.get_serializer(
                    queryset, many=True
                )

                return Response(serializer.data, status=status.HTTP_200_OK)
            elif action == 'last_thirty_days':
                node_1 = request.GET.get('node1', None)
                node_2 = request.GET.get('node2', None)
                selected_date = request.GET.get('selectedDate', None)
                if selected_date is not None:
                    selected_date = timezone.datetime.strptime(
                        selected_date, '%Y-%m-%d'
                    )
                    end_date = selected_date
                else :
                    end_date = timezone.now()
                

                #end_date = selected_date
                start_date = end_date - timezone.timedelta(days=30)

                groups_1 = self.get_last_x(
                    start_date, end_date, timezone.timedelta(days=1), 30, node=node_1
                )
                groups_2 = self.get_last_x(
                    start_date, end_date, timezone.timedelta(days=1), 30, node=node_2
                )

                serializer_1 = serializers.LastSevenDaysActionSerializer(
                    groups_1, many=True
                )
                serializer_2 = serializers.LastSevenDaysActionSerializer(
                    groups_2, many=True
                )
                return Response([serializer_1.data, serializer_2.data],
                                status=status.HTTP_200_OK)
            elif action == 'last_three_months':
                node_1 = request.GET.get('node1', None)
                node_2 = request.GET.get('node2', None)
                selected_date = request.GET.get('selectedDate', None)
                if selected_date is not None:
                    selected_date = timezone.datetime.strptime(
                        selected_date, '%Y-%m-%d'
                    )
                    end_date = selected_date
                else :
                    end_date = timezone.now()
                
                # end_date = timezone.now()
                start_date = end_date - timezone.timedelta(days=90)

                groups_1 = self.get_last_x(
                    start_date, end_date, timezone.timedelta(days=10), 30, node=node_1
                )
                groups_2 = self.get_last_x(
                    start_date, end_date, timezone.timedelta(days=10), 30, node=node_2
                )

                serializer_1 = serializers.LastSevenDaysActionSerializer(
                    groups_1, many=True
                )
                serializer_2 = serializers.LastSevenDaysActionSerializer(
                    groups_2, many=True
                )
                return Response([serializer_1.data, serializer_2.data],
                                status=status.HTTP_200_OK)
            elif action == 'table-view':
                start_date = request.GET.get('start_date', None)
                if start_date is not None:
                    start_date = timezone.datetime.strptime(
                        start_date, '%Y-%m-%d'
                    )
                end_date = request.GET.get('end_date', None)
                if end_date is not None:
                    end_date = timezone.datetime.strptime(
                        end_date, '%Y-%m-%d'
                    )

                if start_date and end_date is not None:
                    end_date = end_date + timezone.timedelta(days=1)    # To include end_date data also
                    serializer = self.get_serializer(
                        self.get_queryset().filter(
                            timestamp__range=(start_date, end_date)
                        ).filter(
                            soil_moisture__range=(0, 101)
                        ).filter(
                            soil_temperature__range=(1, 51)
                        ).order_by('-timestamp', 'node_id').all(), many=True
                    )
                    return Response(serializer.data, status=status.HTTP_200_OK)


class AirReadingViewSet(viewsets.GenericViewSet,
                        mixins.CreateModelMixin):
    """View set for Air Reading model"""

    authentication_classes = []

    permission_classes = []

    serializer_class = serializers.AirReadingSerializer

    queryset = Reading.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.AirReadingPostSerializer
        return super(AirReadingViewSet, self).get_serializer_class()

    def get_queryset(self):
        """Enforce filters"""
        queryset = super(AirReadingViewSet, self).get_queryset()
        start_date = self.request.GET.get('start_date', None)
        if start_date is not None:
            start_date = timezone.datetime.strptime(
                start_date, '%Y-%m-%d'
            )

        end_date = self.request.GET.get('end_date', None)
        if end_date is not None:
            end_date = timezone.datetime.strptime(
                end_date, '%Y-%m-%d'
            )

        if start_date is not None and end_date is not None:
            end_date = end_date + timezone.timedelta(days=1)    # To include end_date data also
            queryset = queryset.filter(
                timestamp__range=(start_date, end_date)
            ).all()

        return queryset

    def view_air_reading(self, request, *args, **kwargs):
        """Return all air readings"""
        start_date = request.GET.get('start_date', None)
        if start_date is not None:
            start_date = timezone.datetime.strptime(
                start_date, '%Y-%m-%d'
            )
        end_date = request.GET.get('end_date', None)
        if end_date is not None:
            end_date = timezone.datetime.strptime(
                end_date, '%Y-%m-%d'
            )
        if start_date and end_date is not None:
            end_date = end_date + timezone.timedelta(days=1)    # To include end_date data also
            serializer = self.get_serializer(
                self.get_queryset().filter(
                    timestamp__range=(start_date, end_date)
                ).filter(
                    node_id='1'
                ).order_by('-timestamp', 'node_id').all(), many=True
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        # serializer = self.get_serializer(
        #     self.get_queryset(), many=True
        # )

    def create_air_reading(self, request, *args, **kwargs):
        """Wrapper around create method for view set distinction"""
        return self.create(request, *args, **kwargs)


class SatelliteImageViewSet(viewsets.GenericViewSet):
    """View set for Satellite Image model"""

    authentication_classes = []

    permission_classes = []

    queryset = SatelliteImage.objects.all()

    serializer_class = serializers.SatelliteImageSerializer

    def view_satellite_image(self, request, *args, **kwargs):
        """Return all satellite images"""
        serializer = self.get_serializer(
            self.get_queryset().order_by('month').all(), many=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)



class UserViewSet(viewsets.GenericViewSet,
                        mixins.CreateModelMixin):
    """View set for User model"""

    authentication_classes = []

    permission_classes = []

    serializer_class = serializers.UserReadingSerializer

    queryset = UserLogin.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.UserPostSerializer
        return super(UserViewSet, self).get_serializer_class()

    def get_queryset(self):
        """Enforce filters"""
        queryset = super(UserViewSet, self).get_queryset()
        email = self.request.GET.get('email', None)
        password = self.request.GET.get('password', None)
        
        if email is not None and password is not None:
            queryset = queryset.filter(
                email=email
            ).filter(
                password=password
            ).all()

        return queryset

    def login_user(self, request, *args, **kwargs):
        """Return all air readings"""
        email = request.GET.get('email', None)
        password = request.GET.get('password', None)
        
        if email and password is not None:
            serializer = self.get_serializer(
                self.get_queryset().filter(
                    email=email
                ).filter(
                    password=password
                ).all(), many=True
            )
            return Response(serializer.data, status=status.HTTP_200_OK)

    def create_user(self, request, *args, **kwargs):
        """Wrapper around create method for view set distinction"""
        return self.create(request, *args, **kwargs)