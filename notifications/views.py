from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .services import NotificacionService
from .api.serializers import NotificacionSerializer

class MarcarNotificacionLeidaView(APIView):

    def post(self, request, id):

        try:
            notificacion = NotificacionService.marcar_leida(id)

            serializer = NotificacionSerializer(notificacion)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

class MisNotificacionesView(APIView):

    def get(self, request):

        notificaciones = NotificacionService.obtener_usuario(request.user)

        serializer = NotificacionSerializer(notificaciones, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)