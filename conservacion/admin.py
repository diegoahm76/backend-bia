from django.contrib import admin
from conservacion.models.viveros_models import (
    Vivero, 
    HistorialAperturaViveros,
    HistorialCuarentenaViveros,
)
from conservacion.models.despachos_models import (
    DespachoEntrantes, 
    ItemsDespachoEntrante,
    DistribucionesItemDespachoEntrante,
)
from conservacion.models.inventario_models import (
    InventarioViveros,
)

admin.site.register(Vivero)
admin.site.register(HistorialAperturaViveros)
admin.site.register(HistorialCuarentenaViveros)
admin.site.register(DespachoEntrantes)
admin.site.register(ItemsDespachoEntrante)
admin.site.register(DistribucionesItemDespachoEntrante)
admin.site.register(InventarioViveros)