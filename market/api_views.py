from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.exceptions import NotFoundError, PermissionDeniedError, ValidationError
from .serializers import (
    PedidoCreateInputSerializer,
    PedidoOutputSerializer,
    PublicacionOutputSerializer,
)
from .services import AcceptOrderService, CatalogService, OrderService


class PedidoCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PedidoCreateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            pedido = OrderService().create_order(user=request.user, **serializer.validated_data)
        except NotFoundError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(PedidoOutputSerializer(pedido).data, status=status.HTTP_201_CREATED)


class PublicacionListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        publicaciones = CatalogService().list_publicaciones()
        return Response(
            PublicacionOutputSerializer(publicaciones, many=True).data,
            status=status.HTTP_200_OK,
        )


class PedidoDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pedido_id: int):
        try:
            pedido = OrderService().get_order_for_user(user=request.user, pedido_id=pedido_id)
        except NotFoundError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        return Response(PedidoOutputSerializer(pedido).data, status=status.HTTP_200_OK)


class PedidoAceptarAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pedido_id: int):
        try:
            pedido = AcceptOrderService().accept_order(user=request.user, pedido_id=pedido_id)
        except NotFoundError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except PermissionDeniedError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        except ValidationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(PedidoOutputSerializer(pedido).data, status=status.HTTP_200_OK)
