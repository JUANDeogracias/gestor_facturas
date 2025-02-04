import jwt
from django.conf import settings
from jwt import ExpiredSignatureError, InvalidTokenError
from rest_framework.permissions import BasePermission
from rest_framework_simplejwt.exceptions import InvalidToken
from rest_framework_simplejwt.tokens import UntypedToken


class IsNormalUser(BasePermission):

    def has_permission(self, request, view):
        # Verificamos si el usuario está autenticado
        if not request.user or not request.auth:
            return False

        # Obtenemos el token desde el encabezado de autorización
        token = request.auth

        # Aseguramos que el token esté en formato bytes
        if isinstance(token, str):
            token = token.encode('utf-8')

        # Comprobamos si el usuario está autenticado
        if token.get('role') == 'user' or token.get('role') == 'admin':
            return True

        return False

    '''
    
    @params: por implementar
    
    def verificar_firma_token(self, token):
        try:
            # Verificamos la firma del token usando la clave secreta
            jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            return True
        except jwt.InvalidTokenError as e:
            print(f"Error al decodificar el token: {str(e)}")
            return False
    '''

class IsAdminUser(BasePermission):

    def has_permission(self, request, view):
        # Verificamos si el usuario está autenticado

        if not request.user or not request.auth:
            return False

        # Obtenemos el contenido de el token
        token_data = request.auth

        # Comprobamos si el usuario esta autenticado como admin
        if token_data.get('role') == 'admin':
            return True

        return False