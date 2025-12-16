import django_filters
from .models import MountainPass


class MountainPassFilter(django_filters.FilterSet):
    email = django_filters.CharFilter(field_name='user__email', lookup_expr='exact')

    class Meta:
        model = MountainPass
        fields = ['status', 'user__email']