from hashids import Hashids
from rest_framework import status
from rest_framework.response import Response


class PasswordHash():
    password = None

    class Meta:
        abstract: True

    def has_password(self, contrasena):
        hashids = Hashids(salt='contrasena_prueba', min_length=7)
        try:
            # Hasheamos el pk que introduce el usuario
            hashed_pk = hashids.encode(int(contrasena))
            return hashed_pk
        except ValueError:
            return Response("No se ha podido hashear la contraseña", status=status.HTTP_400_BAD_REQUEST)

    def __init__(self, password):
        self.password = password
