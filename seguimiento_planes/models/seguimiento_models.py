from django.db import models
from seguimiento_planes.models.planes_models import Planes, Programa, Proyecto, Productos, Actividad, Rubro, Indicador, Metas, Subprograma
from recurso_hidrico.models.bibliotecas_models import Cuencas
from transversal.models.organigrama_models import UnidadesOrganizacionales
from transversal.models.personas_models import Personas
from gestion_documental.models.expedientes_models import ArchivosDigitales
from transversal.models.base_models import (
    ClasesTercero
)


class FuenteFinanciacionIndicadores(models.Model):
    id_fuente = models.AutoField(primary_key=True, editable=False, db_column='T516IdFuente')
    nombre_fuente = models.CharField(max_length=255, db_column='T516nombreFuente')
    vano_1 = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, db_column='T516vano1')
    vano_2 = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, db_column='T516vano2')
    vano_3 = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, db_column='T516vano3')
    vano_4 = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, db_column='T516vano4')
    vadicion1 = models.BooleanField(default=False, db_column='T516adicion1')
    vadicion2 = models.BooleanField(default=False, db_column='T516adicion2')
    vadicion3 = models.BooleanField(default=False, db_column='T516adicion3')
    vadicion4 = models.BooleanField(default=False, db_column='T516adicion4')
    valor_total = models.DecimalField(null=True, blank=True, db_column='T516valorTotal')
    id_plan = models.ForeignKey(Planes, on_delete=models.CASCADE, db_column='T516IdPlan')

    def __str__(self):
        return str(self.nombre_fuente)
    
    class Meta: 
        db_table = 'T516FuentesFinanciacionIndicadores'
        verbose_name = 'Fuentes de Financiación Indicadores'
        verbose_name_plural = 'Fuentes de Financiación Indicadores'


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
    nombre_concepto = models.CharField(max_length=255, db_column='T525nombreConcepto')
    valor_inicial = models.BigIntegerField(null=True, blank=True, db_column='T525valorInicial')
    id_plan = models.ForeignKey(Planes, on_delete=models.CASCADE, db_column='T525IdPlan')
    id_proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, db_column='T525IdProyecto')
    id_rubro = models.ForeignKey(Rubro, on_delete=models.CASCADE, db_column='T525IdRubro')
    id_indicador = models.ForeignKey(Indicador, on_delete=models.CASCADE, db_column='T525IdIndicador')
    id_meta = models.ForeignKey(Metas, on_delete=models.CASCADE, db_column='T525IdMeta')
    id_modalidad = models.ForeignKey(Modalidad, on_delete=models.CASCADE, db_column='T525IdModaliad')
    id_unidad_organizacional = models.ForeignKey(UnidadesOrganizacionales, on_delete=models.CASCADE, db_column='T525IdUnidadOrganizacional')

    def __str__(self):
        return str(self.concepto)
    
    class Meta:
        db_table = 'T525ConceptoPOAI'
        verbose_name = 'Concepto POAI'
        verbose_name_plural = 'Conceptos POAI'


class BancoProyecto(models.Model):
    id_banco = models.AutoField(primary_key=True, editable=False, db_column='T527IdBanco')
    banco_valor = models.BigIntegerField(null=True, blank=True, db_column='T527bancoValor')
    objeto_contrato = models.CharField(max_length=255, db_column='T527objetoContrato')
    id_proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, db_column='T527IdProyecto')
    id_actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE, db_column='T527IdActividad')
    id_indicador = models.ForeignKey(Indicador, on_delete=models.CASCADE, db_column='T527IdIndicador')
    id_meta = models.ForeignKey(Metas, on_delete=models.CASCADE, db_column='T527IdMeta')
    id_rubro = models.ForeignKey(Rubro, on_delete=models.CASCADE, db_column='T527IdRubro')
    id_fuente_financiacion = models.ForeignKey(FuenteFinanciacionIndicadores, on_delete=models.CASCADE, db_column='T527IdFuenteFinanciacion')

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


# class SeguimientoPOAI(models.Model):
#     id_seguimiento = models.AutoField(primary_key=True, editable=False, db_column='T532IdSeguiPOAI')
#     id_plan = models.ForeignKey(Planes, on_delete=models.CASCADE, db_column='T528IdPlan')
#     id_programa = models.ForeignKey(Programa, on_delete=models.CASCADE, db_column='T532IdPrograma')
#     id_proyecto = models.ForeignKey(Proyecto, on_delete=models.CASCADE, db_column='T532IdProyecto')
#     id_producto = models.ForeignKey(Productos, on_delete=models.CASCADE, db_column='T532IdProducto')
#     id_actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE, db_column='T532IdActividad')
#     id_indicador = models.ForeignKey(Indicador, on_delete=models.CASCADE, db_column='T532IdIndicador')
#     id_meta = models.ForeignKey(Metas, on_delete=models.CASCADE, db_column='T532IdMeta')
#     id_concepto = models.ForeignKey(ConceptoPOAI, on_delete=models.CASCADE, db_column='T532IdConcepto')
#     id_sector = models.ForeignKey(Sector, on_delete=models.CASCADE, db_column='T532IdSector')
#     id_fuente_financiacion = models.ForeignKey(FuenteFinanciacion, on_delete=models.CASCADE, db_column='T532IdFuenteFinanciacion')
#     id_unidad_organizacional = models.ForeignKey(UnidadesOrganizacionales, on_delete=models.CASCADE, db_column='T532IdUnidadOrganizacional')
#     id_detalle_inversion = models.ForeignKey(DetalleInversionCuentas, on_delete=models.CASCADE, db_column='T532IdDetalleInversion')
#     id_banco_proyecto = models.ForeignKey(BancoProyecto, on_delete=models.CASCADE, db_column='T532IdBancoProyecto')
#     id_modalidad = models.ForeignKey(Modalidad, on_delete=models.CASCADE, db_column='T532IdModalidad')
#     id_ubicacion = models.ForeignKey(Ubicaciones, on_delete=models.CASCADE, db_column='T532IdUbicacion')
#     id_clase_tercero = models.ForeignKey(ClasesTercero, on_delete=models.CASCADE, db_column='T532IdClaseTercero')
#     porcentaje_pto = models.BigIntegerField(null=True, blank=True, db_column='T532porcentajePTO')
#     vano_1 = models.BigIntegerField(null=True, blank=True, db_column='T532vano1')
#     vano_2 = models.BigIntegerField(null=True, blank=True, db_column='T532vano2')
#     vano_3 = models.BigIntegerField(null=True, blank=True, db_column='T532vano3')
#     vano_4 = models.BigIntegerField(null=True, blank=True, db_column='T532vano4')
#     valor_total = models.BigIntegerField(null=True, blank=True, db_column='T532valorTotal')
#     numero_cdp_paa = models.BigIntegerField(null=True, blank=True, db_column='T532numeroCDP_PAA')
#     numero_rp_paa = models.BigIntegerField(null=True, blank=True, db_column='T532numeroRP_PAA')
#     valor_seguimiento_banco_paa = models.BigIntegerField(null=True, blank=True, db_column='T532valorSeguimientoBanco_PAA')
#     valor_cdp_paa = models.BigIntegerField(null=True, blank=True, db_column='T532valorCDP_PAA')
#     valor_rp_paa = models.BigIntegerField(null=True, blank=True, db_column='T532valorRP_PAA')
#     fecha_termiacion = models.DateField(null=True, blank=True, db_column='T532fechaTermiacion')
#     duracion = models.BigIntegerField(null=True, blank=True, db_column='T532duracion')
#     valor_mesual_paoi = models.BigIntegerField(null=True, blank=True, db_column='T532valorMesualPAOI')
#     mes_oferta_paa = models.CharField(
#         max_length=3, choices=[
#             ('ENE', 'Enero'),
#             ('FEB', 'Febrero'),
#             ('MAR', 'Marzo'),
#             ('ABR', 'Abril'),
#             ('MAY', 'Mayo'),
#             ('JUN', 'Junio'),
#             ('JUL', 'Julio'),
#             ('AGO', 'Agosto'),
#             ('SEP', 'Septiembre'),
#             ('OCT', 'Octubre'),
#             ('NOV', 'Noviembre'),
#             ('DIC', 'Diciembre'),
#         ], db_column='T532mesOfertaPAA')
#     mes_solicita = models.CharField(
#         max_length=3, choices=[
#             ('ENE', 'Enero'),
#             ('FEB', 'Febrero'),
#             ('MAR', 'Marzo'),
#             ('ABR', 'Abril'),
#             ('MAY', 'Mayo'),
#             ('JUN', 'Junio'),
#             ('JUL', 'Julio'),
#             ('AGO', 'Agosto'),
#             ('SEP', 'Septiembre'),
#             ('OCT', 'Octubre'),
#             ('NOV', 'Noviembre'),
#             ('DIC', 'Diciembre'),
#         ], db_column='T532mesSolicita')
#     valor_pagado = models.BigIntegerField(null=True, blank=True, db_column='T532valorPagado')
#     valor_obligado = models.BigIntegerField(null=True, blank=True, db_column='T532valorObligado')
#     valor_saldo = models.BigIntegerField(null=True, blank=True, db_column='T532valorSaldo')
#     porcentaje_ejecuta = models.BigIntegerField(null=True, blank=True, db_column='T532porcentajeEjecuta')
#     numero_contrato = models.BigIntegerField(null=True, blank=True, db_column='T532numeroContrato')
#     numerp_rp = models.BigIntegerField(null=True, blank=True, db_column='T532numerRP_RP')
#     fecha_rp = models.DateField(null=True, blank=True, db_column='T532fechaRP')
#     valor_cdp = models.BigIntegerField(null=True, blank=True, db_column='T532valorCDP')
#     fecha_cdp = models.DateField(null=True, blank=True, db_column='T532fechaCDP')
#     observaciones = models.TextField(null=True, blank=True, db_column='T532observaciones')

#     def __str__(self):
#         return str(self.id_seguimiento)
    
#     class Meta:
#         db_table = "T532SeguiminetoPOAI"
#         verbose_name = "Seguimiento POAI"
#         verbose_name_plural = "Seguimiento POAI"

# # class SeguimientoPoaiOptimizado(models.Model):

class Prioridad(models.Model):
    id_prioridad = models.AutoField(primary_key=True, editable=False, db_column='T538IdPrioridad')
    nombre_prioridad = models.CharField(max_length=100, db_column='T538nombrePrioridad')
    activo = models.BooleanField(default=True, db_column='T538activo')
    item_ya_usado = models.BooleanField(default=False, db_column='T538itemYaUsado')
    registro_precargado = models.BooleanField(default=False, db_column='T538registroPrecargado')

    def __str__(self):
        return str(self.nombre_prioridad)

    class Meta:
        db_table = 'T538Prioridad'
        verbose_name = 'Prioridad'
        verbose_name_plural = 'Prioridades'

class SeguimientoPOAI(models.Model):
    id_seguimiento = models.AutoField(primary_key=True, editable=False, db_column='T537IdSeguimiento')
    id_concepto = models.ForeignKey(ConceptoPOAI, on_delete=models.CASCADE, db_column='T537IdConcepto')
    id_plan = models.ForeignKey(Planes, on_delete=models.CASCADE, db_column='T537IdPlan')
    id_producto = models.ForeignKey(Productos, on_delete=models.CASCADE, db_column='T537IdProducto')
    id_actividad = models.ForeignKey(Actividad, on_delete=models.CASCADE, db_column='T537IdActividad')
    id_indicador = models.ForeignKey(Indicador, on_delete=models.CASCADE, db_column='T537IdIndicador')
    id_meta = models.ForeignKey(Metas, on_delete=models.CASCADE, db_column='T537IdMeta')
    id_rubro = models.ForeignKey(Rubro, on_delete=models.CASCADE, db_column='T537IdRubro')
    descripcion = models.CharField(max_length=255, db_column='T537descripcion')
    id_prioridad = models.ForeignKey(Prioridad, null=True, blank=True, on_delete=models.SET_NULL, db_column='T537IdPrioridad')
    codigo_pre = models.CharField(max_length=100, db_column='T537codigoPre')
    cuenta = models.CharField(max_length=255, db_column='T537cuenta')
    id_unidad_organizacional = models.ForeignKey(UnidadesOrganizacionales, on_delete=models.CASCADE, db_column='T537IdUnidadOrganizacional')
    id_modalidad = models.ForeignKey(Modalidad, on_delete=models.CASCADE, db_column='T537Modalidad')
    id_fuente1 = models.BigIntegerField(null=True, blank=True, db_column='T537IdFuente1')
    valor_fte1 = models.BigIntegerField(null=True, blank=True, db_column='T537valorFte1')
    adicion1 = models.BooleanField(null=True, blank=True, db_column='T537adicion1')
    id_fuente2 = models.BigIntegerField(null=True, blank=True, db_column='T537IdFuente2')
    valor_fte2 = models.BigIntegerField(null=True, blank=True, db_column='T537valorFte2')
    adicion2 = models.BooleanField(null=True, blank=True, db_column='T537adicion2')
    id_fuente3 = models.BigIntegerField(null=True, blank=True, db_column='T537IdFuente3')
    valor_fte3 = models.BigIntegerField(null=True, blank=True, db_column='T537valorFte3')
    adicion3 = models.BooleanField(null=True, blank=True, db_column='T537adicion3')
    id_fuente4 = models.BigIntegerField(null=True, blank=True, db_column='T537IdFuente4')
    valor_fte4 = models.BigIntegerField(null=True, blank=True, db_column='T537valorFte4')
    adicion4 = models.BooleanField(null=True, blank=True, db_column='T537adicion4')
    valor_banco = models.BigIntegerField(null=True, blank=True, db_column='T537valorBanco')
    valor_cdp = models.BigIntegerField(null=True, blank=True, db_column='T537valorCDP')
    valor_rp = models.BigIntegerField(null=True, blank=True, db_column='T537valorRP')
    valor_obligado = models.BigIntegerField(null=True, blank=True, db_column='T537valorObligado')
    fecha_terminacion = models.DateField(null=True, blank=True, db_column='T537fechaTerminacion')
    duracion = models.BigIntegerField(null=True, blank=True, db_column='T537duracion')
    valor_mensual = models.BigIntegerField(null=True, blank=True, db_column='T537valorMensual')
    fecha_estimada = models.DateField(null=True, blank=True, db_column='T537fechaEstimada')
    mes_proyectado = models.CharField(max_length=11, db_column='T537mesProyectado')
    codigo_unsp = models.CharField(max_length=200, db_column='T537codigoUNSP')
    lugar_ejecucion = models.CharField(max_length=100, db_column='T537lugarEjecucion')
    numero_contrato = models.BigIntegerField(null=True, blank=True, db_column='T537numeroContrato')
    numero_banco = models.BigIntegerField(null=True, blank=True, db_column='T537numeroBanco')
    numero_rp = models.BigIntegerField(null=True, blank=True, db_column='T537numeroRP')
    fecha_rp = models.DateField(null=True, blank=True, db_column='T537fechaRP')
    numero_cdp = models.BigIntegerField(null=True, blank=True, db_column='T537numeroCDP')
    fecha_cdp = models.DateField(null=True, blank=True, db_column='T537fechaCDP')
    nombre_contratista = models.CharField(max_length=100, db_column='T537nombreContratista')
    observaciones_poai = models.CharField(max_length=100, db_column='T537observacionesPOAI')
    fecha_registro = models.DateField(null=True, blank=True, db_column='T537fechaRegistro')
    valor_pagado = models.BigIntegerField(null=True, blank=True, db_column='T537valorPagado')
    vseguimiento_paabanco = models.BigIntegerField(null=True, blank=True, db_column='T537vseguimientoPAABanco')
    vseguimiento_paacdp = models.BigIntegerField(null=True, blank=True, db_column='T537vseguimientoPAACDP')
    vseguimiento_paarp = models.BigIntegerField(null=True, blank=True, db_column='T537vseguimientoPAARP')
    svseguimiento_paaobligado = models.BigIntegerField(null=True, blank=True, db_column='T537svseguimientoPAAObligado')
    vseguimiento_paapagado = models.BigIntegerField(null=True, blank=True, db_column='T537vseguimientoPAAPagado')

    def __str__(self):
        return str(self.id_seguimiento)
    
    class Meta:
        db_table = "T537SeguimientoPOAI"
        verbose_name = "Seguimiento POAI"
        verbose_name_plural = "Registros Seguimiento POAI"

    