from rest_framework_simplejwt.tokens import RefreshToken


class CustomToken(RefreshToken):

    # Método para devolver un token personalizado
    @classmethod
    def for_user(cls,user):
        token = super().for_user(user)
        token['id'] = str(user.id)
        token['nombre'] = user.nombre
        token['email'] = user.email
        token['role'] = user.role
        return token

