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
    SeriesSubseriesUnidadOrg,
)
from gestion_documental.models.tca_models import (
    TablasControlAcceso,
    ClasificacionSeriesSubDoc,
    PermisosGD,
    CCD_Clasif_Serie_Subserie_TCA
)

#CCD
admin.site.register(CuadrosClasificacionDocumental),
admin.site.register(SubseriesDoc),
admin.site.register(SeriesDoc),
admin.site.register(SeriesSubseriesUnidadOrg),

#TRD
admin.site.register(TablaRetencionDocumental),
admin.site.register(TipologiasDocumentales),
admin.site.register(TiposMediosDocumentos),
admin.site.register(FormatosTiposMedio),
admin.site.register(FormatosTiposMedioTipoDoc),
admin.site.register(SeriesSubSUnidadOrgTRD),
admin.site.register(SeriesSubSUnidadOrgTRDTipologias),
admin.site.register(HistoricosSerieSubSeriesUnidadOrgTRD)
