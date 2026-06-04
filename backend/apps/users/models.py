"""Modelo de dominio User (RF-001).

Identidad basada en email (sin username). La capa de dominio define la entidad
y su manager; la lógica de negocio de creación/autenticación vive en services.py.
"""
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    """Manager de User. Hashea la contraseña y normaliza el email."""

    use_in_migrations = True

    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError("El email es obligatorio.")
        if not name:
            raise ValueError("El nombre es obligatorio.")
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Un superusuario debe tener is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Un superusuario debe tener is_superuser=True.")
        return self.create_user(email, name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Usuario del sistema. Autenticación por email (RF-001, RF-002)."""

    email = models.EmailField("email", unique=True)
    name = models.CharField("nombre", max_length=150)
    is_active = models.BooleanField("activo", default=True)
    is_staff = models.BooleanField("staff", default=False)
    date_joined = models.DateTimeField("fecha de alta", auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"

    def __str__(self):
        return self.email
