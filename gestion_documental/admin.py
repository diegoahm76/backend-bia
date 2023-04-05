from django.contrib import admin
from gestion_documental.models.trd_models import (
    TablaRetencionDocumental,
    TiposMediosDocumentos,
    FormatosTiposMedio,
    TipologiasDocumentales,
    FormatosTiposMedioTipoDoc,
    DisposicionFinalSeries,
    SeriesSubSUnidadOrgTRD,
    SeriesSubSUnidadOrgTRDTipologias,
    HistoricosSerieSubSeriesUnidadOrgTRD,
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
    PermisosGD,
    Clasif_Serie_Subserie_Unidad_TCA,
    Historico_Clasif_S_Ss_UndOrg_TCA,
    Cargos_Unidad_S_Ss_UndOrg_TCA,
    PermisosCargoUnidadSerieSubserieUnidadTCA,
    HistoricoCargosUnidadSerieSubserieUnidadTCA
)

#CCD
admin.site.register(CuadrosClasificacionDocumental),
admin.site.register(SubseriesDoc),
admin.site.register(SeriesDoc),
admin.site.register(CatalogosSeries),
admin.site.register(CatalogosSeriesUnidad),

#TRD
admin.site.register(TablaRetencionDocumental),
admin.site.register(TipologiasDocumentales),
admin.site.register(TiposMediosDocumentos),
admin.site.register(FormatosTiposMedio),
admin.site.register(FormatosTiposMedioTipoDoc),
admin.site.register(SeriesSubSUnidadOrgTRD),
admin.site.register(SeriesSubSUnidadOrgTRDTipologias),
admin.site.register(HistoricosSerieSubSeriesUnidadOrgTRD)

#TCA
admin.site.register(TablasControlAcceso),
admin.site.register(ClasificacionExpedientes),
admin.site.register(PermisosGD),
admin.site.register(Clasif_Serie_Subserie_Unidad_TCA),
admin.site.register(Historico_Clasif_S_Ss_UndOrg_TCA),
admin.site.register(Cargos_Unidad_S_Ss_UndOrg_TCA),
admin.site.register(PermisosCargoUnidadSerieSubserieUnidadTCA),
admin.site.register(HistoricoCargosUnidadSerieSubserieUnidadTCA)