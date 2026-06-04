"""Endpoints HTTP del módulo AUTH (capa de presentación).

Las vistas solo orquestan: validan entrada con serializers, delegan la lógica en
services.py y devuelven la respuesta. RegisterView y LoginView son públicas;
LogoutView (heredada de Knox) requiere token válido.
"""
from knox.views import LoginView as KnoxLoginView
from knox.views import LogoutAllView as KnoxLogoutAllView
from knox.views import LogoutView as KnoxLogoutView
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users import services
from apps.users.serializers import LoginSerializer, RegisterSerializer, UserSerializer


class RegisterView(APIView):
    """RF-001: registra un usuario con email, nombre y contraseña. Público."""

    authentication_classes = ()
    permission_classes = (AllowAny,)

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            user = services.create_user(
                email=data["email"], name=data["name"], password=data["password"]
            )
        except services.EmailAlreadyExistsError:
            return Response(
                {"email": ["Ya existe un usuario con ese email."]},
                status=status.HTTP_409_CONFLICT,
            )
        except services.DjangoValidationError as exc:
            return Response({"password": exc.messages}, status=status.HTTP_400_BAD_REQUEST)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginView(KnoxLoginView):
    """RF-002: autentica por email + contraseña y emite un token Knox (TTL 24h). Público."""

    authentication_classes = ()
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            user = services.authenticate_user(email=data["email"], password=data["password"])
        except services.InvalidCredentialsError:
            return Response(
                {"detail": "Credenciales inválidas."}, status=status.HTTP_401_UNAUTHORIZED
            )
        # Knox crea el token a partir de request.user; lo seteamos manualmente.
        request.user = user
        return super().post(request, format=format)


class LogoutView(KnoxLogoutView):
    """RF-003: invalida el token actual. Cualquier request posterior con él → 401."""


class LogoutAllView(KnoxLogoutAllView):
    """Invalida todos los tokens del usuario (cierre de todas las sesiones)."""
