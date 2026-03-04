<!--  
se usó python -m venv venv sirve para crear un entorno virtual, esto es para almacenar 
todas las librerías de ese proyecto

venv\Scripts\activate esto es para activar el entorno virtual

pip install django djangorestframework es para descargar django, la estructura basica del framework y django rest framework es para crear la API (endpoints)

django-admin startproject config . es para crear la carpeta de config, y tiene la base del backend del proyecto

python manage.py runserver ejecutar y montar el servidor

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




-->
