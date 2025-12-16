from django.urls import path, include, re_path
from rest_framework.routers import DefaultRouter
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .views import MountainPassViewSet, UserPassesListView

router = DefaultRouter()
router.register(r'submitData', MountainPassViewSet, basename='mountainpass')

schema_view = get_schema_view(
    openapi.Info(
        title="Mountain Passes API",
        default_version='v1',
        description="API для сбора и модерации данных о горных перевалах",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # API endpoints
    path('', include(router.urls)),
    path('submitData/user_passes/', UserPassesListView.as_view(), name='user-passes'),

    # Swagger documentation
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0),
            name='schema-json'),
    path('swagger/',
         schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),
    path('redoc/',
         schema_view.with_ui('redoc', cache_timeout=0),
         name='schema-redoc'),
]