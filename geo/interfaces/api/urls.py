from django.urls import path

from .views import GeocodeAPIView, GeocodeSuggestAPIView, RouteAPIView


urlpatterns = [
    path("geocode", GeocodeAPIView.as_view(), name="geocode"),
    path("geocode/", GeocodeAPIView.as_view(), name="geocode-slash"),
    path("geocode/suggest", GeocodeSuggestAPIView.as_view(), name="geocode-suggest"),
    path("geocode/suggest/", GeocodeSuggestAPIView.as_view(), name="geocode-suggest-slash"),
    path("route", RouteAPIView.as_view(), name="route"),
    path("route/", RouteAPIView.as_view(), name="route-slash"),
]