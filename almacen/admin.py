from django.contrib import admin
from almacen.models.organigrama_models import (
    Organigramas,
    NivelesOrganigrama,
    UnidadesOrganizacionales,
    Cargos
)
from gestion_documental.models.ccd_models import (
    CuadrosClasificacionDocumental,
    SubseriesDoc,
    SeriesDoc,
    SeriesSubseriesUnidadOrg
)
from almacen.models.generics_models import (
    Marcas,
    PorcentajesIVA,
    UnidadesMedida,
    Bodegas
)
from almacen.models.bienes_models import (
    MetodosValoracionArticulos,
    TiposDepreciacionActivos,
    TiposActivo,
    CatalogoBienes
)
from almacen.models.hoja_de_vida_models import (
    VehiculosArrendados,
    HojaDeVidaComputadores,
    HojaDeVidaVehiculos,
    HojaDeVidaOtrosActivos,
    DocumentosVehiculo
)
#from almacen.models.inventario_models import ()
from almacen.models.mantenimientos_models import (
    ProgramacionMantenimientos,
    RegistroMantenimientos
)

admin.site.register(Organigramas)
admin.site.register(NivelesOrganigrama)
admin.site.register(UnidadesOrganizacionales)
admin.site.register(Cargos)
admin.site.register(Marcas)
admin.site.register(PorcentajesIVA)
admin.site.register(UnidadesMedida)
admin.site.register(Bodegas)
admin.site.register(MetodosValoracionArticulos)
admin.site.register(TiposDepreciacionActivos)
admin.site.register(TiposActivo)
admin.site.register(VehiculosArrendados)
admin.site.register(HojaDeVidaComputadores)
admin.site.register(HojaDeVidaVehiculos)
admin.site.register(HojaDeVidaOtrosActivos)
admin.site.register(DocumentosVehiculo)
admin.site.register(ProgramacionMantenimientos)
admin.site.register(RegistroMantenimientos)
admin.site.register(CatalogoBienes)
