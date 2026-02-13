from domain.cucu_builder import CucuBuilder
from infra.notificacion_factory import NotificacionFactory

class CucuService:
    def __init__(self, notificador=None):
        self.notificador = notificador or NotificacionFactory.crear_notificador()

    def diseñar_cucu(self, datos):
        builder = CucuBuilder()
        cucu_obj = (
            builder
            .con_titulo(datos['titulo'])
            .con_descripcion(datos['descripcion'])
            .con_precio(datos['precio'])
            .con_ubicacion(datos['ubicacion'])
            .con_usuario(datos['usuario'])
            .build()
        )
        cucu_obj.save()
        self.notificador.enviar(f"Nuevo CUCU publicado: {cucu_obj.titulo}")
        return cucu_obj
