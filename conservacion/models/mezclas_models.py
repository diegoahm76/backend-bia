from almacen.models.bienes_models import CatalogoBienes
from transversal.models.personas_models import Personas
from conservacion.models.viveros_models import Vivero
from django.db import models
from almacen.models import  UnidadesMedida

class Mezclas(models.Model):
    id_mezcla = models.AutoField(primary_key=True, editable=False, db_column='T168IdMezcla')
    nombre = models.CharField(max_length=100, unique=True, db_column='T168nombre')
    id_unidad_medida = models.ForeignKey(UnidadesMedida, on_delete=models.CASCADE, db_column='T168Id_UnidadMedida')
    item_activo = models.BooleanField(default=True, db_column='T168itemActivo')
    item_ya_usado = models.BooleanField(default=False, db_column='T168itemYaUsado')
    
    def __str__(self):
        return str(self.id_mezcla)
    
    class Meta:
        db_table = 'T168Mezclas'
        verbose_name = 'Mezcla'
        verbose_name_plural = 'Mezclas'

class PreparacionMezclas(models.Model):
    id_preparacion_mezcla = models.AutoField(primary_key=True, editable=False, db_column='T169IdPreparacionMezcla')
    id_vivero = models.ForeignKey(Vivero, on_delete=models.CASCADE, db_column='T169Id_Vivero')
    id_mezcla = models.ForeignKey(Mezclas, on_delete=models.CASCADE, db_column='T169Id_Mezcla')
    consec_vivero_mezclas = models.SmallIntegerField(db_column='T169consecViveroMezcla')
    fecha_preparacion = models.DateTimeField(db_column='T169fechaPreparacion')
    fecha_registro = models.DateTimeField(auto_now_add=True, db_column='T169fechaRegistro')
    observaciones = models.CharField(max_length=255, db_column='T169observaciones')
    cantidad_creada = models.IntegerField(db_column='T169cantidadCreada')
    id_persona_prepara = models.ForeignKey(Personas, on_delete=models.CASCADE, db_column='T169Id_PersonaPrepara', related_name='id_persona_prepara_mezcla')
    preparacion_anulada = models.BooleanField(default=False, db_column='T169preparacionAnulada')
    justificacion_anulacion = models.CharField(max_length=255, blank=True, null=True, db_column='T169justificacionAnulacion')
    fecha_anulacion = models.DateTimeField(blank=True, null=True, db_column='T169fechaAnulacion')
    id_persona_anula = models.ForeignKey(Personas, on_delete=models.SET_NULL, null=True, blank=True, db_column='T169Id_PersonaAnula', related_name='id_persona_anula_mezcla')
    
    def __str__(self):
        return str(self.id_preparacion_mezcla)
    
    class Meta: 
        db_table = 'T169PreparacionMezclas'
        verbose_name = 'Preparacion mezcla'
        verbose_name_plural = 'Preparacion mezclas'
        unique_together = ['id_vivero','id_mezcla','consec_vivero_mezclas']

class ItemsPreparacionMezcla(models.Model):
    id_item_preparacion_mezcla = models.AutoField(primary_key=True, editable=False, db_column='T170IdItem_PreparacionMezcla')
    id_preparacion_mezcla = models.ForeignKey(PreparacionMezclas, on_delete=models.CASCADE, db_column='T170Id_PreparacionMezcla')
    id_bien_usado = models.ForeignKey(CatalogoBienes, on_delete=models.CASCADE, db_column='T170Id_BienUsado')
    cantidad_usada = models.IntegerField(db_column='T170cantidadUsada')
    observaciones = models.CharField(max_length=30, null=True, blank=True, db_column='T170observaciones')
    nro_posicion = models.SmallIntegerField(db_column='T170nroPosicion')
    
    def __str__(self):
        return str(self.id_item_preparacion_mezcla)
    
    class Meta: 
        db_table = 'T170Items_PreparacionMezcla'  
        verbose_name = 'item preparacion mezcla'
        verbose_name_plural = 'items preparacion mezcla'
        unique_together = ['id_preparacion_mezcla','id_bien_usado']
        
    