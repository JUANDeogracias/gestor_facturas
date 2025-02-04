from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from ..Models.FacturaModel import Factura


class FacturaSerializer(serializers.ModelSerializer):

    imagen = serializers.ImageField(use_url=True,required=False,allow_null=True)
    class Meta:
        model = Factura
        fields = ['imagen','fecha','total','usuarios']

    def validate_total(self, value):
        if not value:
            raise ValidationError("El campo total debe de estar relleno")
        return value

    '''
        Mediante esta funcion podemos hacer una validación de la imagen proporcionada de modo que comprobamos el tipo de
        formato que se proporciona y verificamos si es .jpeg o .png.
    '''
    def validate_imagen(self,value):
        """
        Valida que el archivo de imagen tenga una extensión permitida (.jpeg o .png).
        """
        valid_extensions = ['.jpeg', '.png']
        extension = value.name.split('.')[-1].lower()
        if f'.{extension}' not in valid_extensions:
            raise ValidationError(f"El archivo debe ser una imagen con extensión {', '.join(valid_extensions)}.")
        return value