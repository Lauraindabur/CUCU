from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.exceptions import ConflictError, NotFoundError, ValidationError

from ...application import GetUserNotificationsUseCase, MarkNotificationAsReadUseCase
from ..serializers.notification_serializer import NotificacionSerializer


class MarcarNotificacionLeidaView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        try:
            notificacion = MarkNotificationAsReadUseCase().execute(notification_id=id)
        except NotFoundError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ConflictError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)
        except ValidationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = NotificacionSerializer(notificacion)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MisNotificacionesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notificaciones = GetUserNotificationsUseCase().execute(usuario=request.user)
        serializer = NotificacionSerializer(notificaciones, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)