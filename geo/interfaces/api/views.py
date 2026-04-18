from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from common.exceptions import ValidationError

from ...application import GeocodeAddressUseCase, GetRouteUseCase, SuggestAddressesUseCase
from ..serializers.geo_serializer import GeocodeQuerySerializer, GeocodeSuggestQuerySerializer, RouteQuerySerializer


class GeocodeAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        serializer = GeocodeQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        try:
            loc = GeocodeAddressUseCase().execute(direccion_texto=serializer.validated_data["direccion_texto"])
        except ValidationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                "direccion_texto": loc.direccion_texto,
                "latitud": float(loc.latitud),
                "longitud": float(loc.longitud),
            },
            status=status.HTTP_200_OK,
        )


class GeocodeSuggestAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        serializer = GeocodeSuggestQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        try:
            items = SuggestAddressesUseCase().execute(
                query=serializer.validated_data["q"],
                limit=serializer.validated_data.get("limit") or 5,
            )
        except ValidationError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"items": items}, status=status.HTTP_200_OK)


class RouteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = RouteQuerySerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        route = GetRouteUseCase().execute(coords=serializer.validated_data["coords"])
        if not route:
            return Response(
                {"detail": "No fue posible consultar el servicio de rutas"},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        return Response(
            {
                "duration": float(route.get("duration") or 0),
                "distance": float(route.get("distance") or 0),
                "geometry": route.get("geometry") or [],
                "legs": [
                    {
                        "duration": float(leg.get("duration") or 0),
                        "distance": float(leg.get("distance") or 0),
                    }
                    for leg in (route.get("legs") or [])
                ],
            },
            status=status.HTTP_200_OK,
        )