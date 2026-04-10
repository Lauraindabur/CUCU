from __future__ import annotations

import json
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


def _fetch_json(url: str, *, headers: dict[str, str], timeout: int):
    req = Request(url, headers=headers)
    with urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _decode_polyline6(encoded: str) -> list[list[float]]:
    coordinates: list[list[float]] = []
    index = 0
    lat = 0
    lon = 0
    factor = 1_000_000

    while index < len(encoded):
        result = 1
        shift = 0
        while True:
            byte = ord(encoded[index]) - 64
            index += 1
            result += byte << shift
            shift += 5
            if byte < 0x1F:
                break
        lat += ~(result >> 1) if result & 1 else (result >> 1)

        result = 1
        shift = 0
        while True:
            byte = ord(encoded[index]) - 64
            index += 1
            result += byte << shift
            shift += 5
            if byte < 0x1F:
                break
        lon += ~(result >> 1) if result & 1 else (result >> 1)

        coordinates.append([lon / factor, lat / factor])

    return coordinates


class RouteService:
    def get_route(self, *, coords: str):
        route = None
        for fetcher in (self._fetch_osrm_route, self._fetch_valhalla_route):
            try:
                route = fetcher(coords)
            except Exception:
                route = None
            if route:
                return route
        return None

    def _fetch_osrm_route(self, coords: str):
        params = urlencode({
            "overview": "full",
            "geometries": "geojson",
            "steps": "false",
        })
        url = f"https://router.project-osrm.org/route/v1/driving/{coords}?{params}"
        payload = _fetch_json(url, headers={"User-Agent": "CUCU/1.0 routing"}, timeout=4)

        if payload.get("code") != "Ok":
            return None

        routes = payload.get("routes") or []
        if not routes:
            return None

        route = routes[0]
        geometry = (route.get("geometry") or {}).get("coordinates") or []
        legs = route.get("legs") or []
        if not geometry:
            return None

        return {
            "duration": float(route.get("duration") or 0),
            "distance": float(route.get("distance") or 0),
            "geometry": geometry,
            "legs": [
                {
                    "duration": float(leg.get("duration") or 0),
                    "distance": float(leg.get("distance") or 0),
                }
                for leg in legs
            ],
        }

    def _fetch_valhalla_route(self, coords: str):
        points: list[dict[str, float]] = []
        for pair in str(coords or "").split(";"):
            lon_str, lat_str = pair.split(",")
            points.append({"lon": float(lon_str), "lat": float(lat_str)})

        payload_json = json.dumps(
            {
                "locations": points,
                "costing": "auto",
                "directions_options": {"units": "kilometers"},
            },
            separators=(",", ":"),
        )
        url = f"https://valhalla1.openstreetmap.de/route?json={quote(payload_json)}"
        payload = _fetch_json(url, headers={"User-Agent": "CUCU/1.0 routing"}, timeout=10)

        trip = payload.get("trip") or {}
        if int(trip.get("status", -1)) != 0:
            return None

        legs = trip.get("legs") or []
        if not legs:
            return None

        geometry: list[list[float]] = []
        normalized_legs: list[dict[str, float]] = []
        for leg in legs:
            shape = str(leg.get("shape") or "")
            decoded = _decode_polyline6(shape) if shape else []
            if decoded:
                if geometry and geometry[-1] == decoded[0]:
                    geometry.extend(decoded[1:])
                else:
                    geometry.extend(decoded)

            summary = leg.get("summary") or {}
            normalized_legs.append(
                {
                    "duration": float(summary.get("time") or 0),
                    "distance": float(summary.get("length") or 0) * 1000,
                }
            )

        if not geometry:
            return None

        return {
            "duration": sum(leg["duration"] for leg in normalized_legs),
            "distance": sum(leg["distance"] for leg in normalized_legs),
            "geometry": geometry,
            "legs": normalized_legs,
        }