from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .Views.FacturaViewSet import FacturaViewSet
from .Views.UserViewSet import UserViewSet

# Definimos los modelos y rutas que vamos a utilizar

'''
    Gracias a DefaultRouter no es necesario definir las rutas de forma manual
'''
router = DefaultRouter()

router.register(r'usuarios', UserViewSet)
router.register(r'facturas', FacturaViewSet)

# Incluimos las rutas generadas por el enrutador en las URLs
urlpatterns = [
    path('', include(router.urls)),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)