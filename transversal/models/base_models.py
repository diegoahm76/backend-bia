from django.db import models
from transversal.models.organigrama_models import UnidadesOrganizacionales

from transversal.models.personas_models import Personas
from transversal.choices.tipo_direccion_choices import tipo_direccion_CHOICES

from django.conf import settings
from random import choice, choices
from string import ascii_letters, digits

class Paises(models.Model):
    cod_pais = models.CharField(primary_key=True, max_length=2, db_column='T003CodPais')
    nombre = models.CharField(max_length=50, unique=True, db_column='T003nombre')
    
    def __str__(self):
        return str(self.cod_pais)
    
    class Meta:
        db_table = "T003Paises"
        verbose_name = 'Pais'
        verbose_name_plural = 'Paises'

class Municipio(models.Model):
    cod_municipio = models.CharField(primary_key=True, max_length=5, db_column='T001CodMunicipio')
    nombre = models.CharField(max_length=30, db_column='T001nombre')
    cod_departamento = models.ForeignKey('Departamento', on_delete=models.CASCADE, db_column='T001Cod_Departamento')

    def __str__(self):
        return str(self.nombre)

    class Meta:
        db_table = 'T001MunicipiosDepartamento'
        verbose_name = 'Municipio'
        verbose_name_plural = 'Municipios'
        unique_together = (('nombre', 'cod_departamento'),)
        
class Departamento(models.Model):
    cod_departamento = models.CharField(primary_key=True, max_length=2, db_column='T002CodDepartamento')
    nombre = models.CharField(max_length=50, unique=True, db_column='T002nombre')
    pais = models.ForeignKey(Paises, on_delete=models.CASCADE, db_column='T002Cod_Pais')

    def __str__(self):
        return str(self.nombre)

    class Meta:
        db_table = 'T002DepartamentosPais'
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'

class Sexo(models.Model):
    cod_sexo = models.CharField(primary_key=True, max_length=1, db_column='T004CodSexo')
    nombre = models.CharField(max_length=20, unique=True, db_column='T004nombre')

    def __str__(self):  
        return str(self.nombre)
    
    class Meta:
        db_table = 'T004Sexo'
        verbose_name = 'Sexo'
        verbose_name_plural = 'Sexo'
        
class EstadoCivil(models.Model):
    cod_estado_civil = models.CharField(max_length=1, primary_key=True, db_column='T005CodEstadoCivil')
    nombre = models.CharField(max_length=20, unique=True, db_column='T005nombre')
    precargado = models.BooleanField(default=False, db_column='T005registroPrecargado')
    activo = models.BooleanField(default=True, db_column='T005activo')
    item_ya_usado = models.BooleanField(default=False, db_column='T005itemYaUsado')
    
    def __str__(self):
        return str(self.nombre)
    
    class Meta:
        db_table = 'T005EstadoCivil'
        verbose_name = 'Estado civil'
        verbose_name_plural = 'Estados civiles'

class TipoDocumento(models.Model):
    cod_tipo_documento = models.CharField(max_length=2, primary_key=True, db_column='T006CodTipoDocumentoID')
    nombre = models.CharField(max_length=40, unique=True, db_column='T006nombre')
    precargado = models.BooleanField(default=False, db_column='T006registroPrecargado')
    activo = models.BooleanField(default=True, db_column='T006activo')
    item_ya_usado = models.BooleanField(default=False, db_column='T006itemYaUsado')
    def __str__(self):
        return str(self.nombre)
    
    class Meta:
        db_table = 'T006TiposDocumentoID'
        verbose_name = 'Tipo de documento'
        verbose_name_plural = 'Tipos de documentos'
        

class Cargos(models.Model):
    id_cargo = models.SmallAutoField(primary_key=True, editable=False, db_column='T009IdCargo')
    nombre = models.CharField(max_length=50, unique=True, db_column='T009nombre')
    activo = models.BooleanField(default=True, db_column='T009activo')
    item_usado = models.BooleanField(default=False, db_column='T009itemYaUsado')
    
    def __str__(self):
        return str(self.nombre)
        
    class Meta:
        db_table = 'T009Cargos'
        verbose_name = 'Cargo'
        verbose_name_plural = 'Cargos'

class ClasesTercero(models.Model):
    id_clase_tercero = models.SmallAutoField(primary_key=True, editable=False, db_column='T007IdClaseTercero')
    nombre = models.CharField(max_length=30, unique=True, db_column='T007nombre')
    
    def __str__(self):
        return str(self.nombre)

    class Meta:
        db_table = 'T007ClasesTercero'
        verbose_name = 'Clase tercero'
        verbose_name_plural = 'Clase terceros'
        
class ClasesTerceroPersona(models.Model):
    id_clase_tercero_persona = models.SmallAutoField(primary_key=True, editable=False, db_column='T011IdClasesTercero_Persona')
    id_persona = models.ForeignKey(Personas, on_delete=models.CASCADE, db_column='T011Id_Persona')
    id_clase_tercero = models.ForeignKey(ClasesTercero, on_delete=models.CASCADE, db_column='T011Id_ClaseTercero')
    
    def __str__(self):
        return str(self.id_persona) + ' ' + str(self.id_clase_tercero)
    
    class Meta:
        db_table = 'T011ClasesTercero_Persona'
        verbose_name = 'Clase tercero persona'
        verbose_name_plural = 'Clase tercero personas'
        unique_together = (('id_persona', 'id_clase_tercero'),)
        
class ApoderadoPersona(models.Model):
    id_apoderados_persona = models.SmallAutoField(primary_key= True, editable= False, db_column="T013IdApoderados_Persona")
    persona_poderdante = models.ForeignKey(Personas, on_delete=models.CASCADE, related_name='persona_poderdante', db_column='T013Id_PersonaPoderdante')
    persona_apoderada = models.ForeignKey(Personas, on_delete=models.CASCADE, related_name='persona_apoderada', db_column='T013Id_PersonaApoderada')
    id_proceso = models.IntegerField(db_column='T013Id_Proceso')
    consecutivo_del_proceso = models.SmallIntegerField(db_column='T013consecDelProceso')
    fecha_inicio = models.DateField(db_column='T013fechaInicio')
    fecha_cierre = models.DateField(db_column='T013fechaCierre', null=True, blank=True)
    
    def __str__(self):
        return str(self.id_proceso)

    class Meta:
        db_table = 'T013Apoderados_Persona'    
        verbose_name = 'Apoderado'
        verbose_name_plural = 'Apoderados'
        unique_together = (('persona_poderdante', 'persona_apoderada', 'id_proceso', 'consecutivo_del_proceso'),)

class HistoricoDireccion(models.Model):
    id_historico_direccion = models.AutoField(primary_key=True, editable=False, db_column='T015IdHistoDireccion')
    id_persona = models.ForeignKey(Personas, on_delete=models.CASCADE, db_column='T015Id_Persona')    
    direccion = models.CharField(max_length=255, db_column='T015direccion')
    cod_municipio = models.ForeignKey(Municipio, on_delete=models.SET_NULL, null=True, blank=True, db_column='T015Cod_MunicipioEnCol')
    cod_pais_exterior = models.ForeignKey(Paises, on_delete=models.SET_NULL, null=True, blank=True, db_column='T015Cod_PaisEnElExterior')
    tipo_direccion = models.CharField(max_length=3, choices=tipo_direccion_CHOICES, db_column='T015tipoDeDireccion')
    fecha_cambio = models.DateTimeField(auto_now_add=True, db_column='T015fechaCambio')
        
    def __str__(self):
        return str(self.id_historico_direccion)

    class Meta:
        db_table = 'T015HistoricoDirecciones'
        verbose_name = 'Histórico de dirección'
        verbose_name_plural = 'Histórico de direcciones'

class HistoricoEmails(models.Model):
    id_histo_email = models.AutoField(primary_key=True, db_column='T016IdHistoEmail')
    id_persona = models.ForeignKey(Personas, on_delete=models.CASCADE, db_column='T016Id_Persona')
    email_notificacion = models.EmailField(max_length=100, db_column='T016emailDeNotificacion')
    fecha_cambio = models.DateTimeField(auto_now=True, db_column='T016fechaCambio')

    def __str__(self):
        return str(self.email_notificacion)

    class Meta:
        db_table = 'T016HistoricoEmails'      
        verbose_name = 'Historico de email'
        verbose_name_plural = 'Históricos de email'
        
class HistoricoAutirzacionesNotis(models.Model):
    id_historico_autoriza_noti = models.AutoField(primary_key=True, editable=False, db_column='T021IdHistoricoAutorizaNoti')
    id_persona = models.ForeignKey(Personas, on_delete=models.CASCADE, db_column='T021Id_Persona')
    respuesta_autorizacion_sms = models.BooleanField(default=True, db_column='T021rtaAutorizacionSMS')
    respuesta_autorizacion_mail = models.BooleanField(default=True, db_column='T021rtaAutorizacioneMail')
    fecha_inicio = models.DateTimeField(db_column='T021fechaInicio')
    fecha_fin = models.DateTimeField(auto_now=True, db_column='T021fechaFin')

    def __str__(self):
        return str(self.id_historico_autoriza_noti) 
    
    class Meta:
        db_table = 'T021HistoricoAutorizaNotis'  
        verbose_name = 'Histórico de autorización de notificación'
        verbose_name_plural = 'Histórico de autorizaciones de notificaciones'


class HistoricoRepresentLegales(models.Model):
    id_historico_represent_legal = models.AutoField(primary_key=True, editable=False, db_column='T022IdHistoricoRepLegal')
    id_persona_empresa = models.ForeignKey(Personas, on_delete=models.CASCADE, db_column='T022Id_PersonaEmpresa', related_name='persona_empresa_historico')
    consec_representacion = models.SmallIntegerField(db_column='T022consecRepresentacion')
    id_persona_represent_legal = models.ForeignKey(Personas, on_delete=models.CASCADE, db_column='T022Id_PersonaRepLegal', related_name='rep_legal_historico')
    fecha_cambio_sistema = models.DateTimeField(db_column='T022fechaCambioEnSistema')
    fecha_inicio_cargo = models.DateTimeField(db_column='T022fechaInicioCargo')

    def __str__(self):
        return str(self.id_persona_empresa + ' ' + str(self.consec_representacion))
    
    class Meta:
        db_table = 'T022HistoricoRepLegales'
        verbose_name = 'Histórico de representante legal'
        verbose_name_plural = 'Histórico de representantes legales'

class HistoricoCargosUndOrgPersona(models.Model):
    id_historico_cargo_und_org_persona = models.AutoField(primary_key=True, editable=False, db_column='T023IdHistoCargoUndOrg_Persona')
    id_persona = models.ForeignKey(Personas, on_delete=models.CASCADE, db_column='T023Id_Persona')
    id_cargo =  models.ForeignKey(Cargos, on_delete=models.CASCADE, db_column='T023Id_Cargo')
    id_unidad_organizacional = models.ForeignKey(UnidadesOrganizacionales, on_delete=models.CASCADE, db_column='T023Id_UnidadOrganizacional')
    fecha_inicial_historico = models.DateTimeField(db_column='T023fechaInicialHisto')
    fecha_final_historico = models.DateTimeField(db_column='T023fechaFinalHisto')
    observaciones_vinculni_cargo = models.CharField(max_length=100, null=True, blank=True, db_column='T023observacionesVincuIniCargo')
    justificacion_cambio_und_org = models.CharField(max_length=100, null=True, blank=True, db_column='T023justificacionCambioUndOrg')
    desvinculado = models.BooleanField(default=True, db_column='T023desvinculado')
    fecha_desvinculacion = models.DateTimeField(null=True, blank=True, db_column='T023fechaDesvinculacion')
    observaciones_desvinculacion = models.CharField(max_length=100, null=True, blank=True, db_column='T023observacionesDesvincu')
    
    def __str__(self):
        return str(self.id_historico_cargo_und_org_persona) 
    
    class Meta:
        db_table = 'T023HistoricoCargosUndOrg_Persona'  
        verbose_name = 'Histórico de cargo de unidad organizacional'
        verbose_name_plural = 'Histórico de cargos de unidades organizacionales'

class HistoricoCambiosIDPersonas (models.Model):
    historico_cambio_id_persona = models.AutoField(primary_key=True, editable=False, db_column='T024IdHistoCambioId_Persona')
    id_persona = models.ForeignKey(Personas, on_delete=models.CASCADE, db_column='T024Id_Persona')
    nombre_campo_cambiado = models.CharField(max_length=255, db_column='T024nombreCampoCambiado')
    valor_campo_cambiado = models.CharField(max_length=255, db_column='T024valorCampoCambiado')
    ruta_archivo_soporte = models.FileField(upload_to='transversal/modificacion_campos_restringidos/', max_length=255, blank=True, null=True, db_column='T024rutaArchivoSoporte')
    fecha_cambio = models.DateTimeField(auto_now=True, db_column='T024fechaCambio')
    justificacion_cambio = models.CharField(max_length=255, db_column='T024justificacionCambio') 

    def __str__(self):
        return str(self.historico_cambio_id_persona) 
    
    class Meta:
        db_table = 'T024HistoricoCambiosId_Personas'  
        verbose_name = 'Histórico de cambio id persona'
        verbose_name_plural = 'Histórico de cambios id personas'
    
class Shortener(models.Model):
    id_abreviacion_dir = models.SmallAutoField(db_column='TzIdAbreviacionDir', primary_key=True)
    created = models.DateTimeField(auto_now_add=True, db_column='TzfechaCreacion')
    long_url = models.URLField(max_length=500, db_column='TzdirLarga')
    short_url = models.CharField(max_length=15, unique=True, db_column='TzdirCorta')

    class Meta:
        db_table = 'TzAbreviacionesDir'  
        verbose_name = 'Abreviación Dir'
        verbose_name_plural = 'Abreviaciones Dir'
        ordering = ["-created"]

    def __str__(self):
        return f'{self.long_url} to {self.short_url}'
    
    def save(self, *args, **kwargs):
        # Try to get the value from the settings module
        SIZE = getattr(settings, "MAXIMUM_URL_CHARS", 7)

        AVAIABLE_CHARS = ascii_letters + digits
        
        random_code = "".join(
            [choice(AVAIABLE_CHARS) for _ in range(SIZE)]
        )

        model_class = self.__class__
        
        exist = model_class.objects.filter(short_url=random_code).exists()
        
        while exist:
            random_code = "".join(
                [choice(AVAIABLE_CHARS) for _ in range(SIZE)]
            )
            
            exist = model_class.objects.filter(short_url=random_code).exists()
            
        # If the short url wasn't specified
        if not self.short_url:
            # We pass the model instance that is being saved
            self.short_url = random_code

        super().save(*args, **kwargs)