from django.db import models
from rest_framework.exceptions import ValidationError

from ..models import User

'''
    Creacion de el modelo de Facturas con sus respectivas relaciones
'''

class Factura(models.Model):
    imagen = models.ImageField(upload_to='imagenes', blank=True, null=True)
    fecha = models.DateField(blank=False, null=False, auto_now_add=True) # Se crea automáticamente la fecha
    total = models.FloatField(blank=False, null=False)
    # A continuacion creamos una relacion foránea y dejamos el campo facturas en el modelos de User
    usuarios = models.ForeignKey(User, on_delete=models.CASCADE, related_name='facturas')

    def clean(self):
        content = [self.total]

        # Realizamos un contro de que tanto total como fecha no estén vacios
        if any(not valor for valor in content):
            raise ValidationError("Todos los campos deben de estar rellenos")

        if self.imagen:
            self.validate_image_format(self.imagen)

    def validate_image_format(value):
        """
        Validamos que el archivo de imagen tenga una extensión permitida (.jpeg o .png).
        """
        valid_extensions = ['.png']
        extension = value.name.split('.')[-1].lower()
        if f'.{extension}' not in valid_extensions:
            raise ValidationError(f"El archivo debe ser una imagen con extensión {', '.join(valid_extensions)}.")
        return value

    def __str__(self):
        return self.total

