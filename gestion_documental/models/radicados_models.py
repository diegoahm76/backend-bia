from django.db import models
from gestion_documental.choices.tipos_pqr_choices import TIPOS_PQR
from gestion_documental.models.expedientes_models import ArchivosDigitales, DocumentosDeArchivoExpediente
from gestion_documental.models.trd_models import TipologiasDoc
from seguridad.models import Personas
from gestion_documental.choices.tipo_radicado_choices import TIPOS_RADICADO_CHOICES
from transversal.models.base_models import Municipio
from transversal.models.entidades_models import SucursalesEmpresas
class ConfigTiposRadicadoAgno(models.Model):

    
    id_config_tipo_radicado_agno = models.SmallAutoField(primary_key=True, db_column='T235IdConfigTipoRadicadoAgno')
    agno_radicado = models.SmallIntegerField(db_column='T235agnoRadicado')
    cod_tipo_radicado = models.CharField(max_length=1, choices=TIPOS_RADICADO_CHOICES, db_column='T235codTipoRadicado')
    prefijo_consecutivo = models.CharField(null=True,max_length=10, db_column='T235prefijoConsecutivo')
    consecutivo_inicial = models.IntegerField(null=True,db_column='T235consecutivoInicial')
    cantidad_digitos = models.SmallIntegerField(null=True,db_column='T235cantidadDigitos')
    implementar = models.BooleanField(db_column='T235implementar')
    id_persona_config_implementacion = models.ForeignKey('transversal.Personas',null=True, on_delete=models.CASCADE, db_column='T235Id_PersonaConfigImplementacion',related_name='T235Id_PersonaConfigImplementacion')
    fecha_inicial_config_implementacion = models.DateTimeField(null=True,db_column='T235fechaInicialConfigImplementacion')
    consecutivo_actual = models.IntegerField(null=True,db_column='T235consecutivoActual')
    fecha_consecutivo_actual = models.DateTimeField(null=True,db_column='T235fechaConsecutivoActual')
    id_persona_consecutivo_actual = models.ForeignKey('transversal.Personas',null=True, on_delete=models.CASCADE, db_column='T235Id_PersonaConsecutivoActual',related_name='FK2_T235ConfigTiposRadicadoAgno')

    class Meta:
        db_table = 'T235ConfigTiposRadicadoAgno'
        unique_together = ['agno_radicado', 'cod_tipo_radicado']

class TiposPQR(models.Model):


    cod_tipo_pqr = models.CharField( primary_key=True,max_length=1,choices=TIPOS_PQR,db_column='T252CodTipoPQR')
    nombre = models.CharField(max_length=15,unique=True,db_column='T252nombre', verbose_name='Nombre del Tipo de PQR' )
    tiempo_respuesta_en_dias = models.SmallIntegerField(null=True,blank=True,db_column='T252tiempoRtaEnDias')
    
    def __str__(self):
        return self.nombre
    class Meta:
        db_table = 'T252TiposPQR'  
        verbose_name = 'Tipo de PQR'  
        verbose_name_plural = 'Tipos de PQR' 

class MediosSolicitud(models.Model):
    id_medio_solicitud = models.SmallAutoField(primary_key=True, db_column='T253IdMedioSolicitud')
    nombre = models.CharField(max_length=50, db_column='T253nombre',unique=True)
    aplica_para_pqrsdf = models.BooleanField(default=False, db_column='T253aplicaParaPQRSDF')
    aplica_para_tramites = models.BooleanField(default=False, db_column='T253aplicaParaTramites')
    aplica_para_otros = models.BooleanField(default=False, db_column='T253aplicaParaOtros')
    registro_precargado = models.BooleanField(default=False, db_column='T253registroPrecargado')
    activo = models.BooleanField(default=False, db_column='T253activo')
    item_ya_usado = models.BooleanField(default=False, db_column='T253itemYaUsado')

    class Meta:
        db_table = 'T253MediosSolicitud'  
        verbose_name = 'Medio de Solicitud'  
        verbose_name_plural = 'Medios de Solictud' 


class EstadosSolicitudes(models.Model):
    id_estado_solicitud = models.SmallAutoField(primary_key=True, db_column='T254IdEstadoSolicitud')
    nombre = models.CharField(max_length=50, db_column='T254nombre')
    aplica_para_pqrsdf = models.BooleanField(db_column='T254aplicaParaPQRSDF')
    aplica_para_tramites = models.BooleanField(db_column='T254aplicaParaTramites')
    aplica_para_otros = models.BooleanField(db_column='T254aplicaParaOtros')

    class Meta:
       
        db_table = 'T254EstadosSolicitudes'
        verbose_name = 'Estado de Solicitud'  
        verbose_name_plural = 'Estados de Solictud' 


RELACION_TITULAR = [
        ('MP', 'Misma persona'),
        ('RL', 'Representante legal'),
        ('AP', 'Apoderado'),

    ]

FORMA_PRESENTACION = [
    ('V', 'Verbal'),
    ('E', 'Escrita'),
]    

    

class PQRSDF(models.Model):
    IdPQRSDF = models.AutoField(primary_key=True, db_column='T257IdPQRSDF')
    codTipoPQRSDF = models.CharField(max_length=1,choices=TIPOS_PQR,db_column='T257codTipoPQRSDF')#,max_length=1,choices=TIPOS_PQR
    Id_PersonaTitular = models.ForeignKey('transversal.Personas',null=True,on_delete=models.CASCADE,db_column='T257Id_PersonaTitular', related_name='persona_titular_relacion')# models.ForeignKey('transversal.Personas',null=True, on_delete=models.CASCADE,
    Id_PersonaInterpone = models.ForeignKey('transversal.Personas',null=True,on_delete=models.CASCADE,db_column='T257Id_PersonaInterpone',related_name='persona_interpone_relacion')
    codRelacionConElTitular = models.CharField(max_length=2, choices=RELACION_TITULAR, db_column='T257codRelacionConElTitular')
    esAnonima = models.BooleanField(default=False, db_column='T257esAnonima')
    fechaRegistro = models.DateTimeField(db_column='T257fechaRegistro')
    Id_MedioSolicitud = models.SmallIntegerField(db_column='T257Id_MedioSolicitud')
    codFormaPresentacion = models.CharField(max_length=1, choices=FORMA_PRESENTACION, db_column='T257codFormaPresentacion')
    asunto = models.CharField(max_length=100, db_column='T257asunto')
    descripcion = models.CharField(max_length=500, db_column='T257descripcion')
    cantidadAnexos = models.SmallIntegerField(db_column='T257cantidadAnexos')
    nroFoliosTotales = models.SmallIntegerField(db_column='T257nroFoliosTotales')
    requiereRta = models.BooleanField(default=False, db_column='T257requiereRta')
    diasParaRespuesta = models.SmallIntegerField(db_column='T257diasParaRespuesta', null=True)
    Id_SucursalEspecificaImplicada = models.ForeignKey(SucursalesEmpresas,on_delete=models.CASCADE,db_column='T257Id_SucursalEspecificaImplicada', null=True)
    Id_PersonaRecibe = models.ForeignKey('transversal.Personas',on_delete=models.CASCADE,db_column='T257Id_PersonaRecibe', null=True,related_name='persona_recibe_ralacion')
    Id_Sucursal_RecepcionFisica = models.ForeignKey(SucursalesEmpresas,on_delete=models.CASCADE,db_column='T257Id_Sucursal_RecepcionFisica', null=True,related_name='sucursal_recepciona_ralacion')
    Id_Radicado = models.IntegerField(db_column='T257Id_Radicado', null=True)#IMPLEMENTAR TABLA RADICADOS
    fechaRadicado = models.DateTimeField(db_column='T257fechaRadicado', null=True)
    requiereDigitalizacion = models.BooleanField(default=False, db_column='T257requiereDigitalizacion')
    fechaEnvioDefinitivoADigitalizacion = models.DateTimeField(db_column='T257fechaEnvioDefinitivoADigitalizacion', null=True)
    fechaDigitalizacionCompletada = models.DateTimeField(db_column='T257fechaDigitalizacionCompletada', null=True)
    fechaRtaFinalGestion = models.DateTimeField(db_column='T257fechaRtaFinalGestion', null=True)
    Id_PersonaRtaFinalGestion = models.ForeignKey('transversal.Personas',on_delete=models.CASCADE,db_column='T257Id_PersonaRtaFinalGestion', null=True,related_name='persona_rta_final_gestion_ralacion')
    Id_EstadoActualSolicitud = models.SmallIntegerField(db_column='T257Id_EstadoActualSolicitud')
    fechaIniEstadoActual = models.DateTimeField(db_column='T257fechaIniEstadoActual')
    Id_DocDeArch_Exp = models.IntegerField(db_column='T257Id_DocDeArch_Exp', null=True)
    Id_ExpedienteDoc = models.IntegerField(db_column='T257Id_ExpedienteDoc', null=True)

    class Meta:
       
        db_table = 'T257PQRSDF'

from django.db import models

class Estados_PQR(models.Model):
    T255IdEstado_PQR = models.AutoField(primary_key=True, db_column='T255IdEstado_PQR')
    PQRSDF = models.ForeignKey(PQRSDF,on_delete=models.CASCADE,db_column='T255Id_PQRSDF', null=True)
    SolicitudAlUsuSobrePQR = models.IntegerField(db_column='T255Id_SolicitudAlUsuSobrePQR', null=True)#PENDIENTE MODELO T266
    EstadoSolicitud = models.ForeignKey(EstadosSolicitudes,on_delete=models.CASCADE,db_column='T255Id_EstadoSolicitud')
    fechaIniEstado = models.DateTimeField(db_column='T255fechaIniEstado')
    PersonaGeneraEstado = models.ForeignKey('transversal.Personas',on_delete=models.CASCADE,db_column='T255Id_PersonaGeneraEstado', null=True)
    Estado_PQR_Asociado = models.IntegerField(db_column='T255Id_Estado_PQR_Asociado', null=True)#PENDIENTE MODELO T255

    class Meta:
       # managed = False  # Evita que Django gestione esta tabla en la base de datos.
        db_table = 'T255Estados_PQR'
from django.db import models

class InfoDenuncias_PQRSDF(models.Model):
    IdInfoDenuncia_PQRSDF = models.AutoField(primary_key=True, db_column='T256IdInfoDenuncia_PQRSDF')
    Id_PQRSDF = models.ForeignKey(PQRSDF,on_delete=models.CASCADE,db_column='T256Id_PQRSDF', null=True)
    Cod_MunicipioLocalizacionHecho = models.ForeignKey(Municipio,on_delete=models.CASCADE,max_length=5, db_column='T256Cod_MunicipioLocalizacionHecho')
    CodZonaLocalizacion = models.CharField(max_length=1, choices=[('U', 'Urbana'), ('R', 'Rural')], db_column='T256codZonaLocalizacion')
    BarrioOVeredaLocalizacion = models.CharField(max_length=100, db_column='T256barrioOVeredaLocalizacion', null=True)
    DireccionLocalizacion = models.CharField(max_length=255, db_column='T256direccionLocalizacion', null=True)
    CodRecursosAfectadosPresuntos = models.CharField(max_length=2, choices=[('Su', 'Suelo'), ('Ag', 'Agua'), ('Ai', 'Aire'), ('Fl', 'Flora'), ('Fs', 'Fauna silvestre'), ('Ot', 'Otros')], db_column='T256codRecursosAfectadosPresuntos')
    OtroRecursoAfectado_Cual = models.CharField(max_length=50, db_column='T256otroRecursoAfectado_Cual', null=True)
    EvidenciasSoportanHecho = models.CharField(max_length=1000, db_column='T256evidenciasSoportanHecho', null=True)
    NombreCompleto_PresuntoInfractor = models.CharField(max_length=130, db_column='T256nombreCompleto_PresuntoInfractor', null=True)
    Telefono_PresuntoInfractor = models.CharField(max_length=15, db_column='T256telefono_PresuntoInfractor', null=True)
    Direccion_PresuntoInfractor = models.CharField(max_length=255, db_column='T256direccion_PresuntoInfractor', null=True)
    YaHabiaPuestoEnConocimiento = models.BooleanField(db_column='T256yaHabiaPuestoEnConocimiento')
    AnteQueAutoridadHabíaInterpuesto = models.CharField(max_length=200, db_column='T256anteQueAutoridadHabíaInterpuesto', null=True)

    class Meta:
        #managed = False  # Evita que Django gestione esta tabla en la base de datos.
        db_table = 'T256InfoDenuncias_PQRSDF'

class Anexos(models.Model):
    IdAnexo = models.AutoField(primary_key=True, db_column='T258IdAnexo')
    nombreAnexo = models.CharField(max_length=50, db_column='T258nombreAnexo')
    ordenAnexoEnElDoc = models.SmallIntegerField(db_column='T258ordenAnexoEnElDoc')
    codMedioAlmacenamiento = models.CharField(max_length=1, choices=[('D', 'Digital'), ('F', 'Físico'), ('O', 'Otros')], db_column='T258codMedioAlmacenamiento')
    medioAlmacenamientoOtros_Cual = models.CharField(max_length=30, db_column='T258medioAlmacenamientoOtros_Cual', null=True)
    numeroFolios = models.SmallIntegerField(db_column='T258numeroFolios')
    yaDigitalizado = models.BooleanField(db_column='T258yaDigitalizado')
    observacionDigitalizacion = models.CharField(max_length=100, db_column='T258observacionDigitalizacion', null=True)
    Id_DocuDeArch_Exp = models.ForeignKey(DocumentosDeArchivoExpediente,on_delete=models.CASCADE,db_column='T258Id_DocuDeArch_Exp', null=True)

    class Meta:
        #managed = False  # Evita que Django gestione esta tabla en la base de datos.
        db_table = 'T258Anexos'



from django.db import models

class MetadatosAnexosTmp(models.Model):
    IdMetadatosAnexo_Tmp = models.AutoField(primary_key=True, db_column='T260IdMetadatos_Anexo_Tmp')
    Id_Anexo = models.ForeignKey(Anexos, on_delete=models.CASCADE, db_column='T260Id_Anexo')
    nombreOriginalDelArchivo = models.CharField(max_length=50, db_column='T260nombreOriginalDelArchivo', null=True)
    fechaCreacionDoc = models.DateField(db_column='T260fechaCreacionDoc', null=True)
    descripcion = models.CharField(max_length=500, db_column='T260descripcion', null=True)
    asunto = models.CharField(max_length=150, db_column='T260asunto', null=True)
    codCategoriaArchivo = models.CharField(max_length=2, choices=[('Tx', 'Texto'), ('Im', 'Imagen'), ('Au', 'Audio'), ('Vd', 'Video'), ('Mp', 'Modelado de Procesos'), ('Ge', 'Geoespacial'), ('Bd', 'Base de Datos'), ('Pw', 'Páginas Web'), ('Ce', 'Correo Electrónico')], db_column='T260codCategoriaArchivo', null=True)
    esVersionOriginal = models.BooleanField(db_column='T260esVersionOriginal')
    tieneReplicaFisica = models.BooleanField(db_column='T260tieneReplicaFisica')
    nroFoliosDocumento = models.SmallIntegerField(db_column='T260nroFoliosDocumento')
    codOrigenArchivo = models.CharField(max_length=1, choices=[('E', 'Electrónico'), ('F', 'Físico'), ('D', 'Digitalizado')], db_column='T260codOrigenArchivo')
    Id_TipologiaDoc = models.ForeignKey(TipologiasDoc, on_delete=models.CASCADE, db_column='T260Id_TipologiaDoc', null=True)
    codTipologiaDoc_Prefijo = models.CharField(max_length=10, db_column='T260codTipologiaDoc_Prefijo', null=True)
    codTipologiaDoc_Agno = models.SmallIntegerField(db_column='T260codTipologiaDoc_Agno', null=True)
    codTipologiaDoc_Consecutivo = models.CharField(max_length=20, db_column='T260codTipologiaDoc_Consecutivo', null=True)
    tipologiaNoCreadaEnTRD = models.CharField(max_length=50, db_column='T260tipologiaNoCreadaEnTRD', null=True)
    palabrasClaveDoc = models.CharField(max_length=255, db_column='T260palabrasClaveDoc', null=True)
    Id_ArchivoEnSistema = models.ForeignKey(ArchivosDigitales, on_delete=models.CASCADE, db_column='T260Id_ArchivoEnSistema')

    class Meta:
        #managed = False  # Evita que Django gestione esta tabla en la base de datos.
        db_table = 'T260Metadatos_Anexos_Tmp'
        unique_together = ('Id_Anexo',)  # Restricción para que Id_Anexo sea único
