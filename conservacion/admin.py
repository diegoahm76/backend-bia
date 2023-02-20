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
from conservacion.models.traslados_models import (
    TrasladosViveros,
    ItemsTrasladoViveros
)
from conservacion.models.siembras_models import (
    Siembras,
    ConsumosSiembra,
    CamasGerminacionVivero,
    CamasGerminacionViveroSiembra,
    CambiosDeEtapa
)
from conservacion.models.incidencias_models import (
    IncidenciasMatVegetal,
    ConsumosIncidenciasMV,
)
from conservacion.models.mezclas_models import (
    Mezclas,
    PreparacionMezclas,
    ItemsPreparacionMezcla
)
from conservacion.models.solicitudes_models import (
    SolicitudesViveros,
    ItemSolicitudViveros,
)
admin.site.register(Vivero)
admin.site.register(HistorialAperturaViveros)
admin.site.register(HistorialCuarentenaViveros)
admin.site.register(DespachoEntrantes)
admin.site.register(ItemsDespachoEntrante)
admin.site.register(DistribucionesItemDespachoEntrante)
admin.site.register(InventarioViveros)
admin.site.register(TrasladosViveros)
admin.site.register(ItemsTrasladoViveros)
admin.site.register(Siembras)
admin.site.register(ConsumosSiembra)
admin.site.register(CamasGerminacionVivero)
admin.site.register(CamasGerminacionViveroSiembra)
admin.site.register(CambiosDeEtapa)
admin.site.register(IncidenciasMatVegetal)
admin.site.register(ConsumosIncidenciasMV)
admin.site.register(Mezclas)
admin.site.register(PreparacionMezclas)
admin.site.register(ItemsPreparacionMezcla)
admin.site.register(SolicitudesViveros)
admin.site.register(ItemSolicitudViveros)
