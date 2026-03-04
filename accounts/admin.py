from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Este archivo lo que hace es conectar el modelo User con el panel de
# administración de Django
admin.site.register(User, UserAdmin)