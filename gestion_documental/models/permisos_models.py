from django.db import models
from gestion_documental.models.ccd_models import CatalogosSeriesUnidad
from transversal.models.organigrama_models import (
    UnidadesOrganizacionales
)

class PermisosUndsOrgActualesSerieExpCCD(models.Model):
    id_permisos_und_org_actual_serie_exp_ccd=models.AutoField(primary_key=True, editable=False, db_column='T221IdPermisos_UndOrgActual_SerieExp_CCD')
    id_cat_serie_und_org_ccd=models.ForeignKey(CatalogosSeriesUnidad, on_delete=models.CASCADE, db_column='T221Id_CatSerie_UndOrg_CCD')
    id_und_organizacional_actual=models.ForeignKey(UnidadesOrganizacionales, on_delete=models.SET_NULL, blank=True, null=True, db_column='T221Id_UndOrganizacionalActual')
    pertenece_seccion_actual_admin_serie=models.BooleanField(blank=True, null=True, db_column='T221perteneceASeccionActualAdminSerie')
    crear_expedientes=models.BooleanField(blank=True, null=True, db_column='T221crearExpedientes')
    crear_documentos_exps_no_propios=models.BooleanField(blank=True, null=True, db_column='T221crearDocumentosEnExpsNoPropios')
    anular_documentos_exps_no_propios=models.BooleanField(blank=True, null=True, db_column='T221anularDocumentosEnExpsNoPropios')
    borrar_documentos_exps_no_propios=models.BooleanField(blank=True, null=True, db_column='T221borrarDocumentosEnExpsNoPropios')
    conceder_acceso_documentos_exps_no_propios=models.BooleanField(blank=True, null=True, db_column='T221concederAccesoADocumentosEnExpsNoPropios')
    conceder_acceso_expedientes_no_propios=models.BooleanField(blank=True, null=True, db_column='T221concederAccesoAExpedientesNoPropios')
    consultar_expedientes_no_propios=models.BooleanField(blank=True, null=True, db_column='T221consultarExpedientesNoPropios')
    descargar_expedientes_no_propios=models.BooleanField(blank=True, null=True, db_column='T221descargarExpedientesNoPropios')
    denegar_anulacion_docs=models.BooleanField(blank=True, null=True, db_column='T221denegarAnulacionDeDocs')
    denegar_borrado_docs=models.BooleanField(blank=True, null=True, db_column='T221denegarBorradoDeDocs')
    excluir_und_actual_respon_series_doc_restriccion=models.BooleanField(blank=True, null=True, db_column='T221excluirUndActual_ResponSeriesDoc_DeRestriccion')
    denegar_conceder_acceso_doc_na_resp_series=models.BooleanField(blank=True, null=True, db_column='T221denegarConcederAccesoADocNARespSeries')
    denegar_conceder_acceso_exp_na_resp_series=models.BooleanField(blank=True, null=True, db_column='T221denegarConcederAccesoAExpNARespSeries')
    
    def __str__(self):
        return str(self.nombre)
    
    class Meta:
        db_table='T221Permisos_UndsOrgActuales_SerieExp_CCD'
        verbose_name='Permisos sobre Series de Expedientes de los CCD'
        verbose_name_plural='Permiso sobre Serie de Expedientes de los CCD'
        unique_together = ['id_cat_serie_und_org_ccd', 'id_und_organizacional_actual']