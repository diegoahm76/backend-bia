from django.db import models
from seguridad.models import Personas
from almacen.models.generics_models import Marcas, UnidadesMedida
from almacen.models.bienes_models import CatalogoBienes, EntradasAlmacen, Bodegas
from almacen.models.inventario_models import Inventario
from transversal.models.organigrama_models import UnidadesOrganizacionales
from gestion_documental.models.expedientes_models import ArchivosDigitales
from almacen.choices.estado_solicitud_activo_choices import estado_solicitud_activo_CHOICES
from almacen.choices.estado_aprobacion_activo_choices import estado_aprobacion_activo_CHOICES




class BajaActivos(models.Model):
    id_baja_activo = models.AutoField(primary_key=True, db_column="T086IdBajaActivo")
    consecutivo_por_baja = models.SmallIntegerField(unique=True,db_column='T086consecutivoXBaja')
    concepto = models.CharField(max_length=250, db_column="T086concepto")
    fecha_baja = models.DateTimeField(db_column='T086fechaBaja')
    cantidad_activos_baja = models.SmallIntegerField(db_column='T086cantidadActivosDeBaja')
    id_persona_registro_baja = models.ForeignKey(Personas, on_delete=models.CASCADE, db_column='T086Id_PersonaRegistroBaja')
    id_uni_org_registro_baja  = models.ForeignKey(UnidadesOrganizacionales, on_delete=models.CASCADE, db_column='T086Id_UnidadOrgRegistroBaja')

    def __str__(self):
        return str(self.id_baja_activo)
    
    class Meta:
        db_table = 'T086BajaActivos'
        verbose_name = 'Baja de Activo'
        verbose_name_plural = 'Bajas de Activos'


class SalidasEspecialesArticulos(models.Model):
    id_salida_espec_arti = models.AutoField(primary_key=True, db_column="T088IdSalidaEspecial_Articulo")
    consecutivo_por_salida = models.SmallIntegerField(unique=True,db_column='T088consecutivoXSalida')
    fecha_salida = models.DateTimeField(db_column='T088fechaSalida')
    referencia_salida = models.CharField(max_length=100, db_column="T088referenciaDeSalida")
    concepto = models.CharField(max_length=250, db_column="T088concepto")
    id_entrada_almacen_ref = models.ForeignKey(EntradasAlmacen, on_delete=models.CASCADE, db_column='T088Id_EntradaAlmacenReferenciada')

    def __str__(self):
        return str(self.id_salida_espec_arti)
    
    class Meta:
        db_table = 'T088SalidasEspeciales_Articulos'
        verbose_name = 'Salida Especial de Articulo'
        verbose_name_plural = 'Salidas Especiales de Articulos'



class AnexosDocsAlma(models.Model):
    id_anexo_doc_alma = models.AutoField(primary_key=True, db_column="T087IdAnexoDocAlma")
    id_baja_activo = models.ForeignKey(BajaActivos, on_delete=models.SET_NULL,null=True, blank=True, db_column='T087Id_BajaActivo')
    id_salida_espec_arti = models.ForeignKey(SalidasEspecialesArticulos,on_delete=models.SET_NULL, null=True, blank=True, db_column='T087Id_SalidaEspecial_Articulo')
    nombre_anexo = models.CharField(max_length=150, db_column="T087nombreDelAnexo")
    nro_folios = models.SmallIntegerField(db_column="T087nroFolios")
    descripcion_anexo = models.CharField(max_length=255, db_column="T087descripcionAnexo")
    fecha_creacion_anexo = models.DateTimeField(db_column='T087fechaCreacionAnexo')
    id_archivo_digital = models.ForeignKey(ArchivosDigitales, on_delete=models.CASCADE, db_column='T087Id_ArchivoDigital')
    
    def __str__(self):
        return str(self.id_anexo_doc_alma)
    
    class Meta:
        db_table = 'T087AnexosDocsAlma'
        verbose_name = 'Anexo Doc Alma'
        verbose_name_plural = 'Anexos Docs Alma'


class ItemsBajaActivos(models.Model):
    id_item_baja_activo = models.AutoField(primary_key=True, db_column="T094IdItemBajaActivo")
    id_bien = models.ForeignKey(CatalogoBienes, on_delete=models.CASCADE, db_column='T094Id_Bien')
    id_baja_activo = models.ForeignKey(BajaActivos, on_delete=models.CASCADE, db_column='T094Id_BajaActivo')
    codigo_bien = models.CharField(max_length=12, db_column="T094codigoBien")
    nombre = models.CharField(max_length=100, db_column="T094nombre")
    nombre_marca = models.CharField(max_length=50, db_column="T094nombreMarca")
    doc_identificador_nro = models.CharField(max_length=30, db_column="T094docIdentificadorNro")
    valor_unitario = models.DecimalField(max_digits=11, decimal_places=2, db_column='T094valorUnitario')
    justificacion_baja_activo = models.CharField(max_length=255, db_column="T094justificacionBajaActivo")
    
    def __str__(self):
        return str(self.id_item_baja_activo)
    
    class Meta:
        db_table = 'T094ItemsBajaActivos'
        verbose_name = 'item baja Activo'
        verbose_name_plural = 'items bajas Activos'



class SolicitudesActivos(models.Model):
    id_solicitud_viaje = models.AutoField(primary_key=True, db_column="T090IdSolicitudActivo")
    fecha_solicitud = models.DateTimeField(db_column='T090fechaSolicitud')
    motivo = models.CharField(max_length=255, db_column="T090motivo")
    observacion = models.CharField(max_length=255, blank=True, null=True, db_column="T090observacion")
    id_persona_solicita = models.ForeignKey(Personas, related_name='id_persona_solicita', on_delete=models.CASCADE, db_column='T090Id_PersonaSolicita')
    id_uni_org_solicitante = models.ForeignKey(UnidadesOrganizacionales, related_name='id_uni_org_del_solicitante',on_delete=models.CASCADE, db_column='T090Id_UnidadOrgDelSolicitante')
    id_funcionario_resp_unidad = models.ForeignKey(Personas, related_name='id_funcionario_resp_unidad', on_delete=models.CASCADE, db_column='T090Id_FuncionarioResponsableUnidad')
    id_uni_org_responsable = models.ForeignKey(UnidadesOrganizacionales, related_name='id_uni_org_del_responsanble',on_delete=models.CASCADE, db_column='T090Id_UnidadOrgDelResponsable')
    id_persona_operario = models.ForeignKey(Personas, related_name='id_persona_operario', on_delete=models.CASCADE, db_column='T090Id_PersonaOperario')
    id_uni_org_operario = models.ForeignKey(Personas, related_name='id_uni_org_operario', on_delete=models.CASCADE, db_column='T090Id_UnidadOrgOperario')
    estado_solicitud = models.CharField(max_length=2, choices=estado_solicitud_activo_CHOICES, db_column="T090estadoSolicitud")
    solicitud_prestamo = models.BooleanField(db_column="T090solicitudPrestamo")
    fecha_devolucion = models.DateTimeField(blank=True, null=True,db_column='T090fechaDevolucion')
    fecha_cierra_solicitud = models.DateTimeField(db_column='T090fechaCierreSolicitud')
    revisada_responble = models.BooleanField(db_column="T090revisadaResponsable")
    estado_aprobacion_resp = models.CharField(max_length=2, choices=estado_aprobacion_activo_CHOICES, db_column="T090estadoAprobacionResponsable")
    justificacion_rechazo_resp = models.CharField(max_length=255, blank=True, null=True, db_column="T090justificacionRechazoResponsable")
    fecha_aprobacion_resp = models.DateTimeField(blank=True, null=True,db_column='T090fechaAprobacionResponsable')
    gestionada_alma = models.BooleanField(db_column="T090gestionadaAlmacen")
    obser_cierre_no_dispo_alma = models.CharField(max_length=255, blank=True, null=True, db_column="T090ObservCierreNoDispoAlm")
    fecha_cierre_no_dispo_alma = models.DateTimeField(blank=True, null=True,db_column='T090fechaCierreNoDispoAlm')
    id_persona_cierra_no_dispo_alma = models.ForeignKey(Personas, related_name='id_persona_cierra_no_dispo_alma', on_delete=models.CASCADE, db_column='T090Id_PersonaCierreNoDispoAlm')
    rechazada_almacen = models.BooleanField(db_column="T090rechazadaAlmacen")
    fecha_rechazo_almacen = models.DateTimeField(blank=True, null=True,db_column='T090fechaRechazoAlmacen')
    justificacion_rechazo_almacen = models.CharField(max_length=255, blank=True, null=True, db_column="T090justificacionRechazoAlmacen")
    id_persona_alma_rechaza = models.ForeignKey(Personas, related_name='id_persona_alma_rechaza', on_delete=models.SET_NULL, blank=True, null=True, db_column='T090Id_PersonaAlmacenRechaza')
    solicitud_anulada_solicitante = models.BooleanField(db_column="T090solicitudAnuladaSolicitante")
    fecha_anulacion_solicitante = models.DateTimeField(blank=True, null=True,db_column='T090fechaAnulacionSolicitante')

    def __str__(self):
        return str(self.id_solicitud_viaje)
    
    class Meta:
        db_table = 'T090SolicitudesActivos'
        verbose_name = 'Solicitud Activo'
        verbose_name_plural = 'Solicitudes Activos'


class ItemsSolicitudActivos(models.Model):
    id_item_solicitud_activo = models.AutoField(primary_key=True, db_column="T091IdItem_SolicitudActivo")
    id_solicitud_activo = models.ForeignKey(SolicitudesActivos, on_delete=models.CASCADE,null=True, blank=True, db_column='T091Id_SolicitudActivos')
    id_bien = models.ForeignKey(CatalogoBienes, on_delete=models.CASCADE, db_column='T091Id_Bien')
    cantidad = models.SmallIntegerField(db_column="T091cantidad")
    id_unidad_medida = models.ForeignKey(UnidadesMedida, on_delete=models.CASCADE, db_column='T091Id_UnidadMedida ')
    observacion = models.CharField(max_length=255, blank=True, null=True, db_column="T091observaciones")
    nro_posicion = models.SmallIntegerField(db_column="T091nroPosicion")

    def __str__(self):
        return str(self.id_item_solicitud_activo)
    
    class Meta:
        db_table = 'T091Items_SolicitudActivos'
        verbose_name = 'Item Solicitud Activo'
        verbose_name_plural = 'Items Solicitudes Activos'