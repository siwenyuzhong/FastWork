from django.contrib import admin

# Register your models here.
from rbac.models import Menu, Role

admin.site.register(Menu)
admin.site.register(Role)
