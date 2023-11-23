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
    nombre_zona_hidrica = models.CharField(max_length=50, db_column="T621nombreZonaHidrica")
    id_macro_cuenca = models.ForeignKey(MacroCuencas, on_delete=models.CASCADE, db_column="T621Id_MacroCuenca")

    # Nuevo campo agregado
    id_zona_hidrografica = models.CharField(max_length=30, db_column="T621IdZonaHidrografica")

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


class SubZonaHidrica(models.Model):
    id_sub_zona_hidrica = models.AutoField(primary_key=True, editable=False, db_column="T623IdSubZonaHidrica")
    nombre_sub_zona_hidrica = models.CharField(max_length=50, db_column="T623nombreSubZonaHidrica")
    id_zona_hidrica = models.ForeignKey(ZonaHidrica, on_delete=models.CASCADE, db_column="T623Id_ZonaHidrica")
    id_tipo_zona_hidrica = models.ForeignKey(TipoZonaHidrica, on_delete=models.CASCADE, db_column="T623Id_TipoZonaHidrica")
    
    # Nuevo campo agregado
    codigo_rio = models.CharField(max_length=20, db_column="T623CodigoRio", null=True, blank=True,unique=True)

    class Meta:
        db_table = 'T623SubZonasHidricas'
        verbose_name = 'Sub Zona Hidrica'
        verbose_name_plural = 'Sub Zona Hidricas'
        unique_together = ['nombre_sub_zona_hidrica', 'id_zona_hidrica']
      
