from django.db import models
from seguimiento_planes.models.planes_models import ObjetivoDesarrolloSostenible, Planes, EjeEstractegico, Objetivo, Programa, Proyecto, Productos, Actividad, Entidad, Medicion, Tipo, Rubro, Indicador, Metas, TipoEje, Subprograma
from recurso_hidrico.models.bibliotecas_models import Cuencas
from transversal.models.organigrama_models import UnidadesOrganizacionales
from transversal.models.personas_models import Personas
from gestion_documental.models.expedientes_models import ArchivosDigitales
from transversal.models.base_models import (
    ClasesTerceroPersona
)

class FuenteFinanciacionIndicadores(models.Model):
    id_fuente = models.AutoField(primary_key=True, editable=False, db_column='T516IdFuente')
    nombre_fuente = models.CharField(max_length=100, db_column='T516nombreFuente')
    vano_1 = models.BigIntegerField(null=True, blank=True, db_column='T516vano1')
    vano_2 = models.BigIntegerField(null=True, blank=True, db_column='T516vano2')
    vano_3 = models.BigIntegerField(null=True, blank=True, db_column='T516vano3')
    vano_4 = models.BigIntegerField(null=True, blank=True, db_column='T516vano4')
    valor_total = models.BigIntegerField(null=True, blank=True, db_column='T516valorTotal')
    id_indicador = models.ForeignKey(Indicador, on_delete=models.CASCADE, db_column='T516IdIndicador')
    id_cuenca = models.ForeignKey(Cuencas, on_delete=models.CASCADE, db_column='T516IdCuenca')
    id_proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, db_column='T516IdProyecto')
    id_actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE, db_column='T516IdActividad')
    id_producto = models.ForeignKey(Productos, on_delete=models.CASCADE, db_column='T516IdProducto')

    def __str__(self):
        return str(self.nombre_fuente)
    
    class Meta: 
        db_table = 'T516FuentesFinanciacionIndicadores'
        verbose_name = 'Fuentes de Financiación Indicadores'
        verbose_name_plural = 'Fuentes de Financiación Indicadores'

class Sector(models.Model):
    id_sector = models.AutoField(primary_key=True, editable=False, db_column='T517IdSector')
    nombre_sector = models.CharField(max_length=100, db_column='T517nombreSector')
    aplicacion = models.CharField(max_length=100, db_column='T517aplicacion')
    activo = models.BooleanField(default=True, db_column='T517activo')
    item_ya_usado = models.BooleanField(default=False, db_column='T517itemYaUsado')
    registro_precargado = models.BooleanField(default=False, db_column='T517registroPrecargado')

    def __str__(self):
        return str(self.id_sector)

    class Meta:
        db_table = 'T517Sector'
        verbose_name = 'Sector'
        verbose_name_plural = 'Sectores'

class DetalleInversionCuentas(models.Model):
    id_detalle_inversion = models.AutoField(primary_key=True, editable=False, db_column='T518IdDetalleInversion')
    cuenta = models.CharField(max_length=100, db_column='T518cuenta')
    valor_cuenta = models.IntegerField(null=True, blank=True, db_column='T518valorCuenta')
    id_sector = models.ForeignKey(Sector, on_delete=models.CASCADE, db_column='T518IdSector')
    id_rubro = models.ForeignKey(Rubro, on_delete=models.CASCADE, db_column='T518IdRubro')
    id_programa = models.ForeignKey(Programa, on_delete=models.CASCADE, db_column='T518IdPrograma')
    id_subprograma = models.ForeignKey(Subprograma, on_delete=models.CASCADE, db_column='T518IdSubprograma')
    id_proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, db_column='T518IdProyecto')
    id_producto = models.ForeignKey(Productos, on_delete=models.CASCADE, db_column='T518IdProducto')
    id_actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE, db_column='T518IdActividad')
    id_indicador = models.ForeignKey(Indicador, on_delete=models.CASCADE, db_column='T518IdIndicador')
    id_meta = models.ForeignKey(Metas, on_delete=models.CASCADE, db_column='T518IdMeta')

    def __str__(self):
        return str(self.cuenta)

    class Meta:
        db_table = 'T518DetalleInversionCuentas'
        verbose_name = 'Detalle de Inversión Cuentas'
        verbose_name_plural = 'Detalle de Inversión Cuentas'

class Modalidad(models.Model): # Tabla básica
    id_modalidad = models.AutoField(primary_key=True, editable=False, db_column='T519IdModalidad')
    nombre_modalidad = models.CharField(max_length=100, db_column='T519nombreModalidad')
    codigo_modalidad = models.CharField(max_length=100, db_column='T519codigoModalidad')
    activo = models.BooleanField(default=True, db_column='T519activo')
    item_ya_usado = models.BooleanField(default=False, db_column='T519itemYaUsado')
    registro_precargado = models.BooleanField(default=False, db_column='T519registroPrecargado')

    def __str__(self):
        return str(self.nombre_modalidad)

    class Meta:
        db_table = 'T519Modalidad'
        verbose_name = 'Modalidad'
        verbose_name_plural = 'Modalidades'

class Ubicaciones(models.Model):
    id_ubicacion = models.AutoField(primary_key=True, editable=False, db_column='T520IdUbicacion')
    nombre_ubicacion = models.CharField(max_length=100, db_column='T520nombreUbicacion')
    codigo_ubicacion = models.CharField(max_length=100, db_column='T520codigoUbicacion')
    activo = models.BooleanField(default=True, db_column='T520activo')
    item_ya_usado = models.BooleanField(default=False, db_column='T520itemYaUsado')
    registro_precargado = models.BooleanField(default=False, db_column='T520registroPrecargado')

    def __str__(self):
        return str(self.nombre_ubicacion)

    class Meta:
        db_table = 'T520Ubicaciones'
        verbose_name = 'Ubicación'
        verbose_name_plural = 'Ubicaciones'

class FuenteRecursosPaa(models.Model):
    id_fuente = models.AutoField(primary_key=True, editable=False, db_column='T521IdFuente')
    nombre_fuente = models.CharField(max_length=100, db_column='T521nombreFuente')
    activo = models.BooleanField(default=True, db_column='T521activo')
    item_ya_usado = models.BooleanField(default=False, db_column='T521itemYaUsado')
    registro_precargado = models.BooleanField(default=False, db_column='T521registroPrecargado')

    def __str__(self):
        return str(self.nombre_fuente)

    class Meta:
        db_table = 'T521FuenteRecursosPaa'
        verbose_name = 'Fuente de Recursos PAA'
        verbose_name_plural = 'Fuentes de Recursos PAA'

class Intervalo(models.Model):
    id_intervalo = models.AutoField(primary_key=True, editable=False, db_column='T522IdIntervalo')
    nombre_intervalo = models.CharField(max_length=100, db_column='T522nombreIntervalo')
    activo = models.BooleanField(default=True, db_column='T522activo')
    item_ya_usado = models.BooleanField(default=False, db_column='T522itemYaUsado')
    registro_precargado = models.BooleanField(default=False, db_column='T522registroPrecargado')

    def __str__(self):
        return str(self.nombre_intervalo)

    class Meta:
        db_table = 'T522Intervalo'
        verbose_name = 'Intervalo'
        verbose_name_plural = 'Intervalos'
    
class EstadoVF(models.Model):
    id_estado = models.AutoField(primary_key=True, editable=False, db_column='T523IdEstado')
    nombre_estado = models.CharField(max_length=100, db_column='T523nombreEstado')
    activo = models.BooleanField(default=True, db_column='T523activo')
    item_ya_usado = models.BooleanField(default=False, db_column='T523itemYaUsado')
    registro_precargado = models.BooleanField(default=False, db_column='T523registroPrecargado')

    def __str__(self):
        return str(self.nombre_estado)

    class Meta:
        db_table = 'T523EstadoVF'
        verbose_name = 'Estado VF'
        verbose_name_plural = 'Estados VF'

class CodigosUNSP(models.Model):
    id_codigo = models.AutoField(primary_key=True, editable=False, db_column='T524IdCodigo')
    codigo_unsp = models.CharField(max_length=100, db_column='T524codigoUNSP')
    nombre_producto_unsp = models.CharField(max_length=255, db_column='T524nombreProductoUNSP')
    activo = models.BooleanField(default=True, db_column='T524activo')
    item_ya_usado = models.BooleanField(default=False, db_column='T524itemYaUsado')
    registro_precargado = models.BooleanField(default=False, db_column='T524registroPrecargado')

    def __str__(self):
        return str(self.id_codigo)

    class Meta:
        db_table = 'T524CodigosUNSP'
        verbose_name = 'Código UNSP'
        verbose_name_plural = 'Códigos UNSP'

class ConceptoPOAI(models.Model):
    id_concepto = models.AutoField(primary_key=True, editable=False, db_column='T525IdConcepto')
    concepto = models.CharField(max_length=255, db_column='T525concepto')
    valor_total = models.BigIntegerField(null=True, blank=True, db_column='T525valorTotal')
    id_rubro = models.ForeignKey(Rubro, on_delete=models.CASCADE, db_column='T525IdRubro')
    id_indicador = models.ForeignKey(Indicador, on_delete=models.CASCADE, db_column='T525IdIndicador')
    id_unidad_organizacional = models.ForeignKey(UnidadesOrganizacionales, on_delete=models.CASCADE, db_column='T525IdUnidadOrganizacional')

    def __str__(self):
        return str(self.concepto)
    
    class Meta:
        db_table = 'T525ConceptoPOAI'
        verbose_name = 'Concepto POAI'
        verbose_name_plural = 'Conceptos POAI'

class FuenteFinanciacion(models.Model):
    id_fuente = models.AutoField(primary_key=True, editable=False, db_column='T526IdFuente')
    nombre_fuente = models.CharField(max_length=100, db_column='T526nombreFuente')
    vano_1 = models.BigIntegerField(null=True, blank=True, db_column='T526vano1')
    vano_2 = models.BigIntegerField(null=True, blank=True, db_column='T526vano2')
    vano_3 = models.BigIntegerField(null=True, blank=True, db_column='T526vano3')
    vano_4 = models.BigIntegerField(null=True, blank=True, db_column='T526vano4')
    id_concepto = models.ForeignKey(ConceptoPOAI, on_delete=models.CASCADE, db_column='T526IdConcepto')

    def __str__(self):
        return str(self.nombre_fuente)
    
    class Meta: 
        db_table = 'T526FuentesFinanciacion'
        verbose_name = 'Fuentes de Financiación'
        verbose_name_plural = 'Fuentes de Financiación'


class BancoProyecto(models.Model):
    id_banco = models.AutoField(primary_key=True, editable=False, db_column='T527IdBanco')
    banco_valor = models.BigIntegerField(null=True, blank=True, db_column='T527bancoValor')
    objeto_contrato = models.CharField(max_length=255, db_column='T527objetoContrato')
    id_proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, db_column='T527IdProyecto')
    id_actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE, db_column='T527IdActividad')
    id_indicador = models.ForeignKey(Indicador, on_delete=models.CASCADE, db_column='T527IdIndicador')
    id_meta = models.ForeignKey(Metas, on_delete=models.CASCADE, db_column='T527IdMeta')
    id_rubro = models.ForeignKey(Rubro, on_delete=models.CASCADE, db_column='T527IdRubro')
    id_fuente_financiacion = models.ForeignKey(FuenteFinanciacion, on_delete=models.CASCADE, db_column='T527IdFuenteFinanciacion')

    def __str__(self):
        return str(self.objeto_contrato)

    class Meta:
        db_table = 'T527BancoProyecto'
        verbose_name = 'Banco de Proyecto'
        verbose_name_plural = 'Bancos de Proyecto'

class PlanAnualAdquisiciones(models.Model):
    id_plan_anual = models.AutoField(primary_key=True, editable=False, db_column='T528IdPlanAnualAdquisiciones')
    descripcion = models.CharField(max_length=255, db_column='T528descripcion')
    mes_inicio = models.CharField(
        max_length=3, choices=[
            ('ENE', 'Enero'),
            ('FEB', 'Febrero'),
            ('MAR', 'Marzo'),
            ('ABR', 'Abril'),
            ('MAY', 'Mayo'),
            ('JUN', 'Junio'),
            ('JUL', 'Julio'),
            ('AGO', 'Agosto'),
            ('SEP', 'Septiembre'),
            ('OCT', 'Octubre'),
            ('NOV', 'Noviembre'),
            ('DIC', 'Diciembre'),
                ], db_column='T528mesInicio')    
    mes_oferta = models.CharField(
        max_length=3, choices=[
            ('ENE', 'Enero'),
            ('FEB', 'Febrero'),
            ('MAR', 'Marzo'),
            ('ABR', 'Abril'),
            ('MAY', 'Mayo'),
            ('JUN', 'Junio'),
            ('JUL', 'Julio'),
            ('AGO', 'Agosto'),
            ('SEP', 'Septiembre'),
            ('OCT', 'Octubre'),
            ('NOV', 'Noviembre'),
            ('DIC', 'Diciembre'),
        ], db_column='T528mesOferta')
    duracion = models.BigIntegerField(null=True, blank=True, db_column='T528duracion')
    valor_total_estimado = models.BigIntegerField(null=True, blank=True, db_column='T528valorTotalEstimado')
    valor_vigencia_actual = models.BigIntegerField(null=True, blank=True, db_column='T528valorVigenciaActual')
    vigencia_futura = models.BigIntegerField(null=True, blank=True, db_column='T528vigenciaFutura')
    decreto_paa = models.BooleanField(default=False, db_column='T528decretoPAA')
    suministro_paa = models.BooleanField(default=False, db_column='T528suministroPAA')
    id_plan = models.ForeignKey(Planes, on_delete=models.CASCADE, db_column='T528IdPlan')
    id_intervalo = models.ForeignKey(Intervalo, on_delete=models.CASCADE, db_column='T528IdIntervalo')
    id_modalidad = models.ForeignKey(Modalidad, on_delete=models.CASCADE, db_column='T528IdModalidad')
    id_recurso_paa = models.ForeignKey(FuenteRecursosPaa, on_delete=models.CASCADE, db_column='T528IdRecursoPAA')
    id_estado_vf = models.ForeignKey(EstadoVF, on_delete=models.CASCADE, db_column='T528IdEstadoVF')
    id_unidad_organizacional = models.ForeignKey(UnidadesOrganizacionales, on_delete=models.CASCADE, db_column='T525IdUnidadOrganizacional')
    id_ubicaion = models.ForeignKey(Ubicaciones, on_delete=models.CASCADE, db_column='T528IdUbicacion')
    id_persona_responsable = models.ForeignKey(Personas, on_delete=models.CASCADE, db_column='T528IdPersonaResponsable')

    def __str__(self):
        return str(self.descripcion)

    class Meta:
        db_table = 'T528PlanAnualAdquisiciones'
        verbose_name = 'Plan Anual de Adquisiciones'
        verbose_name_plural = 'Planes Anuales de Adquisiciones'

class PAACodgigoUNSP(models.Model): # Tabla intermedia
    id_paacodigo = models.AutoField(primary_key=True, editable=False, db_column='T529IdPAACodigo')
    id_plan = models.ForeignKey(PlanAnualAdquisiciones, on_delete=models.CASCADE, db_column='T529IdPlan')
    id_codigo = models.ForeignKey(CodigosUNSP, on_delete=models.CASCADE, db_column='T529IdCodigo')

    def __str__(self):
        return str(self.id_paacodigo)

    class Meta:
        db_table = 'T529PAACodgigoUNSP'
        verbose_name = 'PAACodgigoUNSP'
        verbose_name_plural = 'PAACodgigoUNSP'

class SeguimientoPAI(models.Model):
    id_seguimiento_pai = models.AutoField(primary_key=True, editable=False, db_column='T530IdSeguiPAI')
    razagada = models.BooleanField(default=False, db_column='T530razagada')
    mes = models.CharField(
        max_length=3, choices=[
            ('ENE', 'Enero'),
            ('FEB', 'Febrero'),
            ('MAR', 'Marzo'),
            ('ABR', 'Abril'),
            ('MAY', 'Mayo'),
            ('JUN', 'Junio'),
            ('JUL', 'Julio'),
            ('AGO', 'Agosto'),
            ('SEP', 'Septiembre'),
            ('OCT', 'Octubre'),
            ('NOV', 'Noviembre'),
            ('DIC', 'Diciembre'),
        ], db_column='T530mes')
    porcentaje_avance = models.BigIntegerField(null=True, blank=True, db_column='T530porcentajeAvance')
    fecha_registro_avance = models.DateField(null=True, blank=True, db_column='T530fechaRegistroAvance')
    entrega_vigencia = models.TextField(null=True, blank=True, db_column='T530entregaVigencia')
    hizo = models.TextField(null=True, blank=True, db_column='T530hizo')
    cuando = models.TextField(null=True, blank=True, db_column='T530cuando')
    adelanto = models.TextField(null=True, blank=True, db_column='T530adelanto')
    donde = models.TextField(null=True, blank=True, db_column='T530donde')
    resultado = models.TextField(null=True, blank=True, db_column='T530resultado')
    participacion = models.TextField(null=True, blank=True, db_column='T530participacion')
    beneficiarios = models.TextField(null=True, blank=True, db_column='T530beneficiarios')
    compromisos = models.TextField(null=True, blank=True, db_column='T530compromisos')
    contratros = models.TextField(null=True, blank=True, db_column='T530contratros')
    fecha_creacion = models.DateField(null=True, blank=True, db_column='T530fechaCreacion')
    id_unidad_organizacional = models.ForeignKey(UnidadesOrganizacionales, on_delete=models.CASCADE, db_column='T530IdUnidadOrganizacional')
    id_programa = models.ForeignKey(Programa, on_delete=models.CASCADE, db_column='T530IdPrograma')
    id_proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, db_column='T530IdProyecto')
    id_producto = models.ForeignKey(Productos, on_delete=models.CASCADE, db_column='T530IdProducto')
    id_actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE, db_column='T530IdActividad')
    id_indicador = models.ForeignKey(Indicador, on_delete=models.CASCADE, db_column='T530IdIndicador')
    id_meta = models.ForeignKey(Metas, on_delete=models.CASCADE, db_column='T530IdMeta')

    def __str__(self):
        return str(self.id_seguimiento_pai)
    
    class Meta:
        db_table = "T530SeguiminetoPAI"
        verbose_name = "Seguimiento PAI"
        verbose_name_plural = "Seguimiento PAI"

class SeguimientoPAIDocumentos(models.Model): # Tabla intermedia
    id_seguimiento_pai_documento = models.AutoField(primary_key=True, editable=False, db_column='T531IdSeguiPAIDoc')
    id_seguimiento_pai = models.ForeignKey(SeguimientoPAI, on_delete=models.CASCADE, db_column='T531IdSeguiPAI')
    id_archivo_digital = models.ForeignKey(ArchivosDigitales, on_delete=models.CASCADE, db_column='T531IdArchivoDigital')

    def __str__(self):
        return str(self.id_seguimiento_pai_documento)
    
    class Meta:
        db_table = "T531SeguiminetoPAIDocumentos"
        verbose_name = "Seguimiento PAI Documentos"
        verbose_name_plural = "Seguimiento PAI Documentos"

class SeguimientoPOAI(models.Model):
    id_seguimiento: models.AutoField(primary_key=True, editable=False, db_column='T532IdSeguiPOAI')
    id_plan = models.ForeignKey(Planes, on_delete=models.CASCADE, db_column='T528IdPlan')
    id_programa = models.ForeignKey(Programa, on_delete=models.CASCADE, db_column='T532IdPrograma')
    id_proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, db_column='T532IdProyecto')
    id_producto = models.ForeignKey(Productos, on_delete=models.CASCADE, db_column='T532IdProducto')
    id_actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE, db_column='T532IdActividad')
    id_indicador = models.ForeignKey(Indicador, on_delete=models.CASCADE, db_column='T532IdIndicador')
    id_meta = models.ForeignKey(Metas, on_delete=models.CASCADE, db_column='T532IdMeta')
    id_concepto = models.ForeignKey(ConceptoPOAI, on_delete=models.CASCADE, db_column='T532IdConcepto')
    id_sector: models.ForeignKey(Sector, on_delete=models.CASCADE, db_column='T532IdSector')
    id_fuente_financiacion = models.ForeignKey(FuenteFinanciacion, on_delete=models.CASCADE, db_column='T532IdFuenteFinanciacion')
    id_unidad_organizacional = models.ForeignKey(UnidadesOrganizacionales, on_delete=models.CASCADE, db_column='T532IdUnidadOrganizacional')
    id_detalle_inversion = models.ForeignKey(DetalleInversionCuentas, on_delete=models.CASCADE, db_column='T532IdDetalleInversion')
    id_banco_proyecto = models.ForeignKey(BancoProyecto, on_delete=models.CASCADE, db_column='T532IdBancoProyecto')
    id_modalidad = models.ForeignKey(Modalidad, on_delete=models.CASCADE, db_column='T532IdModalidad')
    id_ubicacion = models.ForeignKey(Ubicaciones, on_delete=models.CASCADE, db_column='T532IdUbicacion')
    id_clase_tercero = models.ForeignKey(ClasesTerceroPersona, on_delete=models.CASCADE, db_column='T532IdClaseTercero')
    porcentaje_pto = models.BigIntegerField(null=True, blank=True, db_column='T532porcentajePTO')
    vano_1 = models.BigIntegerField(null=True, blank=True, db_column='T532vano1')
    vano_2 = models.BigIntegerField(null=True, blank=True, db_column='T532vano2')
    vano_3 = models.BigIntegerField(null=True, blank=True, db_column='T532vano3')
    vano_4 = models.BigIntegerField(null=True, blank=True, db_column='T532vano4')
    valor_total = models.BigIntegerField(null=True, blank=True, db_column='T532valorTotal')
    numero_cdp_paa = models.BigIntegerField(null=True, blank=True, db_column='T532numeroCDP_PAA')
    numero_rp_paa = models.BigIntegerField(null=True, blank=True, db_column='T532numeroRP_PAA')
    valor_seguimiento_banco_paa = models.BigIntegerField(null=True, blank=True, db_column='T532valorSeguimientoBanco_PAA')
    valor_cdp_paa = models.BigIntegerField(null=True, blank=True, db_column='T532valorCDP_PAA')
    valor_rp_paa = models.BigIntegerField(null=True, blank=True, db_column='T532valorRP_PAA')
    fecha_termiacion = models.DateField(null=True, blank=True, db_column='T532fechaTermiacion')
    duracion = models.BigIntegerField(null=True, blank=True, db_column='T532duracion')
    valor_mesual_paoi = models.BigIntegerField(null=True, blank=True, db_column='T532valorMesualPAOI')
    mes_oferta_paa = models.CharField(
        max_length=3, choices=[
            ('ENE', 'Enero'),
            ('FEB', 'Febrero'),
            ('MAR', 'Marzo'),
            ('ABR', 'Abril'),
            ('MAY', 'Mayo'),
            ('JUN', 'Junio'),
            ('JUL', 'Julio'),
            ('AGO', 'Agosto'),
            ('SEP', 'Septiembre'),
            ('OCT', 'Octubre'),
            ('NOV', 'Noviembre'),
            ('DIC', 'Diciembre'),
        ], db_column='T532mesOfertaPAA')
    mes_solicita = models.CharField(
        max_length=3, choices=[
            ('ENE', 'Enero'),
            ('FEB', 'Febrero'),
            ('MAR', 'Marzo'),
            ('ABR', 'Abril'),
            ('MAY', 'Mayo'),
            ('JUN', 'Junio'),
            ('JUL', 'Julio'),
            ('AGO', 'Agosto'),
            ('SEP', 'Septiembre'),
            ('OCT', 'Octubre'),
            ('NOV', 'Noviembre'),
            ('DIC', 'Diciembre'),
        ], db_column='T532mesSolicita')
    valor_pagado = models.BigIntegerField(null=True, blank=True, db_column='T532valorPagado')
    valor_obligado = models.BigIntegerField(null=True, blank=True, db_column='T532valorObligado')
    valor_saldo = models.BigIntegerField(null=True, blank=True, db_column='T532valorSaldo')
    porcentaje_ejecuta = models.BigIntegerField(null=True, blank=True, db_column='T532porcentajeEjecuta')
    numero_contrato = models.BigIntegerField(null=True, blank=True, db_column='T532numeroContrato')
    numerp_rp = models.BigIntegerField(null=True, blank=True, db_column='T532numerRP_RP')
    fecha_rp = models.DateField(null=True, blank=True, db_column='T532fechaRP')
    valor_cdp = models.BigIntegerField(null=True, blank=True, db_column='T532valorCDP')
    fecha_cdp = models.DateField(null=True, blank=True, db_column='T532fechaCDP')
    observaciones = models.TextField(null=True, blank=True, db_column='T532observaciones')
