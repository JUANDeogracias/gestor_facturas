from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework_simplejwt.views import TokenRefreshView

from api.Views.CustomTokenObtainViewSet import CustomTokenObtainView

schema_view = get_schema_view(
    openapi.Info(
        title="Mi API",
        default_version='v1',
        description="Documentación de mi API",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@miapi.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=False,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api/token/', CustomTokenObtainView.as_view(), name='custom_token_obtain'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
