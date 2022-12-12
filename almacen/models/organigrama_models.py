from django.db import models
from almacen.choices.agrupacion_documental_choices import agrupacion_documental_CHOICES
from almacen.choices.tipo_unidad_choices import tipo_unidad_CHOICES

class Organigramas(models.Model):
    id_organigrama = models.AutoField(primary_key=True, editable=False, db_column='T017IdOrganigrama')
    nombre = models.CharField(max_length=50, unique=True, db_column='T017nombre')
    fecha_terminado = models.DateTimeField(null=True, blank=True,db_column='T017fechaTerminado')
    descripcion = models.CharField(max_length=255, db_column='T017descripcion')
    fecha_puesta_produccion = models.DateTimeField(null=True, blank=True, db_column='T017fechaPuestaEnProduccion')
    fecha_retiro_produccion = models.DateTimeField(null=True, blank=True, db_column='T017fechaRetiroDeProduccion')
    justificacion_nueva_version = models.CharField(max_length=255, null=True, blank=True, db_column='T017justificacionNuevaVersion')
    version = models.CharField(max_length=10, unique=True, db_column='T017version')
    actual = models.BooleanField(default=False, db_column='T017actual')
    ruta_resolucion = models.FileField(null=True, blank=True, db_column='T017rutaResolucion')
    
    def __str__(self):
        return str(self.nombre)

    class Meta:
        db_table = 'T017Organigramas'
        verbose_name = 'Organigrama'
        verbose_name_plural = 'Organigramas'
          

class NivelesOrganigrama(models.Model):
    id_nivel_organigrama = models.AutoField(primary_key = True, editable=False, db_column='T018IdNivelOrganigrama')
    id_organigrama = models.ForeignKey(Organigramas, on_delete=models.CASCADE, null=False, blank=False, db_column='T018Id_Organigrama')
    orden_nivel = models.SmallIntegerField(db_column='T018ordenDelNivel')
    nombre = models.CharField(max_length=50, db_column='T018nombre')
    
    def __str__(self):
        return str(self.nombre)

    class Meta:
        db_table = 'T018NivelesOrganigrama'
        verbose_name = 'Nivel Organigrama'
        verbose_name_plural = 'Niveles Organigrama'
        ordering = ['orden_nivel'] 
        unique_together = ['id_organigrama', 'nombre']
        unique_together = ['id_organigrama', 'orden_nivel']



class UnidadesOrganizacionales(models.Model):
    id_unidad_organizacional=models.AutoField(primary_key=True,editable=False,db_column='T019IdUnidadOrganizacional')
    id_organigrama=models.ForeignKey(Organigramas, on_delete=models.CASCADE, db_column='T019Id_Organigrama')
    id_nivel_organigrama=models.ForeignKey(NivelesOrganigrama, on_delete=models.CASCADE, db_column='T019Id_NivelOrganigrama')
    nombre=models.CharField(max_length=50, db_column='T019nombre')
    codigo=models.CharField(max_length=10,db_column='T019codigo')
    cod_tipo_unidad=models.CharField(max_length=2,choices=tipo_unidad_CHOICES,db_column='T019codTipoUnidad')
    cod_agrupacion_documental=models.CharField(max_length=3, choices=agrupacion_documental_CHOICES, null=True, blank=True, db_column='T019codAgrupacionDocumental')
    unidad_raiz=models.BooleanField(db_column='T019unidadRaiz',default=False)
    id_unidad_org_padre=models.ForeignKey('self',on_delete=models.SET_NULL,blank=True,null=True,db_column='T019Id_UnidadOrgPadre')

    def __str__(self):
        return str(self.nombre) 
    class Meta:
        db_table='T019UnidadesOrganizacionales'
        verbose_name= 'Unidad organizacional'
        verbose_name_plural= 'Unidad organizacionales'
        unique_together = ['id_organigrama', 'nombre']
        unique_together = ['id_organigrama', 'codigo']
        ordering = ['id_nivel_organigrama']