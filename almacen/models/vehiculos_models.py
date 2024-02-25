from django.db import models
from almacen.models.generics_models import Marcas
from almacen.choices.estado_aprobacion_choices import estado_aprobacion_CHOICES
from almacen.choices.cod_tipo_cierre_viaje_choices import cod_tipo_cierre_viajes_CHOICES
from almacen.choices.estado_solicitud_choices import estado_solicitud_CHOICES
from gestion_documental.models.expedientes_models import ExpedientesDocumentales
from seguridad.models import Personas



class VehiculosArrendados(models.Model):
    id_vehiculo_arrendado = models.AutoField(primary_key=True, editable=False, db_column="T071IdVehiculoArrendado")
    nombre = models.CharField(max_length=50, db_column="T071nombre")
    descripcion = models.CharField(max_length=255, db_column="T071descripcion")
    placa = models.CharField(max_length=10, unique=True, db_column="T071placa")
    id_marca = models.ForeignKey(Marcas, on_delete=models.CASCADE, db_column="T071Id_Marca")
    empresa_contratista = models.CharField(max_length=50, db_column="T071empresaContratista")
    tiene_hoja_de_vida = models.BooleanField(default=True, db_column="T071tieneHojaDeVida")
    
    def __str__(self):
        return str(self.nombre)
    
    class Meta:
        db_table = 'T071VehiculosArrendados'
        verbose_name = 'VehiculosArrendado'
        verbose_name_plural = 'VehiculosArrendados'

class VehiculosAgendables_Conductor(models.Model):
    id_vehiculo_conductor = models.AutoField(primary_key=True, editable=False, db_column="T072IdVehiculoConductor")
    id_hoja_vida_vehiculo = models.ForeignKey("almacen.HojaDeVidaVehiculos", on_delete=models.CASCADE, db_column="T072Id_HojaDeVidaVehiculo")
    id_persona_conductor =  models.ForeignKey("transversal.Personas", on_delete=models.CASCADE, db_column="T072Id_PersonaConductor", related_name='T072id_persona_conductor')
    fecha_inicio_asignacion = models.DateField(db_column="T072fechaIniciaAsignacion")
    fecha_final_asignacion = models.DateField(db_column="T072fechaFinalizaAsignacion")
    id_persona_que_asigna = models.ForeignKey("transversal.Personas", on_delete=models.CASCADE, db_column="T072Id_PersonaQueAsigna", related_name='T072id_persona_que_asigna')
    fecha_registro = models.DateTimeField(auto_now_add=True, db_column="T072fechaRegistro")
    
    def __str__(self):
        return str(self.id_vehiculo_conductor)
    
    class Meta:
        db_table = 'T072VehiculosAgendables_Conductor'
        verbose_name = 'VehiculosAgendables_Conductor'
        verbose_name_plural = 'VehiculosAgendables_Conductores'

class InspeccionesVehiculosDia(models.Model):
    id_inspeccion_vehiculo = models.AutoField(primary_key=True, editable=False, db_column="T073IdInspeccionVehiculoDia")
    id_hoja_vida_vehiculo = models.ForeignKey("almacen.HojaDeVidaVehiculos", on_delete=models.CASCADE, db_column="T073Id_HojaDeVidaVehiculo")
    id_persona_inspecciona = models.ForeignKey("transversal.Personas", on_delete=models.CASCADE, db_column="T073Id_PersonaQueInspecciona", related_name="T073id_persona_inspecciona")
    dia_inspeccion = models.DateField(db_column="T073diaInspeccion")
    fecha_registro = models.DateTimeField(db_column="T073fechaRegistro")
    kilometraje = models.IntegerField(db_column="T073Kilometraje")
    dir_llantas_delanteras = models.BooleanField(default=True, db_column="T073dirDelanterasBuenas")
    dir_llantas_Traseras = models.BooleanField(default=True, db_column="T073dirTraserasBuenas")
    limpiabrisas_delantero = models.BooleanField(default=True, db_column="T073limpiabrisasDelanterosBuenos")
    limpiabrisas_traseros = models.BooleanField(default=True, db_column="T073limpiabrisasTraseroBueno")
    nivel_aceite = models.BooleanField(default=True, db_column="T073nivelAceiteBueno")
    estado_frenos = models.BooleanField(default=True, db_column="T073nivelfrenosBueno")
    nivel_refrigerante = models.BooleanField(default=True, db_column="T073nivelRefrigeranteBueno")
    apoyo_cabezas_piloto = models.BooleanField(default=True, db_column="T073apoyaCabezasPilotoBueno")
    apoyo_cabezas_copiloto = models.BooleanField(default=True, db_column="T073apoyaCabezasCopilotoBueno")
    apoyo_cabezas_traseros = models.BooleanField(default=True, db_column="T073apoyaCabezasTraserosBuenos")
    frenos_generales = models.BooleanField(default=True, db_column="T073frenosGeneralesBuenos")    
    freno_emergencia = models.BooleanField(default=True, db_column="T073frenoEmergenciaBueno")
    llantas_delanteras = models.BooleanField(default=True, db_column="T073llantasDelanterasBuenas")
    llantas_traseras = models.BooleanField(default=True, db_column="T073llantasTraserasBuenas")
    llanta_repuesto = models.BooleanField(default=True, db_column="T073llantaRepuestoBuena")
    espejos_laterales = models.BooleanField(default=True, db_column="T073espejosLateralesBuenos")
    espejo_retrovisor = models.BooleanField(default=True, db_column="T073espejoRetrovisorBueno")
    cinturon_seguridad_delantero = models.BooleanField(default=True, db_column="T073cinturonesDelanterosBuenos")
    cinturon_seguridad_trasero = models.BooleanField(default=True, db_column="T073cinturonesTraserosBuenos")
    luces_altas = models.BooleanField(default=True, db_column="T073lucesAltasBuenas")
    luces_media = models.BooleanField(default=True, db_column="T073lucesMediasBuenas")
    luces_bajas = models.BooleanField(default=True, db_column="T073lucesBajasBuenas")
    luces_parada = models.BooleanField(default=True, db_column="T073lucesParadaBuenas")
    luces_parqueo = models.BooleanField(default=True, db_column="T073lucesParqueoBuenas")
    luces_reversa = models.BooleanField(default=True, db_column="T073lucesReversaBuenas")
    kit_herramientas = models.BooleanField(default=True, db_column="T073kitHerramientasAlDia")
    botiquin_completo = models.BooleanField(default=True, db_column="T073botiquinCompleto")
    pito = models.BooleanField(default=True, db_column="T073pitoBueno")
    observaciones = models.CharField(max_length=255, null=True, blank=True, db_column="T073observaciones")
    requiere_verificacion = models.BooleanField(default=True, db_column="T073requiereVerificacionSuperior")
    verificacion_superior_realizada = models.BooleanField(default=True, db_column="T073verificacionSuperiorRealizada")
    id_persona_que_verifica = models.ForeignKey("transversal.Personas", on_delete=models.SET_NULL, null=True, blank=True, db_column="T073Id_PersonaQueVerifica", related_name="T073id_persona_que_verifica")
    
    def __str__(self):
        return str(self.id_inspeccion_vehiculo)
    
    class Meta:
        db_table = "T073InspeccionesVehiculoDias"
        verbose_name = "InspeccionesVehiculoDia"
        verbose_name_plural = "InspeccionesVehiculoDias"
        
class VehiculosAgendadosDiaDisponible(models.Model):
    id_veh_agenda_dia = models.AutoField(primary_key=True, editable=False, db_column="T074IdvehAgendaDia")
    id_Hoja_vida_vehiculo = models.ForeignKey("almacen.HojaDeVidaVehiculos", on_delete=models.CASCADE, db_column="T074Id_HojaDeVidaVehiculo")
    dia_disponibilidad = models.DateField(db_column="T074diaDisponibilidad")
    consecutivo_dia = models.SmallIntegerField(db_column="T074consecutivoDia")
    id_viaje_agendado = models.ForeignKey("almacen.ViajesAgendados", on_delete=models.SET_NULL, null=True, blank=True, db_column="T074Id_ViajeAgendado")
    viaje_ejecutado = models.BooleanField(default=False, db_column="T074viajeEjecutado")
    id_persona_registra = models.ForeignKey("transversal.Personas", on_delete=models.CASCADE, db_column="T074Id_PersonaQueRegistra")
    
    def __str__(self):
        return str(self.id_veh_agenda_dia)
    
    class Meta:
        db_table = 'T074VehiculosAgendados_DiaDisponible'
        verbose_name = 'VehiculosAgendados_DiaDisponible'
        verbose_name_plural = 'VehiculosAgendados_DiaDisponibles'
        
class SolicitudesViajes(models.Model):
    id_solicitud_viaje = models.AutoField(primary_key=True, editable=False, db_column="T075IdSolicitudViaje")
    id_persona_solicita = models.ForeignKey("transversal.Personas", on_delete=models.CASCADE, db_column="T075Id_PersonaSolicita", related_name="T075id_persona_solicita")
    id_unidad_org_solicita = models.ForeignKey("transversal.UnidadesOrganizacionales", on_delete=models.CASCADE, db_column="T075Id_UnidadOrgSolicitante", related_name="T075id_unidad_org_solicita")
    fecha_solicitud = models.DateTimeField(db_column="T075fechaSolicitud")
    tiene_expediente_asociado = models.BooleanField(default=False, db_column="T075tieneExpedienteAsociado")
    id_expediente_asociado = models.ForeignKey(ExpedientesDocumentales, on_delete=models.SET_NULL, db_column='T075Id_ExpedienteAsociado',null=True, blank=True)
    motivo_viaje = models.CharField(max_length=255, db_column="T075motivoViajeSolicitado")
    direccion = models.CharField(max_length=255, db_column="T075direccion")
    cod_municipio = models.ForeignKey("transversal.Municipio", on_delete=models.CASCADE, db_column="T075Cod_MunicipioDestino")
    indicaciones_destino = models.CharField(max_length=255, db_column="T075indicacionesDestino")
    nro_pasajeros = models.SmallIntegerField(db_column="T075nroPasajeros")
    requiere_carga = models.BooleanField(default=True, db_column="T075requiereCarga")
    fecha_partida = models.DateField(db_column="T075fechaPartida")
    hora_partida = models.TimeField(db_column="T075horaPartida")
    fecha_retorno = models.DateField(db_column="T075fechaRetorno")
    hora_retorno = models.TimeField(db_column="T075horaRetorno")
    requiere_compagnia_militar = models.BooleanField(default=False, db_column="T075reqCompagniaMilitar")
    consideraciones_adicionales = models.CharField(max_length=255, null=True, blank=True, db_column="T075consideracionesAdicionales")
    id_persona_responsable = models.ForeignKey(Personas, on_delete=models.SET_NULL, db_column='T075Id_PersonaResponsable',null=True, blank=True,related_name="T075id_PersonaResponsable")
    id_unidad_org_responsable = models.ForeignKey("transversal.UnidadesOrganizacionales",  on_delete=models.SET_NULL, db_column="T075Id_UnidadOrgResponsable", null=True, blank=True)
    fecha_aprobacion_responsable = models.DateTimeField(null=True, blank=True, db_column="T075fechaAprobacionResponsable")
    fecha_rechazo = models.DateTimeField(null=True, blank=True, db_column="T075fechaRechazoSolicitud")
    justificacion_rechazo = models.CharField(max_length=255, null=True, blank=True, db_column="T075JustificacionRechazoSolicitud")
    estado_solicitud = models.CharField(max_length=2, choices=estado_solicitud_CHOICES, db_column="T075estadoSolicitud")
    
    def __str__(self):
        return str(self.id_solicitud_viaje)
    
    class Meta:
        db_table = 'T075SolicitudesViaje'
        verbose_name = 'SolicitudesViaje'
        verbose_name_plural = 'SolicitudesViajes'
        
class AsignacionesViajeAgendado(models.Model):
    id_asignacion_viaje = models.AutoField(primary_key=True, editable=False, db_column="T076IdAsignacion_ViajeAgendado")
    id_viaje_agendado = models.ForeignKey("almacen.ViajesAgendados", on_delete=models.CASCADE, db_column="T076Id_ViajeAgendado")
    id_solicitud_viaje = models.ForeignKey(SolicitudesViajes, on_delete=models.CASCADE, db_column="T076Id_SolicitudViaje")
    fecha_asignacion = models.DateTimeField(db_column="T076fechaAsignacion")
    asignacion_automatica = models.BooleanField(default=True, db_column="T076esAsignacionAutomatica")
    id_persona_asigna = models.ForeignKey("transversal.Personas", on_delete=models.SET_NULL, null=True, blank=True, db_column="T076Id_PersonaAsigna", related_name="T076id_persona_asigna")
    observaciones_asignacion = models.CharField(max_length=255, db_column="T076observacionesAsignacion")
    rechazo_solicitante = models.BooleanField(default=True, db_column="T076rechazadoSolicitante")
    id_persona_rechaza = models.ForeignKey("transversal.Personas", on_delete=models.SET_NULL, null=True, blank=True, db_column="T076Id_PersonaRechaza", related_name="T076id_persona_rechaza")
    justificacion_rechazo = models.CharField(max_length=255, null=True, blank=True, db_column="T076justificacionRechazo")
    fecha_rechazo = models.DateTimeField(db_column="T076fechaRechazo", blank=True, null=True)
    asignacion_anulada = models.BooleanField(null=True, blank=True, db_column="T076asignacionAnulada")
    id_persona_anula = models.ForeignKey("transversal.Personas", on_delete=models.SET_NULL, null=True, blank=True, db_column="T076Id_PersonaAnula", related_name="T076id_persona_anula")
    justificacion_anula = models.CharField(max_length=255, null=True, blank=True, db_column="T076justificacionAnulacion")
    fecha_anulacion = models.DateTimeField(null=True, blank=True, db_column="T076fechaAnulacion")
    solicitud_reprogramada = models.BooleanField(default=True, db_column="T076solicitudReprogramada")
    asignacion_abierta = models.BooleanField(default=True, db_column="T076asignacionAbierta")
    
    def __str__(self):
         return str(self.id_asignacion_viaje)
     
    class Meta:
         db_table = 'T076Asignaciones_ViajeAgendado'
         verbose_name = 'Asignaciones_ViajeAgendado'
         verbose_name_plural = 'Asignaciones_ViajeAgendados'

class ViajesAgendados(models.Model):
    id_viaje_agendado = models.AutoField(primary_key=True, editable=False, db_column="T077IdViajeAgendado")
    id_vehiculo_conductor = models.ForeignKey(VehiculosAgendables_Conductor, on_delete=models.SET_NULL, null=True, blank=True, db_column="T077Id_ConductorVehiculoAsig")
    id_solicitud_viaje = models.ForeignKey(SolicitudesViajes, on_delete=models.CASCADE, db_column="T077Id_SolicitudViaje")
    direccion = models.CharField(max_length=255, null=True, blank=True, db_column="T077direccion")
    cod_municipio_destino = models.ForeignKey("transversal.Municipio", on_delete=models.CASCADE, db_column="T077Cod_MunicipioDestino")
    indicaciones_destino = models.CharField(max_length=255, null=True, blank=True, db_column="T077indicacionesDestino")
    nro_total_pasajeros_req = models.SmallIntegerField(db_column="T077nroTotalPasajerosReq")
    requiere_capacidad_carga = models.BooleanField(default=True, db_column="T077requiereCapacidadCarga")
    fecha_partida_asignada = models.DateField(db_column="T077fechaPartidaAsignada")
    hora_partida = models.TimeField(db_column="T077horaPartida")
    fecha_retorno_asignada = models.DateField(db_column="T077fechaRetornoAsignada")
    hora_retorno = models.TimeField(db_column="T077horaRetorno")
    requiere_compagnia_militar = models.BooleanField(default=True, db_column="T077requiereCompagniaMilitar")
    viaje_autorizado = models.BooleanField(default=True, db_column="T077viajeAutorizado")
    observacion_autorizacion = models.CharField(max_length=140, null=True, blank=True, db_column="T077observacionAutorizacion")
    fecha_no_autorizado = models.DateTimeField(null=True, blank=True, db_column="T077fechaNoAutorizado")
    id_persona_autoriza = models.ForeignKey("transversal.Personas", on_delete=models.SET_NULL, null=True, blank=True, db_column="T077Id_PersonaAutoriza")
    fecha_autorizacion = models.DateTimeField(null=True, blank=True, db_column="T077fechaAutorizacion")
    ya_inicio = models.BooleanField(default=True, db_column="T077yaInicio")
    ya_llego = models.BooleanField(default=True, db_column="T077yaLlego")
    multiples_asignaciones = models.BooleanField(default=True, db_column="T077multiplesAsignaciones")
    estado = models.CharField(max_length=2, choices=estado_aprobacion_CHOICES, db_column="T077estado")

    def __str__(self):
        return str(self.id_viaje_agendado)
    
    class Meta:
        db_table = 'T077ViajesAgendados'
        verbose_name = 'ViajesAgendado'
        verbose_name_plural = 'ViajesAgendados'
        
class CompatibilidadViajesAgendados(models.Model):
    id_compatibilidad = models.AutoField(primary_key=True, editable=False, db_column="T078IdCompatibilidad")
    id_viaje_agendado = models.ForeignKey(ViajesAgendados, on_delete=models.CASCADE, db_column="T078Id_ViajeAgendado")
    id_solicitud_viaje = models.ForeignKey(SolicitudesViajes, on_delete=models.CASCADE, db_column="T078Id_SolicitudViajeSugerido")
    requiere_ajuste = models.BooleanField(null=True, blank=True, db_column="T078requiereAjuste")
    fecha_emparejamiento = models.DateTimeField(db_column="T078fechaEmparejamiento")
    
    def __str__(self):
        return str(self.id_compatibilidad)
    
    class Meta:
        db_table = 'T078Compatibilidades_ViajesAgendados'
        verbose_name = 'Compatibilidades_ViajesAgendado'
        verbose_name_plural = 'Compatibilidades_ViajesAgendados'

class BitacoraViaje(models.Model):
    id_bitacora = models.AutoField(primary_key=True, editable=False, db_column="T079IdBitacoraViaje")
    id_viaje_agendado = models.ForeignKey(ViajesAgendados, on_delete=models.CASCADE, db_column="T079Id_ViajeAgendado")
    id_conductor = models.ForeignKey("transversal.Personas", on_delete=models.SET_NULL, null=True, blank=True, db_column="T079Id_ConductorQueParte")
    nombre_conductor_fuera = models.CharField(max_length=90, null=True, blank=True, db_column="T079nombreConductorFueraSistema")
    documento_conductor_fuera = models.CharField(max_length=90, null=True, blank=True, db_column="T079documentoConductorFS")
    telefono_conductor_fs = models.CharField(max_length=15, null=True, blank=True, db_column="T079telefonoConductorFS")
    fecha_inicio_recorrido = models.DateTimeField(db_column="T079fechaInicioRecorrido")
    fecha_registro_inicio = models.DateTimeField(db_column="T079fechaRegistroDelInicio")
    novedad_salida = models.CharField(max_length=255, null=True, blank=True, db_column="T079novedadSalida")
    fecha_llegada_recorrido = models.DateTimeField(null=True, blank=True, db_column="T079fechaLlegadaRecorrido")
    novedad_llegada = models.CharField(max_length=255, null=True, blank=True, db_column="T079novedadLlegada")
    
    def __str__(self):
        return str(self.id_bitacora)
    
    class Meta:
        db_table = 'T079BitacoraViaje'
        verbose_name = 'BitacoraViaje'
        verbose_name_plural = 'BitacoraViajes'
        
class PeriodoArriendoVehiculo(models.Model):
    id_periodo_vehiculo_arriendo = models.AutoField(primary_key=True, editable=False, db_column="T085IdPeriodoVehiculoArrendado")
    id_vehiculo_arrendado = models.ForeignKey(VehiculosArrendados, on_delete=models.CASCADE, db_column="T085IdVehiculoArrendado")
    fecha_inicio = models.DateField(db_column="T085fechaInicio")
    fecha_fin = models.DateField(db_column="T085fechaFin")
    
    def __str__(self):
        return str(self.id_periodo_vehiculo_arriendo)
    
    class Meta:
        db_table = 'T085PeriodosVehiculoArrendado'
        verbose_name = 'PeriodosVehiculoArrendado'
        verbose_name_plural = 'PeriodosVehiculosArrendados'