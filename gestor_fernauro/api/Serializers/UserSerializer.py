from hashid_field.rest import HashidSerializerCharField
from rest_framework import serializers

from ..models import User


class UserSerializer(serializers.ModelSerializer):
    id = HashidSerializerCharField(source_field='api.User.id', salt="contrasena_prueba")

    class Meta:
        model = User
        fields = ['id','nombre','email', 'password','role']

    def validate_email(self, value):
        if not value:
            raise serializers.ValidationError("This field may not be blank.")
        return value