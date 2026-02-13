import os

class Notificador:
    def enviar(self, mensaje):
        print(f"[REAL] Notificación: {mensaje}")

class NotificadorMock:
    def enviar(self, mensaje):
        print(f"[MOCK] Notificación: {mensaje}")

class NotificacionFactory:
    @staticmethod
    def crear_notificador():
        entorno = os.environ.get('CUCU_ENV', 'MOCK')
        if entorno == 'REAL':
            return Notificador()
        return NotificadorMock()
