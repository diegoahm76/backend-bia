from django.db import models

from transversal.choices.tipo_persona_choices import tipo_persona_CHOICES
from transversal.choices.cod_naturaleza_empresa_choices import cod_naturaleza_empresa_CHOICES
from transversal.models.organigrama_models import UnidadesOrganizacionales

class Personas(models.Model):
    id_persona = models.AutoField(primary_key=True, editable=False, db_column='T010IdPersona')
    tipo_documento = models.ForeignKey('transversal.TipoDocumento', on_delete=models.CASCADE, db_column='T010Cod_TipoDocumentoID')
    numero_documento = models.CharField(max_length=20, db_column='T010nroDocumentoID')
    cod_municipio_expedicion_id = models.ForeignKey('transversal.Municipio', related_name='cod_municipio_expedicion_id', on_delete=models.SET_NULL, null=True, blank=True, db_column='T010Cod_MunicipioExpID')
    digito_verificacion = models.CharField(max_length=1, null=True, blank=True, db_column='T010digitoVerificacion')
    tipo_persona = models.CharField(max_length=1, choices=tipo_persona_CHOICES, db_column='T010TipoPersona')
    cod_naturaleza_empresa = models.CharField(max_length=2, choices=cod_naturaleza_empresa_CHOICES, null=True, blank=True, db_column='T010codNaturalezaEmpresa')
    primer_nombre = models.CharField(max_length=30, null=True, blank=True, db_column='T010primerNombre')
    segundo_nombre = models.CharField(max_length=30, null=True, blank=True, db_column='T010segundoNombre')
    primer_apellido = models.CharField(max_length=30, null=True, blank=True, db_column='T010primerApellido')
    segundo_apellido = models.CharField(max_length=30, null=True, blank=True, db_column='T010segundoApellido')
    razon_social = models.CharField(max_length=200, null=True, blank=True, db_column='T010razonSocial')
    nombre_comercial = models.CharField(max_length=200, null=True, blank=True, db_column='T010nombreComercial')
    direccion_residencia = models.CharField(max_length=255, null=True, blank=True, db_column='T010dirResidencia')
    direccion_residencia_ref = models.CharField(max_length=255, null=True, blank=True, db_column='T010dirResidenciaReferencia')
    ubicacion_georeferenciada = models.DecimalField(max_digits=18, decimal_places=13, null=True, blank=True, db_column='T010dirResidenciaGeorefLat')
    ubicacion_georeferenciada_lon = models.DecimalField(max_digits=18, decimal_places=13, null=True, blank=True, db_column='T010dirResidenciaGeorefLon')
    municipio_residencia = models.ForeignKey('transversal.Municipio', related_name='municipio_residencia', on_delete=models.SET_NULL, null=True, blank=True, db_column='T010Cod_MunicipioResidenciaNal')
    pais_residencia = models.ForeignKey('transversal.Paises', related_name='pais_residencia', on_delete=models.SET_NULL, null=True, blank=True, db_column='T010Cod_PaisResidenciaExterior')
    direccion_laboral = models.CharField(max_length=255, null=True, blank=True, db_column='T010dirLaboralNal')
    cod_municipio_laboral_nal = models.ForeignKey('transversal.Municipio', related_name='cod_municipio_laboral_nal', on_delete=models.SET_NULL, null=True, blank=True, db_column='T010Cod_MunicipioLaboralNal')
    direccion_notificaciones = models.CharField(max_length=255, null=True, blank=True, db_column='T010dirNotificacionNal')
    direccion_notificacion_referencia = models.CharField(max_length=255, null=True, blank=True, db_column='T010dirNotificacionNalReferencia')
    cod_municipio_notificacion_nal = models.ForeignKey('transversal.Municipio', related_name='cod_municipio_notificacion_nal', on_delete=models.SET_NULL, null=True, blank=True, db_column='T010Cod_MunicipioNotificacionNal')
    email = models.EmailField(null=True, blank=True, max_length=100, db_column='T010emailNotificacion')
    email_empresarial = models.EmailField(max_length=100, null=True, blank=True, db_column='T010emailEmpresarial')
    telefono_fijo_residencial = models.CharField(max_length=15, null=True, blank=True, db_column='T010telFijoResidencial')
    telefono_celular = models.CharField(max_length=15, null=True, blank=True, db_column='T010telCelularPersona')
    telefono_empresa = models.CharField(max_length=15, null=True, blank=True, db_column='T010telEmpresa')
    telefono_celular_empresa = models.CharField(max_length=15, blank=True, null=True, db_column='T010telCelularEmpresa')
    telefono_empresa_2 = models.CharField(max_length=15, null=True, blank=True, db_column='T010telEmpresa2')
    cod_pais_nacionalidad_empresa = models.ForeignKey('transversal.Paises', related_name='cod_pais_nacionalidad_empresa', on_delete=models.SET_NULL, null=True, blank=True, db_column='T010Cod_PaisNacionalidadDeEmpresa')
    representante_legal = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, db_column='T010Id_PersonaRepLegal', related_name='rep_legal')
    fecha_cambio_representante_legal = models.DateTimeField(null=True, blank=True, db_column='T010fechaCambioRepLegal')
    fecha_inicio_cargo_rep_legal = models.DateField(null=True, blank=True, db_column='T010fechaInicioCargoRepLegal')
    fecha_nacimiento = models.DateField(blank=True,null=True, db_column='T010fechaNacimiento')
    pais_nacimiento = models.ForeignKey('transversal.Paises', on_delete=models.SET_NULL, null=True, blank=True, db_column='T010Cod_PaisNacimiento')
    sexo = models.ForeignKey('transversal.Sexo', on_delete=models.SET_NULL, null=True, blank=True, db_column='T010Cod_Sexo')
    estado_civil = models.ForeignKey('transversal.EstadoCivil', related_name="estado_civil", on_delete=models.SET_NULL, null=True, blank=True, db_column='T010Cod_EstadoCivil')
    id_cargo = models.ForeignKey('transversal.Cargos', on_delete=models.SET_NULL, null=True, blank=True, db_column='T010Id_CargoActual')
    fecha_inicio_cargo_actual = models.DateTimeField(null=True, blank=True, db_column='T010fechaInicioCargoActual')
    fecha_a_finalizar_cargo_actual = models.DateField(null=True, blank=True, db_column='T010fechaAFinalizarCargoActual')
    observaciones_vinculacion_cargo_actual = models.CharField(max_length=100, null=True, blank=True, db_column='T010observacionesVincuCargoActual')
    id_unidad_organizacional_actual = models.ForeignKey(UnidadesOrganizacionales, on_delete=models.SET_NULL, null=True, blank=True, db_column='T010Id_UnidadOrganizacionalActual')
    fecha_asignacion_unidad = models.DateTimeField(null=True, blank=True, db_column='T010fechaAsignacionUnidadOrg')
    es_unidad_organizacional_actual = models.BooleanField(null=True, blank=True, db_column='T010esUnidadDeOrganigramaActual')
    acepta_notificacion_sms = models.BooleanField(default=False, db_column='T010aceptaNotificacionSMS')
    acepta_notificacion_email = models.BooleanField(default=False, db_column='T010aceptaNotificacionEMail')
    fecha_ultim_actualizacion_autorizaciones = models.DateTimeField(null=True, blank=True, db_column='T010fechaUltActuaAutorizaciones')
    acepta_tratamiento_datos = models.BooleanField(null=True, blank=True, db_column='T010aceptaTratamientoDeDatos')
    fecha_creacion = models.DateTimeField(auto_now_add=True, db_column='T010fechaCreacion')
    id_persona_crea = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, db_column='T010Id_PersonaCrea', related_name='persona_crea')
    fecha_ultim_actualiz_diferente_crea = models.DateTimeField(null=True, blank=True, db_column='T010fechaUltActuaDifCrea')
    id_persona_ultim_actualiz_diferente_crea = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, db_column='T010Id_PersonaUltActuaDifCrea', related_name='persona_ult_act_dif')

    def __str__(self):
        return str(self.primer_nombre) + ' ' + str(self.primer_apellido)
    
    class Meta:
        db_table = 'T010Personas'
        verbose_name = 'Persona'
        verbose_name_plural = 'Personas'
        unique_together = ['tipo_documento', 'numero_documento']