from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView

from api.Views.CustomTokenObtainViewSet import CustomTokenObtainView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api/token/', CustomTokenObtainView.as_view(), name='custom_token_obtain'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
