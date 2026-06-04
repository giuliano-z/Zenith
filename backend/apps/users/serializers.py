"""Contratos de entrada/salida del módulo AUTH (capa de aplicación).

Los serializers validan formato y delegan la lógica de negocio en services.py.
"""
from rest_framework import serializers

from apps.users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Representación pública de un usuario (output). Nunca expone la contraseña."""

    class Meta:
        model = User
        fields = ("id", "email", "name", "date_joined")
        read_only_fields = fields


class RegisterSerializer(serializers.Serializer):
    """Entrada de RF-001. La validación de fortaleza de password vive en services."""

    email = serializers.EmailField()
    name = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, style={"input_type": "password"})


class LoginSerializer(serializers.Serializer):
    """Entrada de RF-002."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, style={"input_type": "password"})
