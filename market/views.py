from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.exceptions import NotFoundError, PermissionDeniedError, ValidationError

from .api.serializers import PedidoOutputSerializer
from .services import AcceptOrderService


class PedidoAceptarAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pedido_id: int):
        try:
            pedido = AcceptOrderService.accept_order(user=request.user, pedido_id=pedido_id)
        except NotFoundError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except PermissionDeniedError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        except ValidationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(PedidoOutputSerializer(pedido).data, status=status.HTTP_200_OK)
