<!--  
se usó python -m venv venv sirve para crear un entorno virtual, esto es para almacenar 
todas las librerías de ese proyecto

venv\Scripts\activate esto es para activar el entorno virtual

pip install django djangorestframework es para descargar django, la estructura basica del framework y django rest framework es para crear la API (endpoints)

django-admin startproject config . es para crear la carpeta de config, y tiene la base del backend del proyecto

python manage.py runserver ejecutar y montar el servidor

Configuracion de Nginx para el taller:
- El archivo nginx.conf en la raiz enruta /api/v1/ hacia Django (servicio django:8000).
- Nginx reescribe /api/v1/... hacia /api/... porque Django hoy no usa versionado en sus URLs internas.
- La ruta estrangulada principal /api/v2/payments se envia al microservicio de pagos (servicio payment-service:8080).
- La ruta /api/v2/payments sin slash final tambien se proxyea directamente para coincidir con el endpoint POST definido en Flask.
- Se mantiene compatibilidad con /api/v2/pagos para redirigir o reescribir hacia /api/v2/payments.
- Todo el trafico restante, incluyendo /, /static/ y /media/, permanece en Django.
- Cuando integren docker-compose.yml, los nombres de servicio deben coincidir con django y payment-service o ajustar los upstreams del archivo.

Snippet sugerido para docker-compose:
- Revisar docker-compose.nginx.snippet.yml para agregar el servicio nginx cuando integren Docker.

Configuración local opcional:
- Crea un archivo `.env.local` en la raíz del proyecto.
- Para habilitar Google Maps en seguimiento y publicar, define `GOOGLE_MAPS_API_KEY=tu_api_key`.

Estos comandos fueron para crear modulos de la aplicación, ya con los archivos necesarios para agregar la logica del modulo 
python manage.py startapp accounts
python manage.py startapp trust
python manage.py startapp geo
python manage.py startapp market
python manage.py startapp payments
python manage.py startapp transactions
python manage.py startapp notifications
python manage.py startapp ratings

INSTALLED_APPS que se encuentra en: config\settings.py. Sirve para decirle a Django qué módulos están activos en el proyecto, agregué estos:

AUTH_USER_MODEL = "accounts.User" 
Es indicarle a django que usaremos un modelo personalizado, no el predeterminado que tiene django

python manage.py makemigrations accounts
python manage.py migrate

---------------------------------
NOTIFACTIONS
factories.py -> NotificacionFactory es donde esta toda la creacion de cualquier tipo de noti y lo guarda 
services.py -> NotificacionService esta toda la logica de la gestion de las notis con 
        enviar() que es crear una notificación para un usuario
        marcar_leida() busca la noti en la db y le cambia el estado
        obtener_usuario()  obtiene todas las notificaciones del usuario
serializer.py -> el objeto tipo Notificacion de models lo converte en json con id,tipo,mensaje
view.py-> Reune los emtodos anteriores solo para usarlos de acuerdo al get/post pero no calcula nada de logica del negocio
        MarcarNotificacionLeidaView() -> crea un endpoint recibe el id de la noti, llama al service y esta ya mira si esta leida-> no lo marca sino lo marca, luego la view envia el resultado en http
        MisNotificacionesView()-> toma del get se obitene el id del usrio y se buscan sus notificaciones devuelve lista de notis




HU1:
Ingresar nombre, email y contraseña: el request lo recibe RegisterInputSerializer (nombre, email, password) en serializers.py.
Guardar en base de datos: AccountService.register_user() crea el User y hace user.save() en services.py.
No permitir email duplicado: email es unique=True en el modelo y además se valida con exists() y se responde 409 (Conflict) si ya existe en models.py y services.py.
Fecha de registro automática: fecha_registro = DateTimeField(auto_now_add=True) en models.py.
Endpoint

Registro: POST /registro y POST /api/registro (ambos funcionan) en urls.py y urls.py.

HU2:

Puede ingresar email y contraseña: LoginInputSerializer recibe email + password en serializers.py.
El sistema valida credenciales: AccountService.login() usa authenticate() y si falla devuelve 401 “Credenciales inválidas” en services.py y api_views.py.
Devuelve respuesta correcta si son válidas: POST /login (y también POST /api/login) responde 200 con { token, user } en api_views.py y rutas en urls.py + urls.py.
Autenticación configurada: el proyecto está configurado con Token Authentication (DRF authtoken) como auth principal en settings.py. (Es token-based, no JWT; si necesitas específicamente JWT, lo implemento.)

HU6:

Se crea pedido asociado a publicación: OrderService.create_order() crea Pedido con publicacion=... en services.py. El modelo tiene FK publicacion en models.py.
Relacionado con usuario: el pedido se crea con usuario=request.user (JWT + IsAuthenticated) en api_views.py y FK usuario en models.py.
Estado inicial = Pendiente/Aceptado: el modelo define estado por defecto PENDIENTE en models.py (cumple la opción “Pendiente”).
Guarda fecha de creación: fecha_creacion = auto_now_add=True en models.py.
Endpoint

Ya existía POST /api/pedidos en urls.py.
Agregué alias para que también funcione POST /pedidos (y variantes con /) en:
urls.py
urls.py


HU8:

Se guarda método y monto: el modelo Pago tiene metodo y monto en models.py.
Se asocia a pedido: Pago.pedido es ForeignKey a market.Pedido y el servicio crea el pago con ese pedido en models.py y services.py.
Tiene estado (Autorizado/Fallido): PaymentService.register_payment() setea estado="AUTORIZADO" o estado="FALLIDO" según el gateway en services.py.
Endpoint

Ya existía POST /api/pagos.
Agregué alias para que también funcione POST /pago (y variantes con /) en:
urls.py
urls.py

-------------------------------
NOTIFICATIONS
factories.py -> NotificacionFactory es donde esta toda la creacion de cualquier tipo de noti y lo guarda.
        Patrón Factory: valida que el tipo sea uno de {pedido, pago, cerca, sistema} antes de crear.
        Si el tipo no es válido lanza ValueError. 

services.py -> NotificacionService esta toda la logica de la gestion de las notis con:
        enviar() que es crear una notificación para un usuario — llama a NotificacionFactory.crear()
        marcar_leida() busca la noti en la db y le cambia el estado a leida=True, si ya estaba leída lanza ValueError
        obtener_usuario() obtiene todas las notificaciones del usuario ordenadas por fecha_envio desc
api/serializers.py -> el objeto tipo Notificacion de models lo convierte en json con id, tipo, mensaje, fecha_envio, leida, usuario

views.py -> Reune los metodos anteriores solo para usarlos de acuerdo al get/post pero no calcula nada de logica del negocio
        MarcarNotificacionLeidaView() -> POST /api/notificaciones/{id}/leer/ — recibe el id de la noti, llama al service,
            el service mira si esta leida: si lo está devuelve 400, sino la marca y devuelve 200 con el objeto actualizado

        MisNotificacionesView() -> GET /api/notificaciones/ — obtiene el usuario del token JWT, busca sus notificaciones,
            devuelve lista de notis en JSON


-->