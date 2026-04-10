from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.exceptions import NotFoundError, PermissionDeniedError, ValidationError

from ...application.use_cases import (
    AcceptOrderUseCase,
    CreateOrderUseCase,
    CreatePublicacionUseCase,
    DeletePublicacionUseCase,
    GetOrderForUserUseCase,
    ListOrdersForUserUseCase,
    ListPublicacionesCercanasUseCase,
    ListPublicacionesForUserUseCase,
    ListPublicacionesUseCase,
    MarkOrderDeliveredUseCase,
    UpdatePublicacionUseCase,
)
from ..serializers.market_serializer import (
    PedidoCreateInputSerializer,
    PedidoOutputSerializer,
    PublicacionCreateInputSerializer,
    PublicacionNearbyQuerySerializer,
    PublicacionOutputSerializer,
    PublicacionUpdateInputSerializer,
)


class PublicacionListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        publicaciones = ListPublicacionesUseCase().execute()
        return Response(
            PublicacionOutputSerializer(publicaciones, many=True).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        serializer = PublicacionCreateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            publicacion = CreatePublicacionUseCase().execute(
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
            publicaciones = ListPublicacionesCercanasUseCase().execute(**serializer.validated_data)
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
            pedido = CreateOrderUseCase().execute(user=request.user, **serializer.validated_data)
        except NotFoundError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(PedidoOutputSerializer(pedido).data, status=status.HTTP_201_CREATED)


class PedidoDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pedido_id: int):
        try:
            pedido = GetOrderForUserUseCase().execute(user=request.user, pedido_id=pedido_id)
        except NotFoundError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        return Response(PedidoOutputSerializer(pedido).data, status=status.HTTP_200_OK)


class PedidoMarkDeliveredAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pedido_id: int):
        try:
            pedido = MarkOrderDeliveredUseCase().execute(user=request.user, pedido_id=pedido_id)
        except NotFoundError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(PedidoOutputSerializer(pedido).data, status=status.HTTP_200_OK)


class MisPedidosAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        pedidos = ListOrdersForUserUseCase().execute(user=request.user)
        return Response(PedidoOutputSerializer(pedidos, many=True).data, status=status.HTTP_200_OK)


class MisPublicacionesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        publicaciones = ListPublicacionesForUserUseCase().execute(user=request.user)
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
            publicacion = UpdatePublicacionUseCase().execute(
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
            DeletePublicacionUseCase().execute(user=request.user, publicacion_id=publicacion_id)
        except NotFoundError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except PermissionDeniedError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)

        return Response(status=status.HTTP_204_NO_CONTENT)


class PedidoAceptarAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pedido_id: int):
        try:
            pedido = AcceptOrderUseCase().execute(user=request.user, pedido_id=pedido_id)
        except NotFoundError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except PermissionDeniedError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        except ValidationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(PedidoOutputSerializer(pedido).data, status=status.HTTP_200_OK)