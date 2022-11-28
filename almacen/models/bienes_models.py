from django.db import models
from seguridad.choices.municipios_choices import municipios_CHOICES
from almacen.choices.tipos_activo_choices import tipos_activo_CHOICES
from seguridad.models import Personas

class Articulos(models.Model):
    id_articulo = models.AutoField(primary_key=True, db_column='T057Id_Articulo')
    nombre = models.CharField(max_length=20, db_column='T057nombre')
    cod_estado_final = models.CharField(max_length=20, db_column='T057cod_estado_final')
    
    def __str__(self):
        return str(self.nombre)

    class Meta:
        db_table = 'T057Articulos'
        verbose_name = 'Artículo'
        verbose_name_plural = 'Artículos'

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
    cod_tipo_activo = models.CharField(primary_key=True, choices=tipos_activo_CHOICES, max_length=1, db_column='T060CodTipoActivo')
    nombre = models.CharField(max_length=15, db_column='T060nombre', unique=True)

    def __str__(self):
        return str(self.nombre)

    class Meta:
        db_table = 'T060TiposActivo'
        verbose_name = 'Tipo Activos'
        verbose_name_plural = 'Tipos Activos'
