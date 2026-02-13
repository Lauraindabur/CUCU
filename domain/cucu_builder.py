from core.models import Cucu

class CucuBuilder:
    def __init__(self):
        self._data = {}

    def con_titulo(self, titulo):
        self._data['titulo'] = titulo
        return self

    def con_descripcion(self, descripcion):
        self._data['descripcion'] = descripcion
        return self

    def con_precio(self, precio):
        self._data['precio'] = precio
        return self

    def con_ubicacion(self, ubicacion):
        self._data['ubicacion'] = ubicacion
        return self

    def build(self):
        # Validación simple
        if not all([self._data.get('titulo'), self._data.get('descripcion'), self._data.get('precio'), self._data.get('ubicacion')]):
            raise ValueError('Todos los campos son obligatorios')
        return Cucu(**self._data)
