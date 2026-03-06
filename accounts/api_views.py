from django.db import IntegrityError
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from common.exceptions import AuthenticationError, ConflictError, ValidationError

from .serializers import (
    LoginInputSerializer,
    RegisterInputSerializer,
    UserOutputSerializer,
)
from .services import AccountService


class RegisterAPIView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def post(self, request):
        serializer = RegisterInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = AccountService().register_user(**serializer.validated_data)
        except ConflictError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)
        except (ValidationError, IntegrityError) as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(UserOutputSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginAPIView(APIView):
    authentication_classes: list = []
    permission_classes: list = []

    def post(self, request):
        serializer = LoginInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = AccountService().login(**serializer.validated_data)
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
