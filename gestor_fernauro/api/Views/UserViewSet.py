from django.core.cache import cache
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import Token

from ..Decorators.Actions import UserDecorator
from ..models import User
from ..Permissions.permissions import IsAdminUser, IsNormalUser
from ..Serializers.UserSerializer import UserSerializer
from ..tasks import enviar_email, ping, registrar_log


class UserViewSet(viewsets.ModelViewSet,
                  UserDecorator):

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsNormalUser]

    cache_key = ''

    # Funcion para devolver Responses y ahorrar y limpiar el codigo
    def responses(self, respuesta, codigo_estado):
        return Response(respuesta, status=codigo_estado)

    # Metodo para obtener usuarios ya predefinido por django
    def list(self, request, *args, **kwargs):
        # Intentar obtener usuarios desde la cache
        usuarios = cache.get(self.cache_key)

        if not usuarios:
            usuarios = User.objects.all()
            if not usuarios:
                return self.responses('No hay usuarios', status.HTTP_404_NOT_FOUND)

            # Serializamos los datos en formato json
            serializer = UserSerializer(usuarios, many=True)
            usuarios = serializer.data

            # Guardamos los datos en la cache durante 10 minutos
            cache.set(self.cache_key, usuarios, timeout=60 * 10)
            print("Guardamos los datos en la cache ")

        return self.responses({'exitoso': usuarios}, status.HTTP_200_OK)

    # Modificamos el metodo post que ya viene predefinido por django
    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['role'] = 'user'

        serializer = UserSerializer(data=data)
        serializer.is_valid(raise_exception=True)


        # Creamos un usuario con el rol de user forzando a que no sea superadministrador
        user = User.objects.create_user(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            nombre=serializer.validated_data['nombre'],
            role=serializer.validated_data['role']
        )

        cached_users = cache.get(self.cache_key)

        if cached_users:
            # Si hay datos en caché, agregamos el nuevo usuario sin hacer otra consulta a la BD
            cached_users.append(UserSerializer(user).data)
            cache.set(self.cache_key, cached_users, timeout=60 * 10)
            print("Cache actualizada con el nuevo usuario.")
        else:
            # Si la caché esta vacía, la regeneramos con todos los usuarios
            cache.set(self.cache_key, UserSerializer(User.objects.all(), many=True).data, timeout=60 * 10)
            print("Cache regenerada después de crear un usuario.")

        return Response(serializer.data, status=status.HTTP_201_CREATED)


















    # Metodo para obtener usuarios ordenados tanto por cantidad como por antiguedad (de más nuevos a más antiguos)
    '''
    @action(detail=False, methods=['get'])
    def pageable(self, request):
        cantidad_usuarios = request.query_params.get('cantidad', 3)

        # enviar_email.delay()
        try:
            cantidad_usuarios = int(cantidad_usuarios)
        except ValueError:
            cantidad_usuarios = 3

        # Filtramos por los usuarios más nuevos
        usuarios_filtrados = (User.objects.all()
                              .order_by('-id')[:cantidad_usuarios])

        usuarios_filtrados_data = UserSerializer(usuarios_filtrados, many=True).data

        registrar_log.delay(usuarios_filtrados_data)

        serializer = UserSerializer(usuarios_filtrados, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

        return self.responses(serializer.data, status.HTTP_200_OK)
    '''

