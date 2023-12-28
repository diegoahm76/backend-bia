from django.contrib import admin

from recaudo.models.base_models import (
    NaturalezaJuridica,
    Ubicaciones,
    RangosEdad,
    TiposBien,
    TiposPago,
    TipoActuacion,
    LeyesLiquidacion
)

from recaudo.models.cobros_models import (
    DocumentosCobro,
    DetalleDocumentosCobro,
    Deudores,
    Cartera,
    ConceptoContable
)

from recaudo.models.garantias_models import (
    RolesGarantias,
    Garantias
)

from recaudo.models.procesos_models import (
    Bienes,
    Avaluos,
    EtapasProceso,
    AtributosEtapas,
    Procesos,
    ValoresProceso,
    FlujoProceso,
    TiposAtributos,
    CategoriaAtributo
)

from recaudo.models.facilidades_pagos_models import (
    FacilidadesPago,
    RequisitosActuacion,
    CumplimientoRequisitos,
    DetallesFacilidadPago,
    GarantiasFacilidad,
    RespuestaSolicitud
)

from recaudo.models.liquidaciones_models import (
    OpcionesLiquidacionBase,
    LiquidacionesBase,
    DetalleLiquidacionBase,
    Expedientes
)

#Base
admin.site.register(NaturalezaJuridica),
admin.site.register(Ubicaciones),
admin.site.register(RangosEdad),
admin.site.register(TiposBien),
admin.site.register(TiposPago),
admin.site.register(TipoActuacion),
admin.site.register(LeyesLiquidacion),

#Cobros
admin.site.register(DocumentosCobro),
admin.site.register(DetalleDocumentosCobro),
admin.site.register(Deudores),
admin.site.register(Expedientes),
admin.site.register(Cartera),
admin.site.register(ConceptoContable),

#Garantias
admin.site.register(RolesGarantias),
admin.site.register(Garantias),

#Liquidaciones
admin.site.register(OpcionesLiquidacionBase),
admin.site.register(LiquidacionesBase),
admin.site.register(DetalleLiquidacionBase),

#Pagos
admin.site.register(FacilidadesPago),
admin.site.register(RequisitosActuacion),
admin.site.register(CumplimientoRequisitos),
admin.site.register(DetallesFacilidadPago),
admin.site.register(GarantiasFacilidad),
admin.site.register(RespuestaSolicitud),

#Procesos
admin.site.register(Bienes),
admin.site.register(Avaluos),
admin.site.register(EtapasProceso),
admin.site.register(AtributosEtapas),
admin.site.register(Procesos),
admin.site.register(ValoresProceso),
admin.site.register(FlujoProceso),
admin.site.register(TiposAtributos),
admin.site.register(CategoriaAtributo)
