from django.contrib import admin
from gestion_documental.models.radicados_models import PQRSDF, Anexos, Anexos_PQR, ComplementosUsu_PQR, Estados_PQR, EstadosSolicitudes, MetadatosAnexosTmp, T262Radicados
from gestion_documental.models.trd_models import (
    TablaRetencionDocumental,
    TiposMediosDocumentos,
    FormatosTiposMedio,
    TipologiasDoc,
    FormatosTiposMedioTipoDoc,
    DisposicionFinalSeries,
    CatSeriesUnidadOrgCCDTRD,
    SeriesSubSUnidadOrgTRDTipologias,
    HistoricosCatSeriesUnidadOrgCCDTRD,
)
from gestion_documental.models.ccd_models import (
    CuadrosClasificacionDocumental,
    SubseriesDoc,
    SeriesDoc,
    CatalogosSeries,
    CatalogosSeriesUnidad,
)
from gestion_documental.models.tca_models import (
    TablasControlAcceso,
    ClasificacionExpedientes,
    # PermisosGD,
    CatSeriesUnidadOrgCCD_TRD_TCA,
    HistoricoCatSeriesUnidadOrgCCD_TRD_TCA,
    # PermisosCatSeriesUnidadOrgTCA,
    # PermisosDetPermisosCatSerieUndOrgTCA,
    # HistoricoPermisosCatSeriesUndOrgTCA
)

#CCD
admin.site.register(CuadrosClasificacionDocumental),
admin.site.register(SubseriesDoc),
admin.site.register(SeriesDoc),
admin.site.register(CatalogosSeries),
admin.site.register(CatalogosSeriesUnidad),

#TRD
admin.site.register(TablaRetencionDocumental),
admin.site.register(TipologiasDoc),
admin.site.register(TiposMediosDocumentos),
admin.site.register(FormatosTiposMedio),
admin.site.register(FormatosTiposMedioTipoDoc),
admin.site.register(CatSeriesUnidadOrgCCDTRD),
admin.site.register(SeriesSubSUnidadOrgTRDTipologias),
admin.site.register(HistoricosCatSeriesUnidadOrgCCDTRD)

#TCA
admin.site.register(TablasControlAcceso),
admin.site.register(ClasificacionExpedientes),
# admin.site.register(PermisosGD),
admin.site.register(CatSeriesUnidadOrgCCD_TRD_TCA),
admin.site.register(HistoricoCatSeriesUnidadOrgCCD_TRD_TCA),
# admin.site.register(PermisosCatSeriesUnidadOrgTCA),
# admin.site.register(PermisosDetPermisosCatSerieUndOrgTCA),
# admin.site.register(HistoricoPermisosCatSeriesUndOrgTCA)

#PQRS
admin.site.register(EstadosSolicitudes)
admin.site.register(PQRSDF)
admin.site.register(T262Radicados)
admin.site.register(Estados_PQR)
admin.site.register(Anexos_PQR)
admin.site.register(Anexos)
admin.site.register(MetadatosAnexosTmp)
admin.site.register(ComplementosUsu_PQR)