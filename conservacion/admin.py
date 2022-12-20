from django.contrib import admin
from conservacion.models.viveros_models import (
    Vivero, 
    HistorialAperturaViveros,
    HistorialCuarentenaViveros,
)

admin.site.register(Vivero)
admin.site.register(HistorialAperturaViveros)
admin.site.register(HistorialCuarentenaViveros)
