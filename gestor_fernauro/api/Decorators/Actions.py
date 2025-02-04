# mixins.py
import os

from django.conf import settings
from hashid_field import hashid
from hashids import Hashids
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from ..models import User
from ..Models.FacturaModel import Factura
from ..Serializers.FacturaSerializer import FacturaSerializer
from ..Serializers.UserSerializer import UserSerializer
from ..tasks import registrar_log


from ..AbstractClass.HashPass import PasswordHash
# Clase donde dejamos registrados los decoradores que vamos a utilizar
class UserDecorator(PasswordHash):

    # Decorador separado de el view
    @action(detail=False, methods=['get'])
    def pageable(self, request):
        cantidad_usuarios = request.query_params.get('cantidad', 3)

        # A continuacion llamamos a un método que permite registrar y devolver los usuarios desde el log
        return self.obtener_usuarios_por_cantidad(cantidad_usuarios, request)

    # Funcion para obtener usuarios por cantidad
    def obtener_usuarios_por_cantidad(self, cantidad_usuarios, request):
        try:
            cantidad_usuarios = int(cantidad_usuarios)
        except ValueError:
            cantidad_usuarios = 3

        usuarios_filtrados = User.objects.all().order_by('-id')[:cantidad_usuarios]
        usuarios_filtrados_data = UserSerializer(usuarios_filtrados, many=True).data

        # Registrar log de usuarios obtenidos
        registrar_log.delay(usuarios_filtrados_data)

        serializer = UserSerializer(usuarios_filtrados, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    '''
        Obtención de un cliente en funcion de su id
    '''
    @action(detail=True, methods=['get'])
    def get_cliente(self, request, pk=None):
        try:
            # Hasheamos el pk que introduce el usuario en funcion de el metodo definido en la clase Abstracta
            hashed_pk = super().has_password(pk)

            # Obtenemos el usuario en funcion de la pk introducida y hasheada
            user = User.objects.get(id=hashed_pk)
        except User.DoesNotExist:
            return Response("El usuario no existe", status=status.HTTP_404_NOT_FOUND)
        except ValueError:
            return Response("ID inválido", status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(f"Error: {str(e)}", status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer = UserSerializer(user, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

class FacturaDecorator():

    # Decorador para añadir imágenes a una factura
    @action(detail=False, methods=['post'])
    def anadir_imagen(self, request):
        try:
            factura_id = int(request.data.get('id'))
        except (ValueError, TypeError):
            return Response("El id proporcionado no es válido", status=status.HTTP_400_BAD_REQUEST)

        content = {
            'id': factura_id,
            'imagen': request.FILES.get('imagen')
        }

        # Comprobamos que se han introducido los campos obligatorios
        if not all(content.values()):
            return Response("Todos los campos deben de estar rellenos",
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            # Obtenemos la factura
            factura = Factura.objects.get(id=content['id'])
        except Factura.DoesNotExist:
            return Response("La factura no existe", status=status.HTTP_404_NOT_FOUND)

        imagen = content['imagen']
        imagen.name = os.path.basename(imagen.name)

        # Asignamos la imagen y guardamos la factura
        factura.imagen = imagen
        factura.save()

        serializer = FacturaSerializer(factura)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Obtenemos las facturas sin imágenes
    @action(detail=False, methods=['get'])
    def sin_imagenes(self, request):
        facturas = Factura.objects.filter(imagen__isnull=True)

        if not facturas.exists():
            return Response("No hay facturas sin imágenes", status=status.HTTP_404_NOT_FOUND)

        serializer = FacturaSerializer(facturas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Obtenemos las facturas con imágenes
    @action(detail=False, methods=['get'])
    def con_imagenes(self, request):
        facturas = Factura.objects.filter(imagen__isnull=False)

        if not facturas.exists():
            return Response("No hay facturas con imágenes", status=status.HTTP_404_NOT_FOUND)

        serializer = FacturaSerializer(facturas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Eliminamos la imagen de una factura
    @action(detail=False, methods=['delete'])
    def eliminar_imagenes(self,request):
        nombre_imagen = request.data.get('imagen')
        imagen_path = os.path.join(settings.MEDIA_ROOT, 'imagenes',nombre_imagen)

        if os.path.exists(imagen_path):
            os.remove(imagen_path)
            return Response("Imagen eliminada", status=status.HTTP_200_OK)
        else:
            return Response("La imagen no existe", status=status.HTTP_404_NOT_FOUND)