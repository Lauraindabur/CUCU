from django.db import IntegrityError
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.exceptions import AuthenticationError, ConflictError, ValidationError

from ...application.use_cases import (
    GetUserProfileUseCase,
    LoginUserUseCase,
    RefreshAccessTokenUseCase,
    RegisterUserUseCase,
    RequestPasswordResetUseCase,
    ResetPasswordUseCase,
)
from ...infrastructure.auth import DjangoAuthService
from ...infrastructure.external_services import DjangoEmailService
from ...infrastructure.repositories_impl import DjangoUserRepository
from ..serializers.user_serializer import (
    LoginInputSerializer,
    PasswordResetConfirmInputSerializer,
    PasswordResetRequestInputSerializer,
    RegisterInputSerializer,
    TokenRefreshInputSerializer,
    UserOutputSerializer,
)


def _user_repository() -> DjangoUserRepository:
    return DjangoUserRepository()


def _auth_service() -> DjangoAuthService:
    return DjangoAuthService(user_repository=_user_repository())


def _email_service() -> DjangoEmailService:
    return DjangoEmailService()


class RegisterAPIView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def post(self, request):
        serializer = RegisterInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user_dto = RegisterUserUseCase(user_repository=_user_repository()).execute(**serializer.validated_data)
        except ConflictError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)
        except (ValidationError, IntegrityError) as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(UserOutputSerializer(user_dto).data, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def post(self, request):
        serializer = LoginInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = LoginUserUseCase(auth_service=_auth_service()).execute(**serializer.validated_data)
        except AuthenticationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(
            {
                "access": result.access,
                "refresh": result.refresh,
                "user": UserOutputSerializer(result.user).data,
            },
            status=status.HTTP_200_OK,
        )


class TokenRefreshAPIView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def post(self, request):
        serializer = TokenRefreshInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = RefreshAccessTokenUseCase(auth_service=_auth_service()).execute(**serializer.validated_data)
        return Response({"access": result.access}, status=status.HTTP_200_OK)


class PasswordResetRequestAPIView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def post(self, request):
        serializer = PasswordResetRequestInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            reset_url_base = request.build_absolute_uri("/ui/restablecer-password/")
            RequestPasswordResetUseCase(
                user_repository=_user_repository(),
                auth_service=_auth_service(),
                email_service=_email_service(),
            ).execute(email=serializer.validated_data["email"], reset_url_base=reset_url_base)
        except ValidationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {"detail": "Si el correo existe, enviamos un enlace para cambiar la contraseña."},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmAPIView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def post(self, request):
        serializer = PasswordResetConfirmInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user_dto = ResetPasswordUseCase(
                user_repository=_user_repository(),
                auth_service=_auth_service(),
            ).execute(**serializer.validated_data)
        except ValidationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "detail": "Contraseña actualizada correctamente.",
                "user": UserOutputSerializer(user_dto).data,
            },
            status=status.HTTP_200_OK,
        )


class MeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_dto = GetUserProfileUseCase().execute(user=request.user)
        return Response(UserOutputSerializer(user_dto).data, status=status.HTTP_200_OK)