from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from decimal import Decimal
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from common.exceptions import ValidationError
from config.settings import GOOGLE_MAPS_API_KEY


@dataclass
class GeocodedLocation:
    latitud: Decimal
    longitud: Decimal
    direccion_texto: str


class GeocodingService:
    _SUGGEST_CACHE_TTL_SECONDS = 120
    _SUGGEST_NEGATIVE_CACHE_TTL_SECONDS = 5
    _NOMINATIM_BACKOFF_SECONDS = 20
    _GEOCODE_CACHE_TTL_SECONDS = 600
    _SUGGEST_CACHE_MAX = 300
    _GEOCODE_CACHE_MAX = 500
    _suggest_cache: dict[tuple, tuple[float, list[dict]]] = {}
    _geocode_cache: dict[str, tuple[float, GeocodedLocation]] = {}
    _nominatim_backoff_until: float = 0.0

    # Fallback mínimo de POIs en Medellín para cuando Nominatim está lento o rate-limit (429).
    # Coordenadas aproximadas.
    _POI_FALLBACKS: list[dict] = [
        {
            "aliases": ["eafit", "universidad eafit"],
            "primary": "Universidad EAFIT",
            "secondary": "El Poblado, Medellin, Antioquia, Colombia",
            "display_name": "Universidad EAFIT, El Poblado, Medellin, Antioquia, Colombia",
            "lat": 6.2007,
            "lon": -75.5785,
        },
        {
            "aliases": ["udea", "universidad de antioquia"],
            "primary": "Universidad de Antioquia",
            "secondary": "Medellin, Antioquia, Colombia",
            "display_name": "Universidad de Antioquia, Medellin, Antioquia, Colombia",
            "lat": 6.2661,
            "lon": -75.5684,
        },
        {
            "aliases": ["unal", "universidad nacional", "universidad nacional medellin"],
            "primary": "Universidad Nacional de Colombia (Sede Medellin)",
            "secondary": "Medellin, Antioquia, Colombia",
            "display_name": "Universidad Nacional de Colombia (Sede Medellin), Medellin, Antioquia, Colombia",
            "lat": 6.2630,
            "lon": -75.5762,
        },
        {
            "aliases": ["upb", "universidad pontificia bolivariana"],
            "primary": "Universidad Pontificia Bolivariana (UPB)",
            "secondary": "Medellin, Antioquia, Colombia",
            "display_name": "Universidad Pontificia Bolivariana (UPB), Medellin, Antioquia, Colombia",
            "lat": 6.2451,
            "lon": -75.5883,
        },
        {
            "aliases": ["santafe", "santa fe", "cc santafe", "centro comercial santafe", "centro comercial santafé"],
            "primary": "Centro Comercial Santafe Medellin",
            "secondary": "El Poblado, Medellin, Antioquia, Colombia",
            "display_name": "Centro Comercial Santafe Medellin, El Poblado, Medellin, Antioquia, Colombia",
            "lat": 6.1976,
            "lon": -75.5734,
        },
    ]

    @classmethod
    def _poi_fallback_matches(cls, q: str) -> list[dict]:
        text = (q or "").strip().lower()
        if not text:
            return []
        hits: list[dict] = []
        for poi in cls._POI_FALLBACKS:
            aliases = poi.get("aliases") or []
            if any(alias in text for alias in aliases):
                hits.append(poi)
        return hits

    @classmethod
    def _poi_fallback_location(cls, direccion_texto: str) -> GeocodedLocation | None:
        hits = cls._poi_fallback_matches(direccion_texto)
        if not hits:
            return None
        poi = hits[0]
        return GeocodedLocation(
            latitud=Decimal(str(poi["lat"])),
            longitud=Decimal(str(poi["lon"])),
            direccion_texto=str(poi["display_name"]),
        )

    def geocode_address(self, *, direccion_texto: str) -> GeocodedLocation:
        direccion = (direccion_texto or "").strip()
        if not direccion:
            raise ValidationError("La dirección es requerida")

        poi_loc = self._poi_fallback_location(direccion)
        if poi_loc is not None:
            return poi_loc

        scope = self._detect_query_scope(direccion)
        direccion_ctx = self._add_default_context_if_needed(direccion, scope=scope)
        countrycodes = "co" if scope == "colombia" else None

        cached = self._geocode_cache_get(direccion_ctx)
        if cached is not None:
            return cached

        if GOOGLE_MAPS_API_KEY:
            result = self._google_geocode(direccion_ctx)
            if result is not None:
                self._geocode_cache_set(direccion_ctx, result)
                return result

        result = self._nominatim_geocode(direccion_ctx, countrycodes=countrycodes)
        if result is not None:
            self._geocode_cache_set(direccion_ctx, result)
            return result

        # Fallback: algunas direcciones muy específicas no existen en OSM.
        # Probamos variantes más generales (sector/intersección) antes de fallar.
        if countrycodes == "co":
            for variant in self._fallback_queries_for_co(direccion_ctx):
                result = self._nominatim_geocode(variant, countrycodes=countrycodes)
                if result is not None:
                    self._geocode_cache_set(direccion_ctx, result)
                    return result

        raise ValidationError("No se pudo ubicar la dirección proporcionada")

    def suggest_addresses(self, *, query: str, limit: int = 5) -> list[dict]:
        q = (query or "").strip()
        if not q:
            raise ValidationError("La dirección es requerida")

        safe_limit = int(limit or 5)
        safe_limit = max(1, min(10, safe_limit))

        cached = self._suggest_cache_get(q, safe_limit)
        if cached is not None:
            return cached

        poi_hits = self._poi_fallback_matches(q)
        if poi_hits:
            items = [
                {
                    "display_name": str(poi["display_name"]),
                    "primary": str(poi["primary"]),
                    "secondary": str(poi["secondary"]),
                    "latitud": float(poi["lat"]),
                    "longitud": float(poi["lon"]),
                }
                for poi in poi_hits
            ][:safe_limit]
            self._suggest_cache_set(q, safe_limit, items)
            return items

        scope = self._detect_query_scope(q)
        restrict_medellin = False
        countrycodes = "co" if scope == "colombia" else None
        bounded = False
        viewbox = None

        q_scoped = self._add_default_context_if_needed(q, scope=scope)

        is_place_query = self._looks_like_place_query(q)

        normalized = self._normalize_co_address_query(q_scoped) if countrycodes == "co" else q_scoped
        variants: list[str] = []

        def add_variant(value: str | None):
            text = str(value or "").strip()
            if not text:
                return
            if text in variants:
                return
            variants.append(text)

        # Para direcciones Colombia priorizamos primero la forma más útil/normalizada.
        if countrycodes == "co":
            add_variant(normalized)
        else:
            add_variant(q_scoped)

        if q != q_scoped:
            add_variant(q)

        if is_place_query:
            stripped = self._strip_place_noise(q)
            add_variant(stripped)

        if countrycodes != "co":
            add_variant(normalized)

        # Nominatim a veces no reconoce el formato colombiano con "#".
        # Probamos variantes sin '#', y con separadores alternos.
        no_hash = ""
        no_hash_no_dash = ""
        if normalized and countrycodes == "co":
            no_hash = re.sub(r"\s*#\s*", " ", normalized)
            no_hash = re.sub(r"\s+", " ", no_hash).strip()
            add_variant(no_hash)

            no_hash_no_dash = re.sub(r"-", " ", no_hash)
            no_hash_no_dash = re.sub(r"\s+", " ", no_hash_no_dash).strip()
            add_variant(no_hash_no_dash)

        # Variante adicional: cuando el usuario va escribiendo, intentamos con "#80C" sin el tramo final.
        general = ""
        road_only = ""
        if countrycodes == "co":
            general = self._generalize_co_house_number_variant(normalized or q_scoped)
            add_variant(general)

            road_only = self._road_only_variant(normalized or q_scoped)
            add_variant(road_only)

        merged: list[dict] = []
        seen = set()

        def push(item: dict):
            display = str(item.get("display_name") or "").strip()
            lat = item.get("lat")
            lon = item.get("lon")
            if not display or lat is None or lon is None:
                return

            if restrict_medellin:
                # Filtra resultados fuera de Medellín/V.A. cuando la query fue de Medellín.
                if not self._looks_like_medellin_result(item):
                    return

            key = (display.lower(), str(lat), str(lon))
            if key in seen:
                return
            seen.add(key)

            primary, secondary = self._split_suggestion_display(item)
            merged.append(
                {
                    "display_name": display,
                    "primary": primary,
                    "secondary": secondary,
                    "latitud": float(lat),
                    "longitud": float(lon),
                }
            )

        # Mantiene el autocomplete ágil, pero para direcciones de Colombia con detalle
        # (#, letras o numeración parcial) probamos un pequeño set de variantes más específicas
        # antes de caer al nombre de la vía.
        primary_query = str(variants[0] if variants else "").strip()
        query_has_house_detail = bool(re.search(r"#|\d+[A-Za-z]", q))
        variants_to_try = variants[:1]
        if countrycodes == "co" and query_has_house_detail:
            variants_to_try = variants[:4]

        for variant in variants_to_try:
            for it in self._nominatim_search(
                variant,
                limit=safe_limit,
                bounded=bounded,
                viewbox=viewbox,
                countrycodes=countrycodes,
                timeout=1.35,
            ):
                push(it)
            if merged:
                break

        # Si las variantes "específicas" llevaron a una calle equivocada (por ejemplo,
        # interpretando "#80C" como si fuera la vía "Calle 80C"), descartamos ese set
        # y preferimos volver a la vía base correcta.
        if countrycodes == "co" and query_has_house_detail and merged and road_only:
            road_primary = self._split_display_name(road_only)[0].strip().lower()
            if road_primary:
                has_consistent_result = any(
                    road_primary in str(item.get("primary") or "").lower()
                    or road_primary in str(item.get("display_name") or "").lower()
                    for item in merged
                )
                if not has_consistent_result:
                    merged = []
                    seen = set()

        # Fallback extra (solo Colombia): si la dirección exacta no existe en OSM,
        # devolvemos algo útil (vía/sector) en vez de dropdown vacío.
        if not merged and countrycodes == "co":
            fallback_variant = road_only or general or no_hash or no_hash_no_dash
            fallback_variant = str(fallback_variant or "").strip()
            if fallback_variant and fallback_variant != primary_query:
                for it in self._nominatim_search(
                    fallback_variant,
                    limit=safe_limit,
                    bounded=bounded,
                    viewbox=viewbox,
                    countrycodes=countrycodes,
                    timeout=1.8,
                ):
                    push(it)

        final_items = merged[:safe_limit]
        if countrycodes == "co" and query_has_house_detail and final_items:
            exact_prefix = self._co_address_display_prefix(normalized or q_scoped or q)
            if exact_prefix:
                best_match = final_items[0]
                exact_secondary = str(best_match.get("secondary") or "").strip() or "Usar la dirección escrita"
                exact_display = exact_prefix if not exact_secondary else f"{exact_prefix}, {exact_secondary}"
                exact_item = {
                    **best_match,
                    "display_name": exact_display,
                    "primary": exact_prefix,
                    "secondary": exact_secondary,
                }
                remainder = [
                    {
                        **item,
                        "primary": exact_prefix,
                    }
                    for item in final_items[1:]
                ]
                final_items = [exact_item, *remainder][:safe_limit]
        self._suggest_cache_set(q, safe_limit, final_items)
        return final_items

    def _google_geocode(self, direccion_texto: str) -> GeocodedLocation | None:
        params = urlencode({"address": direccion_texto, "key": GOOGLE_MAPS_API_KEY})
        url = f"https://maps.googleapis.com/maps/api/geocode/json?{params}"
        payload = self._fetch_json(url, headers={})

        results = payload.get("results") or []
        if not results:
            return None

        location = results[0].get("geometry", {}).get("location", {})
        if "lat" not in location or "lng" not in location:
            return None

        return GeocodedLocation(
            latitud=Decimal(str(location["lat"])),
            longitud=Decimal(str(location["lng"])),
            direccion_texto=results[0].get("formatted_address") or direccion_texto,
        )

    def _nominatim_geocode(self, direccion_texto: str, *, countrycodes: str | None = None) -> GeocodedLocation | None:
        if time.time() < self._nominatim_backoff_until:
            return None

        params_dict = {
            "q": direccion_texto,
            "format": "json",
            "limit": 1,
        }
        if countrycodes:
            params_dict["countrycodes"] = countrycodes

        params = urlencode(params_dict)
        url = f"https://nominatim.openstreetmap.org/search?{params}"
        payload = self._fetch_json(
            url,
            headers={"User-Agent": "CUCU/1.0 (cucu-local-dev) geocoding"},
            timeout=5,
        )

        if not payload:
            return None

        result = payload[0]
        latitud = result.get("lat")
        longitud = result.get("lon")
        if latitud is None or longitud is None:
            return None

        return GeocodedLocation(
            latitud=Decimal(str(latitud)),
            longitud=Decimal(str(longitud)),
            direccion_texto=result.get("display_name") or direccion_texto,
        )

    def _nominatim_search(
        self,
        direccion_texto: str,
        *,
        limit: int = 5,
        bounded: bool = True,
        viewbox: str | None = None,
        countrycodes: str | None = None,
        timeout: float | None = None,
    ) -> list[dict]:
        if time.time() < self._nominatim_backoff_until:
            return []

        params_map: dict[str, object] = {
            "q": direccion_texto,
            "format": "jsonv2",
            "limit": int(limit or 5),
            "addressdetails": 1,
            "dedupe": 1,
        }
        if countrycodes:
            params_map["countrycodes"] = countrycodes
        if viewbox:
            params_map["viewbox"] = viewbox
            params_map["bounded"] = 1 if bounded else 0

        params = urlencode(params_map)
        url = f"https://nominatim.openstreetmap.org/search?{params}"
        effective_timeout = float(timeout) if timeout is not None else (2.2 if bounded else 3.0)
        try:
            payload = self._fetch_json(
                url,
                headers={
                    "User-Agent": "CUCU/1.0 (cucu-local-dev) geocoding",
                    "Accept-Language": "es",
                },
                timeout=effective_timeout,
            )
        except ValidationError:
            # En autocomplete preferimos fallar "rápido" y silencioso.
            return []

        if not payload:
            return []
        if not isinstance(payload, list):
            return []
        return payload

    @staticmethod
    def _split_display_name(display: str) -> tuple[str, str]:
        text = (display or "").strip()
        if not text:
            return ("", "")
        parts = [p.strip() for p in text.split(",") if p.strip()]
        if not parts:
            return (text, "")
        primary = parts[0]
        secondary = ", ".join(parts[1:]) if len(parts) > 1 else ""
        return (primary, secondary)

    def _split_suggestion_display(self, item: dict) -> tuple[str, str]:
        display = str(item.get("display_name") or "").strip()
        address = item.get("address") or {}
        if isinstance(address, dict):
            road = str(address.get("road") or "").strip()
            house = str(address.get("house_number") or "").strip()
            name = str(address.get("name") or "").strip()
            neighbourhood = str(address.get("neighbourhood") or address.get("suburb") or "").strip()
            city = str(address.get("city") or address.get("town") or address.get("municipality") or "").strip()
            state = str(address.get("state") or "").strip()
            country = str(address.get("country") or "").strip()

            display_primary, _ = self._split_display_name(display)

            # Para POIs: a veces 'address.name' viene vacío, pero el primer segmento del display_name
            # sí contiene el nombre del lugar (ej. "Universidad EAFIT").
            if name:
                primary = name
            elif display_primary and road and display_primary.lower() != road.lower():
                primary = display_primary
            elif road and house:
                primary = f"{road} {house}".strip()
            elif road:
                primary = road
            else:
                primary = display_primary

            road_line = " ".join([p for p in [road, house] if p]).strip()
            secondary_parts = [p for p in [road_line, neighbourhood, city, state, country] if p]
            secondary = ", ".join(secondary_parts) if secondary_parts else self._split_display_name(display)[1]
            return (primary, secondary)

        return self._split_display_name(display)

    @staticmethod
    def _looks_like_medellin_result(item: dict) -> bool:
        display = str(item.get("display_name") or "").lower()
        lat = item.get("lat")
        lon = item.get("lon")
        try:
            if lat is not None and lon is not None and GeocodingService._is_within_medellin_viewbox(float(lat), float(lon)):
                return True
        except (TypeError, ValueError):
            pass

        if "medell" in display and "antioquia" in display:
            return True

        address = item.get("address") or {}
        if not isinstance(address, dict):
            return False

        city = str(address.get("city") or address.get("town") or address.get("municipality") or "").lower()
        state = str(address.get("state") or "").lower()
        county = str(address.get("county") or "").lower()

        if "antioquia" not in state and "antioquia" not in county and "antioquia" not in display:
            return False

        if "medell" in city or "medell" in display:
            return True

        # Algunos resultados vienen etiquetados por región (Valle de Aburrá).
        return "aburr" in display

    @classmethod
    def _is_within_medellin_viewbox(cls, lat: float, lon: float) -> bool:
        # MEDELLIN_VIEWBOX: "minlon,minlat,maxlon,maxlat"
        try:
            min_lon_s, min_lat_s, max_lon_s, max_lat_s = (cls.MEDELLIN_VIEWBOX or "").split(",")
            min_lon = float(min_lon_s)
            min_lat = float(min_lat_s)
            max_lon = float(max_lon_s)
            max_lat = float(max_lat_s)
        except Exception:
            return False

        return (min_lat <= lat <= max_lat) and (min_lon <= lon <= max_lon)

    @staticmethod
    def _looks_like_place_query(query: str) -> bool:
        q = (query or "").strip().lower()
        if not q:
            return False

        # Si parece dirección (calle/carrera/#), NO lo tratamos como POI.
        if re.search(r"\b(cl|calle|cra|carrera|kr|av|avenida)\b", q):
            return False
        if "#" in q:
            return False

        has_letters = bool(re.search(r"[a-záéíóúñ]", q))
        has_digits = bool(re.search(r"\d", q))
        # Nombres suelen tener letras; si tiene dígitos, igual puede ser (p.ej. "Universidad 1").
        return has_letters and len(q) >= 3 and not (has_digits and len(q) <= 4)

    @staticmethod
    def _strip_place_noise(query: str) -> str:
        q = (query or "").strip()
        if not q:
            return ""

        # Quita prefijos genéricos que a veces hacen que Nominatim no encuentre el POI.
        lowered = q.lower().strip()
        patterns = [
            r"^parque\s+",
            r"^centro\s+comercial\s+",
            r"^c\.?c\.?\s+",
            r"^cc\s+",
            r"^universidad\s+",
        ]
        for p in patterns:
            new_lowered = re.sub(p, "", lowered, flags=re.IGNORECASE)
            if new_lowered != lowered:
                # Conserva capitalización simple (título) para la query.
                cleaned = new_lowered.strip()
                if len(cleaned) >= 3:
                    return cleaned
                return ""

        return ""

    @staticmethod
    def _normalize_co_address_query(query: str) -> str:
        a = (query or "").strip()
        if not a:
            return ""

        a = re.sub(r"\s+", " ", a)
        # Solo expandimos abreviaturas cuando son un token completo (seguido de espacio).
        # Importante: evitar que "cal" haga match sobre "Calle" ("Calle" -> "Calle le").
        a = re.sub(r"^cl\.?\s+", "Calle ", a, flags=re.IGNORECASE)
        a = re.sub(r"^cll\.?\s+", "Calle ", a, flags=re.IGNORECASE)
        a = re.sub(r"^cal\.?\s+", "Calle ", a, flags=re.IGNORECASE)
        a = re.sub(r"^cra\.?\s+", "Carrera ", a, flags=re.IGNORECASE)
        a = re.sub(r"^kr\.?\s+", "Carrera ", a, flags=re.IGNORECASE)
        a = re.sub(r"^av\.?\s+", "Avenida ", a, flags=re.IGNORECASE)

        # Espacio antes del # cuando viene pegado
        a = re.sub(r"(\d)\s*#", r"\1 #", a)

        # "Calle 5 #80c125" -> "Calle 5 #80C-125"
        m_hash = re.match(r"^(Calle|Carrera)\s*(\d+[A-Za-z]?)\s*#\s*(\d+)\s*([A-Za-z])\s*-?\s*(\d+)(\s*,.*)?$", a, flags=re.IGNORECASE)
        if m_hash:
            via = m_hash.group(1).title()
            num1 = m_hash.group(2)
            num2 = f"{m_hash.group(3)}{m_hash.group(4).upper()}"
            num3 = m_hash.group(5)
            tail = (m_hash.group(6) or "").strip()
            rebuilt = f"{via} {num1} #{num2}-{num3}".strip()
            return f"{rebuilt} {tail}".strip()

        # "Calle 5 80c125" -> "Calle 5 #80C-125"
        m = re.match(r"^(Calle|Carrera)\s*(\d+[A-Za-z]?)\s+(\d+)([A-Za-z])\s*(\d+)(\s*,.*)?$", a, flags=re.IGNORECASE)
        if m:
            via = m.group(1).title()
            num1 = m.group(2)
            num2 = f"{m.group(3)}{m.group(4).upper()}"
            num3 = m.group(5)
            tail = (m.group(6) or "").strip()
            rebuilt = f"{via} {num1} #{num2}-{num3}".strip()
            return f"{rebuilt} {tail}".strip()

        return a

    @staticmethod
    def _looks_like_co_street_query(text: str) -> bool:
        a = (text or "").strip().lower()
        if not a:
            return False
        if "#" in a:
            return True
        if re.search(r"\b(cl|cll|calle|cra|carrera|kr|avenida|av)\b", a) and re.search(r"\d", a):
            return True
        return False

    @staticmethod
    def _contains_other_colombian_city_hint(text: str) -> bool:
        a = (text or "").lower()
        # Si el usuario escribe otra ciudad, no forzamos Medellín.
        return bool(
            re.search(
                r"\b(bogot|cali\b|barranquilla|cartagena|bucaramanga|pereira|manizales|cucuta|ibague|santa\s*marta|villavicencio|pasto|armenia)\b",
                a,
            )
        )

    @classmethod
    def _detect_query_scope(cls, text: str) -> str:
        a = (text or "").strip().lower()
        if not a:
            return "global"

        # Si ya menciona Medellín/Antioquia, asumimos Colombia pero sin limitar ciudad.
        if re.search(r"medell[ií]n", a) or "antioquia" in a:
            return "colombia"

        # Direcciones tipo Colombia (calle/carrera/#): asumimos Colombia.
        if cls._looks_like_co_street_query(a):
            return "colombia"

        # Por defecto: global (sin viewbox ni countrycodes).
        return "global"

    @classmethod
    def _add_default_context_if_needed(cls, text: str, *, scope: str) -> str:
        a = (text or "").strip()
        if not a:
            return ""

        if scope == "colombia":
            if re.search(r"\bcolombia\b", a, re.IGNORECASE):
                return a
            return f"{a}, Colombia"

        return a

    @staticmethod
    def _generalize_co_house_number_variant(query: str) -> str:
        a = (query or "").strip()
        if not a:
            return ""

        # "Calle 5 #80C-125" -> "Calle 5 #80C" (mantiene sector)
        m = re.match(r"^(.*?#\s*[0-9]+\s*[A-Za-z])\s*-\s*\d+\s*(,.*)?$", a)
        if m:
            head = (m.group(1) or "").strip()
            tail = (m.group(2) or "").strip()
            return (head + (" " + tail if tail else "")).strip()

        # "Calle 5 80C" o "Calle 5 #80C" (sin el -125)
        m2 = re.match(r"^(Calle|Carrera)\s*(\d+[A-Za-z]?)\s*#?\s*(\d+)\s*([A-Za-z])\s*(,.*)?$", a, flags=re.IGNORECASE)
        if m2:
            via = m2.group(1).title()
            num1 = m2.group(2)
            num2 = f"{m2.group(3)}{m2.group(4).upper()}"
            tail = (m2.group(5) or "").strip()
            rebuilt = f"{via} {num1} #{num2}".strip()
            return f"{rebuilt} {tail}".strip()

        return ""

    @classmethod
    def _road_only_variant(cls, query: str) -> str:
        a = (query or "").strip()
        if not a:
            return ""

        a = cls._normalize_co_address_query(a)

        # Separa contexto (", Medellin...") antes de hacer match, para evitar
        # que una regex "greedy" se coma el tail.
        head, sep, tail = a.partition(",")
        head = head.strip()
        tail = tail.strip()

        # "Calle 5 #80C-125" -> "Calle 5"
        m = re.match(r"^(Calle|Carrera)\s*(\d+[A-Za-z]?)(?:\s+.*)?$", head, flags=re.IGNORECASE)
        if not m:
            return ""

        via = m.group(1).title()
        num1 = m.group(2)
        rebuilt = f"{via} {num1}".strip()
        if sep and tail:
            return f"{rebuilt}, {tail}".strip()
        return rebuilt

    @staticmethod
    def _co_address_display_prefix(query: str) -> str:
        text = str(query or "").strip()
        if not text:
            return ""
        head = text.split(",", 1)[0].strip()
        return re.sub(r"\s+", " ", head).strip()

    @staticmethod
    def _fallback_queries_for_co(direccion_texto: str) -> list[str]:
        direccion = (direccion_texto or "").strip()
        if not direccion:
            return []

        variants: list[str] = []

        # Caso típico Colombia: "Calle 5 #80C-125" -> "Calle 5 #80C" (mantiene zona/intersección).
        # También soporta espacios variables: "# 80C - 125".
        m = re.match(r"^(.*?#\s*[0-9A-Za-z]+)\s*-\s*\d+\s*(,.*)?$", direccion)
        if m:
            head = (m.group(1) or "").strip()
            tail = (m.group(2) or "").strip()
            variants.append((head + (" " + tail if tail else "")).strip())

        # Variante: quitar el tramo final "- 125" aunque no exista # (último recurso).
        variants.append(re.sub(r"\s*-\s*\d+\s*$", "", direccion).strip())

        # Elimina duplicados conservando orden
        out: list[str] = []
        for v in variants:
            v = (v or "").strip()
            if not v:
                continue
            if v == direccion:
                continue
            if v in out:
                continue
            out.append(v)
        return out

    @staticmethod
    def _fetch_json(url: str, *, headers: dict[str, str], timeout: float = 10):
        request = Request(url, headers=headers)
        try:
            with urlopen(request, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            # Si Nominatim rate-limita (429), aplicamos backoff para evitar martillar el proveedor.
            if exc.code == 429 and "nominatim.openstreetmap.org" in str(url):
                GeocodingService._nominatim_backoff_until = time.time() + GeocodingService._NOMINATIM_BACKOFF_SECONDS
            raise ValidationError("No fue posible consultar el servicio de geocodificación") from exc
        except Exception as exc:
            raise ValidationError("No fue posible consultar el servicio de geocodificación") from exc

    @classmethod
    def _suggest_cache_get(cls, query: str, limit: int) -> list[dict] | None:
        key = (str(query).strip().lower(), int(limit or 5))
        hit = cls._suggest_cache.get(key)
        if not hit:
            return None
        ts, items = hit
        ttl = cls._SUGGEST_NEGATIVE_CACHE_TTL_SECONDS if not items else cls._SUGGEST_CACHE_TTL_SECONDS
        if (time.time() - ts) > ttl:
            cls._suggest_cache.pop(key, None)
            return None
        return items

    @classmethod
    def _suggest_cache_set(cls, query: str, limit: int, items: list[dict]) -> None:
        key = (str(query).strip().lower(), int(limit or 5))
        if len(cls._suggest_cache) >= cls._SUGGEST_CACHE_MAX:
            # Evicción simple (FIFO por timestamp más antiguo)
            oldest_key = None
            oldest_ts = None
            for k, (ts, _) in cls._suggest_cache.items():
                if oldest_ts is None or ts < oldest_ts:
                    oldest_ts = ts
                    oldest_key = k
            if oldest_key is not None:
                cls._suggest_cache.pop(oldest_key, None)
        cls._suggest_cache[key] = (time.time(), items)

    @classmethod
    def _geocode_cache_get(cls, direccion_ctx: str) -> GeocodedLocation | None:
        key = str(direccion_ctx).strip().lower()
        hit = cls._geocode_cache.get(key)
        if not hit:
            return None
        ts, loc = hit
        if (time.time() - ts) > cls._GEOCODE_CACHE_TTL_SECONDS:
            cls._geocode_cache.pop(key, None)
            return None
        return loc

    @classmethod
    def _geocode_cache_set(cls, direccion_ctx: str, loc: GeocodedLocation) -> None:
        key = str(direccion_ctx).strip().lower()
        if len(cls._geocode_cache) >= cls._GEOCODE_CACHE_MAX:
            oldest_key = None
            oldest_ts = None
            for k, (ts, _) in cls._geocode_cache.items():
                if oldest_ts is None or ts < oldest_ts:
                    oldest_ts = ts
                    oldest_key = k
            if oldest_key is not None:
                cls._geocode_cache.pop(oldest_key, None)
        cls._geocode_cache[key] = (time.time(), loc)