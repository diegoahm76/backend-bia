from django.db import models
from gestion_documental.models.ccd_models import CatalogosSeriesUnidad, CuadrosClasificacionDocumental
from gestion_documental.models.tca_models import ClasificacionExpedientes

class CtrlAccesoClasificacionExpCCD(models.Model):
    id_ctrl_acceso_clasif_exp_ccd = models.AutoField(primary_key=True, editable=False, db_column='T222IdCtrlAcceso_ClasifExp_CCD')
    id_ccd = models.ForeignKey(CuadrosClasificacionDocumental, on_delete=models.CASCADE, db_column='T222Id_CCD')
    cod_clasificacion_exp = models.ForeignKey(ClasificacionExpedientes, on_delete=models.SET_NULL, null=True, blank=True, db_column='T222Cod_ClasificacionExp')
    id_cat_serie_und_org_ccd = models.ForeignKey(CatalogosSeriesUnidad, on_delete=models.SET_NULL, null=True, blank=True, db_column='T222Id_CatSerie_UndOrg_CCD')
    entidad_entera_consultar = models.BooleanField(null=True, blank=True, db_column='T222entidadEntera_Consultar')
    entidad_entera_descargar = models.BooleanField(null=True, blank=True, db_column='T222entidadEntera_Descargar')
    seccion_actual_respon_serie_doc_consultar = models.BooleanField(null=True, blank=True, db_column='T222seccionActualResponSerieDoc_Consultar')
    seccion_actual_respon_serie_doc_descargar = models.BooleanField(null=True, blank=True, db_column='T222seccionActualResponSerieDoc_Descargar')
    seccion_raiz_organi_actual_consultar = models.BooleanField(null=True, blank=True, db_column='T222seccionRaizDelOrganiActual_Consultar')
    seccion_raiz_organi_actual_descargar = models.BooleanField(null=True, blank=True, db_column='T222seccionRaizDelOrganiActual_Descargar')
    secciones_actuales_mismo_o_sup_nivel_respon_consulta = models.BooleanField(null=True, blank=True, db_column='T222seccionesActualesMismoOSupNivelALaRespon_Consultar')
    secciones_actuales_mismo_o_sup_nivel_respon_descargar = models.BooleanField(null=True, blank=True, db_column='T222seccionesActualesMismoOSupNivelALaRespon_Descargar')
    secciones_actuales_inf_nivel_respon_consultar = models.BooleanField(null=True, blank=True, db_column='T222seccionesActualesInfNivelALaRespon_Consultar')
    secciones_actuales_inf_nivel_respon_descargar = models.BooleanField(null=True, blank=True, db_column='T222seccionesActualesInfNivelALaRespon_Descargar')
    unds_org_sec_respon_mismo_o_sup_nivel_resp_exp_consultar = models.BooleanField(null=True, blank=True, db_column='T222undsOrgEnSecRespon_MismoOSupNivelAUndRespExp_Consultar')
    unds_org_sec_respon_mismo_o_sup_nivel_resp_exp_descargar = models.BooleanField(null=True, blank=True, db_column='T222undsOrgEnSecRespon_MismoOSupNivelAUndRespExp_Descargar')
    unds_org_sec_respon_inf_nivel_resp_exp_consultar = models.BooleanField(null=True, blank=True, db_column='T222undsOrgEnSecRespon_InfNivelAUndRespExp_Consultar')
    unds_org_sec_respon_inf_nivel_resp_exp_descargar = models.BooleanField(null=True, blank=True, db_column='T222undsOrgEnSecRespon_InfNivelAUndRespExp_Descargar')

    def __str__(self):
        return str(self.id_ctrl_acceso_clasif_exp_ccd)
    
    class Meta:
        db_table='T222CtrlAcceso_ClasificacionExp_CCD'
        verbose_name='Control de Acceso de Expediente de CCD'
        verbose_name_plural='Control de Acceso de Expedientes de los CCD'
        unique_together = [('id_ccd','cod_clasificacion_exp','id_cat_serie_und_org_ccd')]