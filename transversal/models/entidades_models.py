from django.db import models

from seguridad.choices.municipios_choices import municipios_CHOICES
from seguridad.choices.paises_choices import paises_CHOICES


class ConfiguracionEntidad(models.Model):
    id_persona_entidad = models.IntegerField(primary_key=True, editable=False, db_column='T027IdPersonaEntidad')
    #id_persona_entidad = models.ForeignKey('seguridad.Personas', on_delete=models.CASCADE, null=True, db_column='T027IdPersonaEntidad')
    email_corporativo_sistema = models.CharField(max_length=100, null=True, db_column='T027emailCorporativoSistema')
    id_persona_director_actual = models.ForeignKey('seguridad.Personas', on_delete=models.SET_NULL, null=True, related_name='config_director_actual', db_column='T027Id_PersonaDirectorActual')
    fecha_inicio_dir_actual = models.DateTimeField(null=True, db_column='T027fechaInicioDirActual')
    id_persona_coord_almacen_actual = models.ForeignKey('seguridad.Personas', on_delete=models.SET_NULL, null=True, related_name='config_coord_almacen_actual', db_column='T027Id_PersonaCoordAlmacenActual')
    fecha_inicio_coord_alm_actual = models.DateTimeField(null=True, db_column='T027fechaInicioCoordAlmActual')
    id_persona_respon_transporte_actual = models.ForeignKey('seguridad.Personas', on_delete=models.SET_NULL, null=True, related_name='config_respon_transporte_actual', db_column='T027Id_PersonaResponTransporteActual')
    fecha_inicio_respon_trans_actual = models.DateTimeField(null=True, db_column='T027fechaInicioResponTransActual')
    id_persona_coord_viveros_actual = models.ForeignKey('seguridad.Personas', on_delete=models.SET_NULL, null=True, related_name='config_coord_viveros_actual', db_column='T027Id_PersonaCoordViverosActual')
    fecha_inicio_coord_viv_actual = models.DateTimeField(null=True, db_column='T027fechaInicioCoordVivActual')
    id_persona_almacenista = models.ForeignKey('seguridad.Personas', on_delete=models.SET_NULL, null=True, related_name='config_almacenista', db_column='T027Id_PersonaAlmacenista')
    fecha_inicio_almacenista = models.DateTimeField(null=True, db_column='T027fechaInicioAlmacenista')

    def _str_(self):
        return str(self.id_persona_entidad)

    class Meta:
        db_table = 'T027ConfiguracionEntidad'
        verbose_name = 'Configuración de Entidad'
        verbose_name_plural = 'Configuraciones de Entidad'


class HistoricoPerfilesEntidad(models.Model):
    id_historico_perfil_entidad = models.AutoField(primary_key=True, db_column='T028IdHistoricoPerfil_Entidad')
    id_persona_entidad = models.ForeignKey(ConfiguracionEntidad, on_delete=models.CASCADE, db_column='T028Id_PersonaEntidad')
    cod_tipo_perfil_histo = models.CharField(max_length=4, choices=[('Dire', 'Director'), ('CViv', 'Coordinador de Viveros'), ('RTra', 'Responsable de Transporte'), ('CAlm', 'Coordinador de Almacén'), ('Alma', 'Almacenista')], db_column='T028codTipoPerfilHisto')
    consec_asignacion_perfil_histo = models.SmallIntegerField(db_column='T028consecAsignacionPerfilHisto')
    id_persona_perfil_histo = models.ForeignKey('seguridad.Personas',related_name='historico_perfiles_perfil_histo', on_delete=models.CASCADE, db_column='T028Id_PersonaPerfilHisto')
    fecha_inicio_periodo = models.DateTimeField(db_column='T028fechaInicioPeriodo')
    fecha_fin_periodo = models.DateTimeField(db_column='T028fechaFinPeriodo')
    observaciones_cambio = models.CharField(max_length=255, db_column='T028observacionesCambio')
    id_persona_cambia = models.ForeignKey('seguridad.Personas',related_name='historico_perfiles_cambia' ,on_delete=models.CASCADE, db_column='T028Id_PersonaCambia')

    def __str__(self):
        return str(self.id_historico_perfil_entidad)

    class Meta:
        db_table = 'T028HistoricoPerfiles_Entidad'
        verbose_name = 'Histórico de Perfil de Entidad'
        verbose_name_plural = 'Históricos de Perfiles de Entidad'
        unique_together = ['id_persona_entidad', 'cod_tipo_perfil_histo','consec_asignacion_perfil_histo']


class SucursalesEmpresas(models.Model):
    id_sucursal_empresa = models.AutoField(primary_key=True, editable=False, db_column='T012IdSucursalEmpresa')
    id_persona_empresa = models.ForeignKey('seguridad.Personas',on_delete=models.CASCADE,  db_column='T012Id_PersonaEmpresa')
    numero_sucursal = models.SmallIntegerField(db_column='T012nroSucursal')
    descripcion_sucursal = models.CharField(max_length=255, db_column='T012descripcionSucursal')
    direccion = models.CharField(max_length=255, db_column='T012dirSucursal')
    direccion_sucursal_georeferenciada = models.CharField(max_length=50, null=True, blank=True, db_column='T012dirSucursalGeoref')
    municipio = models.CharField(max_length=5, choices=municipios_CHOICES, null=True, blank=True, db_column='T012Cod_MunicipioSucursalNal')
    pais_sucursal_exterior = models.CharField(max_length=2, choices=paises_CHOICES, null=True, blank=True, db_column='T012Cod_PaisSucursalExterior')
    direccion_notificacion = models.CharField(max_length=255, null=True, blank=True, db_column='T012dirNotificacionNal')
    direccion_notificacion_referencia = models.CharField(max_length=255, null=True, blank=True, db_column='T012dirNotificacionNalReferencia')
    municipio_notificacion = models.CharField(max_length=5, choices=municipios_CHOICES, null=True, blank=True, db_column='T012Cod_MunicipioNotificacionNal') 
    email_sucursal = models.EmailField(max_length=100, null=True, blank=True, db_column='T012emailSucursal')
    telefono_sucursal = models.CharField(max_length=15, null=True, blank=True, db_column='T012telContactoSucursal')
    es_principal = models.BooleanField(default=True, db_column='T012esPrincipal')
    activo = models.BooleanField(default=True, db_column='T012activo')
    item_ya_usado = models.BooleanField(default=False, db_column='T012itemYaUsado')
    
    def __str__(self):
        return str(self.descripcion_sucursal)
    
    class Meta:
        db_table = 'T012SucursalesEmpresa'
        verbose_name = 'Sucursal'
        verbose_name_plural = 'Sucursales'
        unique_together = [('id_persona_empresa','descripcion_sucursal'), ('numero_sucursal','id_persona_empresa')]
