from django.db import models
from recaudo.models.base_models import TiposBien, Ubicaciones
from recaudo.models.liquidaciones_models import Deudores


class Bienes(models.Model):
    id = models.AutoField(primary_key=True, db_column='T419id')
    cod_deudor = models.ForeignKey(Deudores, on_delete=models.CASCADE, db_column='T419cod_deudor')
    descripcion = models.CharField(max_length=255, db_column='T419descripcion')
    direccion = models.CharField(max_length=255, db_column='T419direccion')
    estado = models.CharField(max_length=255, db_column='T419estado')
    id_tipo_bien = models.ForeignKey(TiposBien, on_delete=models.CASCADE, db_column='T419id_tipo_bien')
    documento_soporte = models.FileField(db_column='T419documento_soporte')
    id_ubicacion = models.ForeignKey(Ubicaciones, on_delete=models.CASCADE, db_column='T419id_ubicacion')

    class Meta:
        db_table = 'T419bienes'
        verbose_name = 'Bien'
        verbose_name_plural = 'Bienes'


class Avaluos(models.Model):
    id = models.AutoField(primary_key=True, db_column='T420id')
    id_bien = models.ForeignKey(Bienes, on_delete=models.CASCADE, db_column='T420id_bien')
    fecha_avaluo = models.DateField(auto_now_add=True, db_column='T420fecha_avaluo')
    fecha_fin_vigencia = models.DateField(db_column='T420fecha_fin_vigencia')
    cod_funcionario_perito = models.IntegerField(db_column='T420cod_funcionario_perito')
    valor = models.DecimalField(max_digits=30, decimal_places=2, db_column='T420valor')
    inicio = models.DateField(null=True, blank= True, db_column='T420inicio')
    fin = models.DateField(null=True, blank= True, db_column='T420fin')

    class Meta:
        db_table = 'T420avaluos'
        verbose_name = 'Avaluo'
        verbose_name_plural = 'Avaluos'


class TiposAtributos(models.Model):
    id = models.AutoField(primary_key=True, db_column='T434id')
    tipo = models.CharField(max_length=255, db_column='T434tipo')

    class Meta:
        db_table = 'T434tipos_atributos'
        verbose_name = 'Tipos atributo'
        verbose_name_plural = 'Tipo atributo'


class EtapasProceso(models.Model):
    id = models.AutoField(primary_key=True, db_column='T413id')
    etapa = models.CharField(max_length=255, db_column='T413etapa')
    descripcion = models.CharField(max_length=255, db_column='T413descripcion')

    class Meta:
        db_table = 'T413etapas_proceso'
        verbose_name = 'Etapa procesos'
        verbose_name_plural = 'Etapas procesos'


class CategoriaAtributo(models.Model):
    id = models.AutoField(primary_key=True, db_column='T437id')
    categoria = models.CharField(max_length=255, db_column='T437categoria_atributo')

    class Meta:
        db_table = 'T437categoria_atributo'
        verbose_name = 'Categorias atributo'
        verbose_name_plural = 'Categorias atributos'


class AtributosEtapas(models.Model):
    id = models.AutoField(primary_key=True, db_column='T421id')
    descripcion = models.CharField(max_length=255, db_column='T421descripcion')
    obligatorio = models.IntegerField(db_column='T421obligatorio')
    id_tipo = models.ForeignKey(TiposAtributos, on_delete=models.CASCADE, db_column='T421tipo')
    id_etapa = models.ForeignKey(EtapasProceso, on_delete=models.CASCADE, db_column='T421id_etapa')
    id_categoria = models.ForeignKey(CategoriaAtributo, on_delete=models.CASCADE, db_column='T421id_categoria')

    class Meta:
        db_table = 'T421atributos_etapa'
        verbose_name = 'Atributo etapas'
        verbose_name_plural = 'Atributos etapas'


class Procesos(models.Model):
    id = models.AutoField(primary_key=True, db_column='T422id')
    id_cartera = models.ForeignKey('recaudo.Cartera', on_delete=models.CASCADE, db_column='T422id_cartera')
    id_etapa = models.ForeignKey(EtapasProceso, on_delete=models.CASCADE, db_column='T422id_etapa')
    id_funcionario = models.IntegerField(db_column='T422id_funcionario')
    id_categoria = models.ForeignKey(CategoriaAtributo, on_delete=models.CASCADE, db_column='T422id_categoria')
    inicio = models.DateField(db_column='T422inicio')
    fin = models.DateField(db_column='T422fin', null=True, blank=True)

    class Meta:
        db_table = 'T422procesos'
        verbose_name = 'Proceso'
        verbose_name_plural = 'Procesos'


class ValoresProceso(models.Model):
    id = models.AutoField(primary_key=True, db_column='T423id')
    id_proceso = models.ForeignKey(Procesos, on_delete=models.CASCADE, db_column='T423id_proceso')
    id_atributo = models.ForeignKey(AtributosEtapas, on_delete=models.CASCADE, db_column='T423id_atributo')
    valor = models.TextField(db_column='T423valor', null=True, blank=True)
    documento = models.FileField(db_column='T423documento', null=True, blank=True)

    class Meta:
        db_table = 'T423valores_proceso'
        verbose_name = 'Valores proceso'
        verbose_name_plural = 'Valores procesos'


class FlujoProceso(models.Model):
    id = models.AutoField(primary_key=True, db_column='T425id')
    id_etapa_origen = models.ForeignKey(EtapasProceso, on_delete=models.CASCADE, db_column='T425id_etapa_origen', related_name='origen')
    id_etapa_destino = models.ForeignKey(EtapasProceso, on_delete=models.CASCADE, db_column='T425id_etapa_destino', related_name='destino')
    fecha_flujo = models.DateField(db_column='T425fecha_flujo')
    descripcion = models.CharField(max_length=255, db_column='T425descripcion')
    requisitos = models.TextField(db_column='T425requisitos')

    class Meta:
        db_table = 'T425flujo_proceso'
        verbose_name = 'Flujo proceso'
        verbose_name_plural = 'Flujo procesos'
