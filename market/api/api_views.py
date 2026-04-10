from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.exceptions import NotFoundError, PermissionDeniedError, ValidationError

from .serializers import (
    PedidoCreateInputSerializer,
    PublicacionCreateInputSerializer,
    PublicacionNearbyQuerySerializer,
    PublicacionUpdateInputSerializer,
    PedidoOutputSerializer,
    PublicacionOutputSerializer,
)
from ..domain.services import AcceptOrderService, CatalogService, OrderService


class PublicacionListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        publicaciones = CatalogService().list_publicaciones()
        return Response(
            PublicacionOutputSerializer(publicaciones, many=True).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = PublicacionCreateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            publicacion = CatalogService().create_publicacion(
                user=request.user,
                **serializer.validated_data,
            )
        except ValidationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(PublicacionOutputSerializer(publicacion).data, status=status.HTTP_201_CREATED)


class PublicacionNearbyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = PublicacionNearbyQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        try:
            publicaciones = CatalogService().list_publicaciones_cercanas(
                **serializer.validated_data,
            )
        except ValidationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(
            PublicacionOutputSerializer(publicaciones, many=True).data,
            status=status.HTTP_200_OK,
        )


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


class PedidoDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pedido_id: int):
        try:
            pedido = OrderService().get_order_for_user(user=request.user, pedido_id=pedido_id)
        except NotFoundError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        return Response(PedidoOutputSerializer(pedido).data, status=status.HTTP_200_OK)


class PedidoMarkDeliveredAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pedido_id: int):
        try:
            pedido = OrderService().mark_order_delivered(user=request.user, pedido_id=pedido_id)
        except NotFoundError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(PedidoOutputSerializer(pedido).data, status=status.HTTP_200_OK)


class MisPedidosAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        pedidos = (
            OrderService()
            .list_orders_for_user(user=request.user)
        )
        return Response(PedidoOutputSerializer(pedidos, many=True).data, status=status.HTTP_200_OK)


class MisPublicacionesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        publicaciones = CatalogService().list_publicaciones_for_user(user=request.user)
        publicaciones_data = PublicacionOutputSerializer(publicaciones, many=True).data
        saldo_disponible = round(sum(float(item.get("saldo_generado") or 0) for item in publicaciones_data), 2)
        total_unidades_vendidas = sum(int(item.get("total_vendido") or 0) for item in publicaciones_data)
        return Response(
            {
                "saldo_disponible": saldo_disponible,
                "total_unidades_vendidas": total_unidades_vendidas,
                "publicaciones": publicaciones_data,
            },
            status=status.HTTP_200_OK,
        )


class PublicacionDetailUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, publicacion_id: int):
        serializer = PublicacionUpdateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            publicacion = CatalogService().update_publicacion(
                user=request.user,
                publicacion_id=publicacion_id,
                **serializer.validated_data,
            )
        except NotFoundError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except PermissionDeniedError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        except ValidationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(PublicacionOutputSerializer(publicacion).data, status=status.HTTP_200_OK)

    def delete(self, request, publicacion_id: int):
        try:
            CatalogService().delete_publicacion(user=request.user, publicacion_id=publicacion_id)
        except NotFoundError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except PermissionDeniedError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        return Response(status=status.HTTP_204_NO_CONTENT)


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

