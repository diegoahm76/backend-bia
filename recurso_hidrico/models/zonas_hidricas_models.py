from django.db import models


class MacroCuencas (models.Model):
    id_macro_cuenca = models.AutoField(primary_key=True,editable=False, db_column="T620IdMacroCuenca")
    nombre_macro_cuenca = models.CharField(max_length=50, db_column="T620nombreMacroCuenca") 

    class Meta:
        db_table = 'T620MacroCuencas'
        verbose_name = 'Macro Cuenca'
        verbose_name_plural = 'Macro Cuencas'


class ZonaHidrica(models.Model):
    id_zona_hidrica = models.AutoField(primary_key=True, db_column="T621IdZonaHidrica")
    nombre_zona_hidrica = models.CharField(max_length=150, db_column="T621nombreZonaHidrica")
    codigo_zona_hidrica = models.CharField(max_length=3, db_column="T621codigoZonaHidrica")
    id_macro_cuenca = models.ForeignKey(MacroCuencas, on_delete=models.CASCADE, db_column="T621Id_MacroCuenca")
    
    class Meta:
        db_table = 'T621ZonasHidricas'
        verbose_name = 'Zona Hidrica'
        verbose_name_plural = 'Zona Hidricas'


class TipoZonaHidrica (models.Model):
    id_tipo_zona_hidrica = models.AutoField(primary_key=True,editable=False, db_column="T622IdTipoZonaHidrica")
    nombre_tipo_zona_hidrica = models.CharField(max_length=50,db_column="T622nombreTipoZonaHidrica") 
    
    class Meta:
        db_table = 'T622TipoZonasHidricas'
        verbose_name = 'Tipo Zona Hidrica'
        verbose_name_plural = 'Tipo Zona Hidricas'


class TipoAguaZonaHidrica (models.Model):
    id_tipo_agua_zona_hidrica = models.AutoField(primary_key=True,editable=False, db_column="T624IdTipoAguaZonaHidrica")
    nombre_tipo_agua_zona_hidrica = models.CharField(max_length=50,db_column="T624nombreTipoAguaZonaHidrica") 
    
    class Meta:
        db_table = 'T624TipoAguaZonaHidrica'
        verbose_name = 'Tipo Zona Agua Hidrica'
        verbose_name_plural = 'Tipo Zona Agua Hidricas'


class SubZonaHidrica(models.Model):
    id_sub_zona_hidrica = models.AutoField(primary_key=True, editable=False, db_column="T623IdSubZonaHidrica")
    nombre_sub_zona_hidrica = models.CharField(max_length=255, db_column="T623nombreSubzonaHidrica")
    codigo_rio = models.CharField(max_length=10, db_column="T623codigoRio")
    id_zona_hidrica = models.ForeignKey(ZonaHidrica, on_delete=models.CASCADE, db_column="T623Id_ZonaHidrica")
    id_tipo_zona_hidrica = models.ForeignKey(TipoZonaHidrica, on_delete=models.CASCADE, db_column="T623Id_TipoZonaHidrica")    
    id_tipo_agua_zona_hidrica = models.ForeignKey(TipoAguaZonaHidrica,blank=True,null=True,on_delete=models.SET_NULL, db_column="T623Id_TipoAguaZonaHidrica")
    valor_regional = models.CharField(max_length=50, db_column="T623valorRegional", null=True, blank=True)

    class Meta:
        db_table = 'T623SubZonasHidricas'
        verbose_name = 'Sub Zona Hidrica'
        verbose_name_plural = 'Sub Zona Hidricas'
        unique_together = ['nombre_sub_zona_hidrica', 'id_zona_hidrica','codigo_rio']

class CuencasSubZonas(models.Model):
    id_cuenca = models.AutoField(primary_key=True, db_column="T625IdCuenca")
    codigo_cuenca = models.CharField(max_length=10, db_column="T625codigoCuenca")
    nombre_cuenca = models.CharField(max_length=100, db_column="T625nombreCuenca")
    id_sub_zona_hidrica = models.ForeignKey(SubZonaHidrica, on_delete=models.CASCADE, db_column="T625Id_SubZonaHidrica")
    
    class Meta:
        db_table = 'T625Cuencas'
        verbose_name = 'Cuenca'
        verbose_name_plural = 'Cuencas'
        unique_together = ['codigo_cuenca', 'nombre_cuenca','id_sub_zona_hidrica']
