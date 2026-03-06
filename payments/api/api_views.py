from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.exceptions import NotFoundError, ValidationError

from .serializers import PagoCreateInputSerializer, PagoOutputSerializer
from ..domain.services import PaymentService


class PagoCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PagoCreateInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            pago = PaymentService().register_payment(user=request.user, **serializer.validated_data)
        except NotFoundError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(PagoOutputSerializer(pago).data, status=status.HTTP_201_CREATED)

