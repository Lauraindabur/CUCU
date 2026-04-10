from decimal import Decimal, ROUND_HALF_UP
from math import cos, radians, sin

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from geo.infrastructure.models import Ubicacion
from market.infrastructure.models import Publicacion


class Command(BaseCommand):
    help = "Crea publicaciones demo cerca de Medellin para probar filtros de compra"

    BASE_LAT = Decimal("6.216527")
    BASE_LNG = Decimal("-75.603663")

    DEMO_ITEMS = [
        {
            "email": "tacos.cucu@example.com",
            "nombre": "Andrea Martinez",
            "titulo": "Tacos de Carnitas",
            "descripcion": "Tortillas rellenas de carnitas al estilo mexicano con cebolla encurtida y salsa de la casa.",
            "precio": 12000,
            "direccion": "Calle 10 #43C-12, El Poblado, Medellin",
            "target_distance_km": "0.1",
            "bearing_deg": 10,
        },
        {
            "email": "ensaladas.cucu@example.com",
            "nombre": "Roberto Lopez",
            "titulo": "Ensalada Cesar",
            "descripcion": "Lechuga fresca, pollo a la parrilla, crotones artesanales y aderezo cesar casero.",
            "precio": 18500,
            "direccion": "Carrera 42 #8-15, El Poblado, Medellin",
            "target_distance_km": "0.5",
            "bearing_deg": 55,
        },
        {
            "email": "pasta.cucu@example.com",
            "nombre": "Valeria Ruiz",
            "titulo": "Pasta Boloñesa",
            "descripcion": "Espagueti con salsa boloñesa lenta, parmesano y albahaca fresca.",
            "precio": 22000,
            "direccion": "Calle 9 #39-48, Manila, Medellin",
            "target_distance_km": "0.9",
            "bearing_deg": 100,
        },
        {
            "email": "pozole.cucu@example.com",
            "nombre": "Luis Garcia",
            "titulo": "Pozole Rojo",
            "descripcion": "Pozole tradicional, picante y lleno de sabor con maiz pozolero y rabanos frescos.",
            "precio": 17000,
            "direccion": "Carrera 43A #6 Sur-26, Medellin",
            "target_distance_km": "1.3",
            "bearing_deg": 140,
        },
        {
            "email": "bowl.cucu@example.com",
            "nombre": "Carla Jimenez",
            "titulo": "Bowl Saludable",
            "descripcion": "Pollo a la plancha, quinoa, espinaca, aguacate y vegetales rostizados.",
            "precio": 19500,
            "direccion": "Carrera 34 #7-58, Provenza, Medellin",
            "target_distance_km": "1.8",
            "bearing_deg": 180,
        },
        {
            "email": "chilaquiles.cucu@example.com",
            "nombre": "Mario Sanchez",
            "titulo": "Chilaquiles Verdes",
            "descripcion": "Totopos crujientes con pollo, salsa verde, crema y queso fresco.",
            "precio": 16000,
            "direccion": "Calle 8 #38-21, Medellin",
            "target_distance_km": "2.2",
            "bearing_deg": 220,
        },
        {
            "email": "lasagna.cucu@example.com",
            "nombre": "Sofia Herrera",
            "titulo": "Lasagna Casera",
            "descripcion": "Capas de pasta, carne y queso gratinado al horno, ideal para almuerzo abundante.",
            "precio": 28000,
            "direccion": "Calle 12 #30-45, Medellin",
            "target_distance_km": "2.7",
            "bearing_deg": 260,
        },
        {
            "email": "brownie.cucu@example.com",
            "nombre": "Paula Moreno",
            "titulo": "Brownie de Chocolate",
            "descripcion": "Brownie humedo con nueces y salsa tibia de chocolate semiamargo.",
            "precio": 9000,
            "direccion": "Carrera 35 #10B-20, Medellin",
            "target_distance_km": "3.1",
            "bearing_deg": 300,
        },
        {
            "email": "pizza.cucu@example.com",
            "nombre": "Tomas Vega",
            "titulo": "Pizza Margarita",
            "descripcion": "Pizza artesanal con salsa pomodoro, mozzarella fresca y albahaca.",
            "precio": 36000,
            "direccion": "Calle 10A #36-11, Medellin",
            "target_distance_km": "3.6",
            "bearing_deg": 330,
        },
        {
            "email": "cheesecake.cucu@example.com",
            "nombre": "Laura Castro",
            "titulo": "Cheesecake de Frutos Rojos",
            "descripcion": "Cheesecake cremoso con base crocante y cubierta de frutos rojos.",
            "precio": 14000,
            "direccion": "Carrera 39 #11-08, Medellin",
            "target_distance_km": "4.0",
            "bearing_deg": 20,
        },
        {
            "email": "ramen.cucu@example.com",
            "nombre": "Diego Alvarez",
            "titulo": "Ramen de Cerdo",
            "descripcion": "Caldo intenso, fideos, huevo marinado y panceta cocinada lentamente.",
            "precio": 32000,
            "direccion": "Carrera 44 #10-91, Medellin",
            "target_distance_km": "4.5",
            "bearing_deg": 80,
        },
        {
            "email": "galletas.cucu@example.com",
            "nombre": "Juliana Arias",
            "titulo": "Cookies Artesanales",
            "descripcion": "Galletas recien horneadas de vainilla y chips de chocolate.",
            "precio": 8000,
            "direccion": "Calle 14 #37-44, Medellin",
            "target_distance_km": "5.0",
            "bearing_deg": 125,
        },
        {
            "email": "salchipapas.cucu@example.com",
            "nombre": "Kevin Rojas",
            "titulo": "Salchipapas",
            "descripcion": "Salchicha, papa crocante, salsas y toque casero para compartir.",
            "precio": 15000,
            "direccion": "Carrera 41 #9-18, Medellin",
            "target_distance_km": "2.5",
            "bearing_deg": 245,
            "stock": 0,
            "categoria": "otra",
        },
        {
            "email": "parrilla.cucu@example.com",
            "nombre": "Esteban Mejia",
            "titulo": "Carne a la parrilla",
            "descripcion": "Corte a la parrilla con guarnición del día y chimichurri casero.",
            "precio": 32000,
            "direccion": "Calle 11 #34-28, Medellin",
            "target_distance_km": "3.3",
            "bearing_deg": 290,
            "stock": 0,
            "categoria": "otra",
        },
        {
            "email": "frijoles.cucu@example.com",
            "nombre": "Diana Gomez",
            "titulo": "Frijoles",
            "descripcion": "Frijoles caseros con arroz, aguacate y acompañamiento tradicional.",
            "precio": 18000,
            "direccion": "Carrera 36 #8-60, Medellin",
            "target_distance_km": "4.2",
            "bearing_deg": 315,
            "stock": 0,
            "categoria": "otra",
        },
        {
            "email": "arroz.cucu@example.com",
            "nombre": "Natalia Jaramillo",
            "titulo": "Arroz con pollo",
            "descripcion": "Arroz sazonado con pollo desmechado, verduras y aliños caseros.",
            "precio": 19000,
            "direccion": "Calle 13 #32-17, Medellin",
            "target_distance_km": "4.8",
            "bearing_deg": 350,
            "stock": 0,
            "categoria": "otra",
        },
    ]

    COORD_DECIMALS = Decimal("0.000001")

    def _coordinates_for_distance(self, *, distance_km: Decimal, bearing_deg: int):
        distance = float(distance_km)
        angle = radians(float(bearing_deg))
        km_per_lat_degree = 111.32
        km_per_lng_degree = 111.32 * cos(radians(float(self.BASE_LAT)))

        lat_offset = Decimal(distance * cos(angle) / km_per_lat_degree)
        lng_offset = Decimal(distance * sin(angle) / km_per_lng_degree)

        latitud = (self.BASE_LAT + lat_offset).quantize(self.COORD_DECIMALS, rounding=ROUND_HALF_UP)
        longitud = (self.BASE_LNG + lng_offset).quantize(self.COORD_DECIMALS, rounding=ROUND_HALF_UP)
        return latitud, longitud

    def handle(self, *args, **options):
        user_model = get_user_model()
        created = 0
        updated = 0

        for item in self.DEMO_ITEMS:
            user, _ = user_model.objects.get_or_create(
                username=item["email"],
                defaults={
                    "email": item["email"],
                    "nombre": item["nombre"],
                },
            )

            if not user.email:
                user.email = item["email"]
            if not user.nombre:
                user.nombre = item["nombre"]
            user.set_password("secret12345")
            user.save()

            latitud, longitud = self._coordinates_for_distance(
                distance_km=Decimal(item["target_distance_km"]),
                bearing_deg=int(item["bearing_deg"]),
            )

            ubicacion, _ = Ubicacion.objects.update_or_create(
                direccion_texto=item["direccion"],
                defaults={
                    "latitud": latitud,
                    "longitud": longitud,
                },
            )

            publicacion, was_created = Publicacion.objects.update_or_create(
                titulo=item["titulo"],
                usuario=user,
                defaults={
                    "descripcion": item["descripcion"],
                    "categoria": item.get("categoria", ""),
                    "stock": int(item.get("stock", 10)),
                    "maximo_por_venta": int(item.get("maximo_por_venta", 5)),
                    "precio": item["precio"],
                    "estado": "ACTIVA",
                    "ubicacion": ubicacion,
                },
            )

            _ = publicacion
            if was_created:
                created += 1
            else:
                updated += 1

        self.stdout.write(self.style.SUCCESS(
            f"Catalogo demo listo. Creadas: {created}. Actualizadas: {updated}."
        ))