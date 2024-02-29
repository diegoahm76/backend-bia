from django.db import models
from seguridad.models import Personas
from almacen.models.generics_models import Marcas
from almacen.models.bienes_models import CatalogoBienes, EntradasAlmacen, Bodegas
from almacen.models.inventario_models import Inventario
from transversal.models.organigrama_models import UnidadesOrganizacionales
from gestion_documental.models.expedientes_models import ArchivosDigitales



class BajaActivos(models.Model):
    id_baja_activo = models.AutoField(primary_key=True, db_column="T086IdBajaActivo")
    consecutivo_por_baja = models.SmallIntegerField(unique=True,db_column='T086consecutivoXBaja')
    concepto = models.CharField(max_length=250, db_column="T086concepto")
    fecha_baja = models.DateTimeField(db_column='T086fechaBaja')
    cantidad_activos_baja = models.SmallIntegerField(unique=True,db_column='T086cantidadActivosDeBaja')
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
    id_arhcivo_digital = models.ForeignKey(ArchivosDigitales, on_delete=models.CASCADE, db_column='T087Id_ArchivoDigital')
    
    def __str__(self):
        return str(self.id_anexo_doc_alma)
    
    class Meta:
        db_table = 'T087AnexosDocsAlma'
        verbose_name = 'Anexo Doc Alma'
        verbose_name_plural = 'Anexos Docs Alma'


class ItemsBajaActivos(models.Model):
    id_item_baja_activo = models.AutoField(primary_key=True, db_column="T094IdItemBajaActivo")
    id_bien = models.ForeignKey(CatalogoBienes, on_delete=models.CASCADE, db_column='T094Id_Bien')
    id_baja_Activo = models.ForeignKey(BajaActivos, on_delete=models.CASCADE, db_column='T094Id_BajaActivo')
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