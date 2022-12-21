from django.db import models
from seguridad.choices.municipios_choices import municipios_CHOICES
from almacen.choices.estados_articulo_choices import estados_articulo_CHOICES
from almacen.choices.tipos_activo_choices import tipos_activo_CHOICES
from almacen.choices.cod_tipo_bien_choices import cod_tipo_bien_CHOICES
from almacen.choices.metodos_valoracion_articulos_choices import metodos_valoracion_articulos_CHOICES
from almacen.choices.tipos_depreciacion_activos_choices import tipos_depreciacion_activos_CHOICES
# from seguridad.models import Personas
from almacen.models import Marcas, UnidadesMedida, PorcentajesIVA, Bodegas
from django.core.validators import MaxValueValidator, MinValueValidator

class CatalogoBienes(models.Model):
    id_bien = models.AutoField(primary_key=True, db_column='T057IdBien')
    codigo_bien = models.CharField(max_length=12, db_column='T057codigoBien')
    nro_elemento_bien = models.PositiveSmallIntegerField(null=True, blank=True, db_column='T057nroElementoEnElBien')
    nombre = models.CharField(max_length=100, db_column='T057nombre')
    cod_tipo_bien = models.CharField(max_length=1, choices=cod_tipo_bien_CHOICES, db_column='T057codTipoBien')
    cod_tipo_activo = models.CharField(max_length=3, choices=tipos_activo_CHOICES, null=True, blank=True, db_column='T057Cod_TipoActivo')
    nivel_jerarquico = models.PositiveSmallIntegerField(validators=[MaxValueValidator(5), MinValueValidator(1)], db_column='T057nivelJerarquico')
    nombre_cientifico = models.CharField(max_length=255, null=True, blank=True, db_column='T057nombreCientifico')
    descripcion = models.CharField(max_length=255, null=True, blank=True, db_column='T057descripcion')
    doc_identificador_nro = models.CharField(max_length=30, null=True, blank=True, db_column='T057docIdentificadorNro')
    id_marca = models.ForeignKey(Marcas, on_delete=models.SET_NULL, null=True, blank=True, db_column='T057Id_Marca')
    id_unidad_medida = models.ForeignKey(UnidadesMedida, related_name='unidad_medida', on_delete=models.CASCADE, db_column='T057Id_UnidadMedida')
    id_porcentaje_iva = models.ForeignKey(PorcentajesIVA, on_delete=models.CASCADE, db_column='T057Id_PorcentajeIVA')
    cod_metodo_valoracion = models.PositiveSmallIntegerField(choices=metodos_valoracion_articulos_CHOICES, null=True, blank=True, db_column='T057Cod_MetodoValoracion')
    cod_tipo_depreciacion = models.PositiveSmallIntegerField(choices=tipos_depreciacion_activos_CHOICES, null=True, blank=True, db_column='T057Cod_TipoDepreciacion')
    cantidad_vida_util = models.PositiveSmallIntegerField(null=True, blank=True, db_column='T057cantidadVidaUtil')
    id_unidad_medida_vida_util = models.ForeignKey(UnidadesMedida, related_name='unidad_medida_vida_util', on_delete=models.SET_NULL, null=True, blank=True, db_column='T057Id_UnidadMedidaVidaUtil')
    valor_residual = models.FloatField(null=True, blank=True, db_column='T057valorResidual')
    stock_minimo = models.PositiveSmallIntegerField(null=True, blank=True, db_column='T057stockMinimo')
    stock_maximo = models.PositiveIntegerField(null=True, blank=True, db_column='T057stockMaximo')
    solicitable_vivero = models.BooleanField(default=False, db_column='T057solicitablePorVivero')
    tiene_hoja_vida = models.BooleanField(null=True, blank=True, db_column='T057tieneHojaDeVida')
    id_bien_padre = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, db_column='T057Id_BienPadre')
    maneja_hoja_vida = models.BooleanField(default=False, db_column='T057manejaHojaDeVida')
    visible_solicitudes = models.BooleanField(default=False, db_column='T057visibleEnSolicitudes')
    
    def __str__(self):
        return str(self.nombre)

    class Meta:
        db_table = 'T057CatalogoBienes'
        verbose_name = 'Catalogo Bien'
        verbose_name_plural = 'Catalogo Bienes'
        unique_together = ['codigo_bien', 'nro_elemento_bien']

class EstadosArticulo(models.Model):
    cod_estado = models.CharField(max_length=1, primary_key=True, unique=True, db_column='T051Cod_Estado')
    nombre = models.CharField(max_length=20, db_column='T051nombre')

    def __str__(self):
        return str(self.nombre)

    class Meta:
        db_table = 'T051EstadosArticulo'
        verbose_name = 'Estado artículo'
        verbose_name_plural = 'Estados artículos'
        
class MetodosValoracionArticulos(models.Model):
    cod_metodo_valoracion = models.AutoField(primary_key=True, db_column='T058CodMetodoValoracion')
    nombre = models.CharField(max_length=50, db_column='T058nombre', unique=True)
    descripcion = models.CharField(max_length=255, db_column='T058descripccion', blank=True, null=True)
    
    def __str__(self):
        return str(self.nombre)

    class Meta:
        db_table = 'T058MetodosValoracionArticulos'
        verbose_name = 'Metodo valoracion articulo'
        verbose_name_plural = 'Metodos valoracion articulo'

class TiposDepreciacionActivos(models.Model):
    cod_tipo_depreciacion = models.AutoField(primary_key=True, db_column='T059CodTipoDepreciacion')
    nombre = models.CharField(max_length=50, db_column='T059nombre', unique=True)

    def __str__(self):
        return str(self.nombre)

    class Meta:
        db_table = 'T059TiposDepreciacionActivos'
        verbose_name = 'Tipo Depreciacion Activos'
        verbose_name_plural = 'Tipos Depreciacion Activos'

class TiposActivo(models.Model):
    cod_tipo_activo = models.CharField(primary_key=True, choices=tipos_activo_CHOICES, max_length=3, db_column='T060CodTipoActivo')
    nombre = models.CharField(max_length=30, db_column='T060nombre', unique=True)

    def __str__(self):
        return str(self.nombre)

    class Meta:
        db_table = 'T060TiposActivo'
        verbose_name = 'Tipo Activos'
        verbose_name_plural = 'Tipos Activos'

class EntradasAlmacen(models.Model):
    id_entrada_almacen = models.AutoField(primary_key=True, editable=False, db_column='T063IdEntradaAlmacen')
    numero_entrada_almacen = models.PositiveIntegerField(db_column='T063nroEntradaAlmacen')	
    fecha_entrada = models.DateTimeField(db_column='T063fechaEntrada')
    fecha_real_registro = models.DateTimeField(auto_now=True, db_column='T063fechaRealRegistro')
    motivo = models.CharField(max_length=255,db_column='T063motivo')
    observacion = models.CharField( max_length=255,db_column='T063observacion',blank=True,null=True)
    id_proveedor= models.ForeignKey('seguridad.Personas', related_name='persona_provee_entrada', on_delete=models.CASCADE, db_column='T063Id_Proveedor')
    id_tipo_entrada = models.ForeignKey('almacen.TiposEntradas', on_delete=models.CASCADE, db_column='T063Cod_TipoEntrada')
    id_bodega = models.ForeignKey(Bodegas, on_delete=models.CASCADE, db_column='T063Id_BodegaGral')	
    valor_total_entrada = models.DecimalField(max_digits=12,decimal_places=2, db_column='T063valorTotalEntrada')
    id_creador = models.ForeignKey('seguridad.Personas', related_name='persona_crea_entrada', on_delete=models.CASCADE, db_column='T063Id_PersonaCrea')	
    id_persona_ult_act_dif_creador = models.ForeignKey('seguridad.Personas', related_name='persona_actualiza_entrada', on_delete=models.SET_NULL, blank=True, null=True, db_column='T063Id_PersonaUltActualizacionDifACrea')			
    fecha_ultima_actualizacion_diferente_creador= models.DateTimeField(null=True,blank=True, db_column='T063fechaUltActualizacionDifACrea')	
    entrada_anulada= models.BooleanField(null=True, blank=True,db_column='T063entradaAnulada') 
    justificacion_anulacion=models.CharField(max_length=255,blank=True,null=True,db_column='T063justificacionAnulacion') 
    fecha_anulacion=models.DateTimeField(null=True, blank=True, db_column='T063fechaAnulacion')
    id_persona_anula=models.ForeignKey('seguridad.Personas',related_name='persona_anula_entrada',on_delete=models.SET_NULL, blank=True, null=True, db_column='T063Id_PersonaAnula')

    def __str__(self):
        return str(self.id_entrada_almacen)

    class Meta:
        db_table = 'T063EntradasAlmacen'
        verbose_name = 'Entrada de Almacen'
        verbose_name_plural = 'Entradas de Almacen'

class ItemEntradaAlmacen(models.Model):
    id_item_entrada_almacen = models.AutoField(primary_key=True, editable=False, db_column='T064IdItem_EntradaAlmacen')
    id_entrada_almacen = models.ForeignKey(EntradasAlmacen, on_delete=models.CASCADE, db_column='T064Id_EntradaAlmacen')
    id_bien = models.ForeignKey(CatalogoBienes, on_delete=models.CASCADE, db_column='T064Id_Bien')
    cantidad = models.PositiveIntegerField(db_column='T064cantidad')
    valor_unitario = models.DecimalField(max_digits=9,decimal_places=2,db_column='T064valorUnitario')
    porcentaje_iva = models.ForeignKey(PorcentajesIVA, on_delete=models.CASCADE, db_column='T064porcentajeIVA')
    valor_iva = models.DecimalField(max_digits=9,decimal_places=2,db_column='T064valorIVA')
    valor_total_item = models.DecimalField(max_digits=9,decimal_places=2,db_column='T064valorTotalItem')
    id_bodega = models.ForeignKey(Bodegas, on_delete=models.CASCADE, db_column='T064Id_Bodega')
    cod_estado = models.CharField(max_length=1, choices=estados_articulo_CHOICES, db_column='T064Cod_Estado')
    doc_identificador_bien= models.CharField(max_length=30, blank=True, null=True, db_column='T064docIdentificadorBien')
    cantidad_vida_util= models.PositiveSmallIntegerField(blank=True,  null=True, db_column='T064cantidadVidaUtil')
    id_unidad_medida_vida_util= models.ForeignKey(UnidadesMedida,on_delete=models.SET_NULL,blank=True,null=True,db_column='T064Id_UnidadMedidaVidaUtil')
    valor_residual = models.DecimalField(max_digits=10, decimal_places=0, db_column='T064valorResidual',blank=True,null=True)
    numero_posicion = models.PositiveSmallIntegerField(db_column='T064nroPosicion')

    def __str__(self):
        return str(self.id_item_entrada_almacen)

    class Meta:
        db_table = 'T064Items_EntradaAlmacen'
        verbose_name = 'Items entrada de Almacen'
        verbose_name_plural = 'Items de Entradas de Almacen'	
	