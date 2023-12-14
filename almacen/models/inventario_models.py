from django.db import models
from transversal.choices.municipios_choices import municipios_CHOICES
from almacen.choices.magnitudes_choices import magnitudes_CHOICES
from almacen.choices.tipo_doc_ultimo_choices import tipo_doc_ultimo_CHOICES
from almacen.choices.estados_articulo_choices import estados_articulo_CHOICES
# from seguridad.models import Personas
from almacen.models.bienes_models import (
    CatalogoBienes,
    EstadosArticulo
)
from almacen.models.generics_models import (
    Bodegas,
)

class TiposEntradas(models.Model):
    cod_tipo_entrada = models.SmallIntegerField(primary_key=True, editable=False, db_column='T061CodTipoEntrada')
    nombre = models.CharField(max_length=15, unique=True, db_column='T061nombre')
    descripcion = models.CharField(max_length=255, db_column='T061descripcion')
    titulo_persona_origen = models.CharField(max_length=20, db_column='T061tituloPersonaOrigen')
    constituye_propiedad = models.BooleanField(default=False, db_column='T061constituyePropiedad')

    def __str__(self):
        return str(self.nombre)

    class Meta:
        db_table = 'T061TiposEntrada'
        verbose_name = 'Tipo Entrada'
        verbose_name_plural = 'Tipos Entradas'


class Inventario(models.Model):
    id_inventario = models.AutoField(primary_key=True, editable=False, db_column='T062IdInventario')
    id_bien = models.ForeignKey(CatalogoBienes, on_delete=models.CASCADE, db_column='T062Id_Bien')
    id_bodega = models.ForeignKey(Bodegas, on_delete=models.CASCADE, db_column='T062Id_Bodega')
    cod_tipo_entrada = models.ForeignKey(TiposEntradas, on_delete=models.SET_NULL, null=True, blank=True, db_column='T062Cod_TipoEntrada')
    fecha_ingreso = models.DateField(null=True, blank=True, db_column='T062fechaIngreso')
    id_persona_origen = models.ForeignKey('transversal.Personas', related_name='persona_origen', on_delete=models.SET_NULL, null=True, blank=True, db_column='T062Id_PersonaOrigen')
    numero_doc_origen = models.CharField(max_length=30, null=True, blank=True, db_column='T062numeroDocOrigen')
    valor_ingreso = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, db_column='T062valorAlIngreso')
    realizo_baja = models.BooleanField(null=True, blank=True, db_column='T062realizoBaja')
    realizo_salida = models.BooleanField(null=True, blank=True, db_column='T062realizoSalida')
    ubicacion_en_bodega = models.BooleanField(null=True, blank=True, db_column='T062ubicacionEnBodega')
    ubicacion_asignado = models.BooleanField(null=True, blank=True, db_column='T062ubicacionAsignado')
    ubicacion_prestado = models.BooleanField(null=True, blank=True, db_column='T062ubicacionPrestado')
    id_persona_responsable = models.ForeignKey('transversal.Personas', related_name='persona_responsable', on_delete=models.SET_NULL, null=True, blank=True, db_column='T062Id_PersonaResponsable')
    cod_estado_activo = models.ForeignKey(EstadosArticulo, on_delete=models.SET_NULL, null=True, blank=True, db_column='T062Cod_EstadoDelActivo')
    fecha_ultimo_movimiento = models.DateTimeField(null=True, blank=True, db_column='T062fechaUltimoMov')
    tipo_doc_ultimo_movimiento = models.CharField(max_length=5,choices=tipo_doc_ultimo_CHOICES,null=True, blank=True, db_column='T062tipoDocUltimoMov')
    id_registro_doc_ultimo_movimiento = models.IntegerField(null=True, blank=True, db_column='T062IdRegEnDocUltimoMov')
    cantidad_entrante_consumo = models.IntegerField(null=True, blank=True, db_column='T062cantidadEntranteConsumo')
    cantidad_saliente_consumo = models.IntegerField(null=True, blank=True, db_column='T062cantidadSalienteConsumo')

    def __str__(self):
        return str(self.id_bien.nombre) + str(self.id_bodega.nombre) 
    
    class Meta:
        db_table = 'T062Inventario'
        verbose_name = 'Inventario'
        verbose_name_plural = 'Inventario'
        unique_together = ['id_bien', 'id_bodega']
