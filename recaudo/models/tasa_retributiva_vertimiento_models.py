from django.db import models

# from gestion_documental.models.expedientes_models import ArchivosDigitales

class documento_formulario_recuado(models.Model):
    id_documento = models.AutoField(primary_key=True,db_column='TXXXIdDocumentoFormularioRecaudo')
    id_persona = models.ForeignKey('transversal.Personas', on_delete=models.CASCADE,db_column='TXXXId_Persona')	
    radicado = models.CharField(max_length=225, db_column='TXXXRadicado')
    id_archivo_sistema	= models.ForeignKey('gestion_documental.ArchivosDigitales', on_delete=models.CASCADE, db_column='TXXXId_ArchivoEnSistema')
    ids_destinatarios_personas = models.CharField(max_length=225, db_column='TXXXIds_Destinatarios_Personas')
    ids_destinatarios_unidades = models.CharField(max_length=225, db_column='TXXXIds_Destinatarios_Unidades')



    class Meta:
        db_table = 'TXXXDocumentoFormularioRecuado'
        verbose_name = 'Documento de Formulario de Recuado'
        verbose_name_plural = 'Documentos de Formularios de Recuado'
        #unique_together = ('codigo_exp_und_serie_subserie', 'codigo_exp_Agno', 'codigo_exp_consec_por_agno')



class InformacionFuente(models.Model):
    numero = models.PositiveIntegerField()
    tipo = models.CharField(max_length=255)
    nombreFuente = models.CharField(max_length=255)
    caudalConcesionado = models.CharField(max_length=255)
    sistemaMedicionAguaCaptada = models.CharField(max_length=255)

    def __str__(self):
        return f"aT452_{self.numero} - {self.nombreFuente}"

    class Meta:
        verbose_name = 'Información de Fuente'
        verbose_name_plural = 'Información de Fuentes'


class CoordenadasSitioCaptacion(models.Model):
    cordenadaX = models.FloatField()
    cordenadaY = models.FloatField()

    def __str__(self):
        return f"T453_{self.cordenadaX}, {self.cordenadaY}"

    class Meta:
        verbose_name = 'Coordenadas de Sitio de Captación'
        verbose_name_plural = 'Coordenadas de Sitios de Captación'


class FactoresUtilizacion(models.Model):
    numeroUsuarios = models.PositiveIntegerField()
    numeroBovinos = models.PositiveIntegerField()
    numeroPorcinos = models.PositiveIntegerField()
    numeroHectareas = models.PositiveIntegerField()
    consumoNumeroUsuarios = models.PositiveIntegerField()

    def __str__(self):
        return f"T454_{self.numeroUsuarios} - {self.numeroBovinos} - {self.numeroPorcinos} - {self.numeroHectareas}"

    class Meta:
        verbose_name = 'Factores de Utilización'
        verbose_name_plural = 'Factores de Utilización'


class CaptacionMensualAgua(models.Model):
    MES_CHOICES = [
        (1, 'Enero'),
        (2, 'Febrero'),
        (3, 'Marzo'),
        (4, 'Abril'),
        (5, 'Mayo'),
        (6, 'Junio'),
        (7, 'Julio'),
        (8, 'Agosto'),
        (9, 'Septiembre'),
        (10, 'Octubre'),
        (11, 'Noviembre'),
        (12, 'Diciembre'),
    ]

    periodoUso = models.CharField(max_length=255)
    tiempoUso = models.PositiveIntegerField()
    caudalUtilizado = models.PositiveIntegerField()
    volumenAguaCaptada = models.PositiveIntegerField()
    mes = models.PositiveIntegerField(choices=MES_CHOICES)

    def __str__(self):
        return f"T455_{self.periodoUso} - {self.mes}"

    class Meta:
        verbose_name = 'Captación Mensual de Agua'
        verbose_name_plural = 'Captaciones Mensuales de Agua'


class T0444Formulario(models.Model):
    TIPO_USUARIO_CHOICES = [
        ('EMPRESARIAL', 'Empresarial'),
        ('DOMESTICO', 'Doméstico'),
        ('MUNICIPAL', 'Municipal'),
        ('COMERCIAL', 'Comercial'),
        ('ESP', 'E.S.P'),
        ('OTRO', 'Otro'),
    ]

    tipoUsuario = models.CharField(max_length=15, choices=TIPO_USUARIO_CHOICES)
    otrotipo = models.CharField(max_length=255, blank=True, null=True)
    razonSocial = models.CharField(max_length=255)
    nit = models.PositiveIntegerField()
    nombreRepresentanteLegal = models.CharField(max_length=255)
    cc = models.PositiveIntegerField()
    actividadEconomica = models.CharField(max_length=255)
    telefono = models.CharField(max_length=15)
    fax = models.CharField(max_length=15)
    codigoCIIU = models.PositiveIntegerField()
    direccion = models.TextField()
    municipio = models.CharField(max_length=255)
    expediente = models.PositiveIntegerField()
    numConcesion = models.PositiveIntegerField()
    fechaCreacion = models.DateTimeField(auto_now_add=True)
    informacionFuentesAbastecimiento = models.ManyToManyField(InformacionFuente)
    coordenadasSitioCaptacion = models.OneToOneField(CoordenadasSitioCaptacion, on_delete=models.CASCADE)
    factoresUtilizacion = models.OneToOneField(FactoresUtilizacion, on_delete=models.CASCADE)
    captacionesMensualesAgua = models.ManyToManyField(CaptacionMensualAgua)

    def __str__(self):
        return f"T456_{self.id} - {self.razonSocial}"

    class Meta:
        verbose_name = 'T457ormulario '
        verbose_name_plural = 'T467Formularios '