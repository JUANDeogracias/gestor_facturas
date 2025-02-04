from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.core.exceptions import ValidationError
from django.db import models
from hashid_field import HashidAutoField


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El correo electrónico es obligatorio.')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El superusuario debe tener is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El superusuario debe tener is_superuser=True.')


        return self.create_user(email, password,**extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    id = HashidAutoField(primary_key=True, salt='contrasena_prueba')
    email = models.EmailField(unique=True, blank=False, null=False)
    nombre = models.CharField(max_length=30, blank=True)
    apellidos = models.CharField(max_length=30, blank=True)
    role = models.CharField(max_length=10, default='user')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    # Necesario para el login el campo email
    USERNAME_FIELD = 'email'

    # Campos obligatorios para crear un superusuario/administrador
    REQUIRED_FIELDS = ['nombre', 'role']

    def __str__(self):
        return self.email