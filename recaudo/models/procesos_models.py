from django.db import models
from recaudo.models.base_models import TiposBien


class Bienes(models.Model):
    id = models.AutoField(primary_key=True, db_column='T419id')
    cod_deudor = models.IntegerField(db_column='T419cod_deudor')
    descripcion = models.CharField(max_length=255, db_column='T419descripcion')
    estado = models.CharField(max_length=255, db_column='T419estado')
    id_tipo_bien = models.ForeignKey(TiposBien, on_delete=models.CASCADE, db_column='T419id_tipo_bien')
    documento_soporte = models.TextField(db_column='T419documento_soporte')

    class Meta:
        db_table = 'T419bienes'
        verbose_name = 'Bien'
        verbose_name_plural = 'Bienes'


class Avaluos(models.Model):
    id = models.AutoField(primary_key=True, db_column='T420id')
    id_bien = models.IntegerField(db_column='T420id_bien')
    fecha_avaluo = models.DateField(db_column='T420fecha_avaluo')
    cod_funcionario_perito = models.IntegerField(db_column='T420cod_funcionario_perito')
    valor = models.DecimalField(max_digits=30, decimal_places=2, db_column='T420valor')
    inicio = models.DateField(db_column='T420inicio')
    fin = models.DateField(db_column='T420fin')

    class Meta:
        db_table = 'T420avaluos'
        verbose_name = 'Avaluo'
        verbose_name_plural = 'Avaluos'


class EtapasProceso(models.Model):
    id = models.AutoField(primary_key=True, db_column='T413id')
    descripcion = models.CharField(max_length=255, db_column='T413descripcion')

    class Meta:
        db_table = 'T413etapas_proceso'
        verbose_name = 'Etapa procesos'
        verbose_name_plural = 'Etapas procesos'


class AtributosEtapas(models.Model):
    id = models.AutoField(primary_key=True, db_column='T421id')
    descripcion = models.CharField(max_length=255, db_column='T421descripcion')
    obligatorio = models.IntegerField(db_column='T421obligatorio')
    tipo = models.IntegerField(db_column='T421tipo')
    id_etapa = models.IntegerField(db_column='T421id_etapa')

    class Meta:
        db_table = 'T421atributos_etapa'
        verbose_name = 'Atributo etapas'
        verbose_name_plural = 'Atributos etapas'


class Procesos(models.Model):
    id = models.AutoField(primary_key=True, db_column='T422id')
    id_cartera = models.IntegerField(db_column='T422id_cartera')
    id_funcionario = models.IntegerField(db_column='T422id_funcionario')
    inicio = models.DateField(db_column='T422inicio')
    fin = models.DateField(db_column='T422fin')

    class Meta:
        db_table = 'T422procesos'
        verbose_name = 'Proceso'
        verbose_name_plural = 'Procesos'


class ValoresProceso(models.Model):
    id = models.AutoField(primary_key=True, db_column='T423id')
    id_proceso = models.IntegerField(db_column='T423id_proceso')
    id_atributo = models.IntegerField(db_column='T423id_atributo')
    valor = models.TextField(db_column='T423valor')

    class Meta:
        db_table = 'T423valores_proceso'
        verbose_name = 'Valores proceso'
        verbose_name_plural = 'Valores procesos'


class FlujoProceso(models.Model):
    id = models.AutoField(primary_key=True, db_column='T425id')
    id_etapa_origen = models.IntegerField(db_column='T425id_etapa_origen')
    id_etapa_destino = models.IntegerField(db_column='T425id_etapa_destino')
    fecha_flujo = models.DateField(db_column='T425fecha_flujo')
    descripcion = models.CharField(max_length=255, db_column='T425descripcion')
    requisitos = models.TextField(db_column='T425requisitos')

    class Meta:
        db_table = 'T425flujo_proceso'
        verbose_name = 'Flujo proceso'
        verbose_name_plural = 'Flujo procesos'
