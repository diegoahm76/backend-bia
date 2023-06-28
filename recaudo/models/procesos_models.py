from django.db import models
from recaudo.models.base_models import TiposBien, Ubicaciones
from recaudo.models.liquidaciones_models import Deudores


class Bienes(models.Model):
    id = models.AutoField(primary_key=True, db_column='T419IdBien')
    id_deudor = models.ForeignKey(Deudores, on_delete=models.CASCADE, db_column='T419Id_Deudor')
    descripcion = models.CharField(max_length=255, db_column='T419descripcion')
    direccion = models.CharField(max_length=255, db_column='T419direccion')
    id_tipo_bien = models.ForeignKey(TiposBien, on_delete=models.CASCADE, db_column='T419Id_TipoBien')
    documento_soporte = models.FileField(db_column='T419documentoSoporte')
    id_ubicacion = models.ForeignKey(Ubicaciones, on_delete=models.CASCADE, db_column='T419Id_Ubicacion')

    class Meta:
        db_table = 'T419Bienes'
        verbose_name = 'Bien'
        verbose_name_plural = 'Bienes'


class Avaluos(models.Model):
    id = models.AutoField(primary_key=True, db_column='T420IdAvaluo')
    id_bien = models.ForeignKey(Bienes, on_delete=models.CASCADE, db_column='T420Id_Bien')
    fecha_avaluo = models.DateField(auto_now_add=True, db_column='T420fechaAvaluo')
    fecha_fin_vigencia = models.DateField(db_column='T420fechaFinVigencia')
    cod_funcionario_perito = models.IntegerField(db_column='T420Id_FuncionarioPerito')
    valor = models.DecimalField(max_digits=30, decimal_places=2, db_column='T420valor')
    inicio = models.DateField(null=True, blank= True, db_column='T420inicio')
    fin = models.DateField(null=True, blank= True, db_column='T420fin')

    class Meta:
        db_table = 'T420Avaluos'
        verbose_name = 'Avaluo'
        verbose_name_plural = 'Avaluos'


class TiposAtributos(models.Model):
    id = models.AutoField(primary_key=True, db_column='T434IdTipoAtributo')
    tipo = models.CharField(max_length=255, db_column='T434tipo')

    class Meta:
        db_table = 'T434TiposAtributos'
        verbose_name = 'Tipo atributo'
        verbose_name_plural = 'Tipos atributo'


class EtapasProceso(models.Model):
    id = models.AutoField(primary_key=True, db_column='T413IdEtapaProceso')
    etapa = models.CharField(max_length=255, db_column='T413etapa')
    descripcion = models.CharField(max_length=255, db_column='T413descripcion')

    class Meta:
        db_table = 'T413EtapasProceso'
        verbose_name = 'Etapa procesos'
        verbose_name_plural = 'Etapas procesos'


class AtributosEtapas(models.Model):
    id = models.AutoField(primary_key=True, db_column='T421IdAtributoEtapa')
    descripcion = models.CharField(max_length=255, db_column='T421descripcion')
    obligatorio = models.IntegerField(db_column='T421obligatorio')
    id_tipo = models.ForeignKey(TiposAtributos, on_delete=models.CASCADE, db_column='T421tipo')
    id_etapa = models.ForeignKey(EtapasProceso, on_delete=models.CASCADE, db_column='T421Id_EtapaProceso')

    class Meta:
        db_table = 'T421AtributosEtapas'
        verbose_name = 'Atributo etapas'
        verbose_name_plural = 'Atributos etapas'


class Procesos(models.Model):
    id = models.AutoField(primary_key=True, db_column='T422IdProceso')
    id_cartera = models.ForeignKey('recaudo.Cartera', on_delete=models.CASCADE, db_column='T422Id_Cartera')
    id_etapa = models.ForeignKey(EtapasProceso, on_delete=models.CASCADE, db_column='T422Id_EtapaProceso')
    id_funcionario = models.IntegerField(db_column='T422Id_Funcionario')
    inicio = models.DateField(db_column='T422inicio')
    fin = models.DateField(db_column='T422fin', null=True, blank=True)

    class Meta:
        db_table = 'T422Procesos'
        verbose_name = 'Proceso'
        verbose_name_plural = 'Procesos'


class ValoresProceso(models.Model):
    id = models.AutoField(primary_key=True, db_column='T423IdValorProceso')
    id_proceso = models.ForeignKey(Procesos, on_delete=models.CASCADE, db_column='T423Id_Proceso')
    id_atributo = models.ForeignKey(AtributosEtapas, on_delete=models.CASCADE, db_column='T423Id_AtributoEtapa')
    valor = models.TextField(db_column='T423valor', null=True, blank=True)
    documento = models.FileField(db_column='T423documento', null=True, blank=True)

    class Meta:
        db_table = 'T423ValoresProceso'
        verbose_name = 'Valores proceso'
        verbose_name_plural = 'Valores procesos'


class FlujoProceso(models.Model):
    id = models.AutoField(primary_key=True, db_column='T425IdFlujoProceso')
    id_etapa_origen = models.ForeignKey(EtapasProceso, on_delete=models.CASCADE, db_column='T425Id_EtapaProcesoOrigen', related_name='origen')
    id_etapa_destino = models.ForeignKey(EtapasProceso, on_delete=models.CASCADE, db_column='T425id_EtapaProcesoDestino', related_name='destino')
    fecha_flujo = models.DateField(db_column='T425fechaFlujo')
    descripcion = models.CharField(max_length=255, db_column='T425descripcion')
    requisitos = models.TextField(db_column='T425requisitos')

    class Meta:
        db_table = 'T425FlujosProceso'
        verbose_name = 'Flujo proceso'
        verbose_name_plural = 'Flujo procesos'
