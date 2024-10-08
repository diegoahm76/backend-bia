from django.db import models

# from gestion_documental.models.expedientes_models import ArchivosDigitales

class documento_formulario_recuado(models.Model):
    id_documento = models.AutoField(primary_key=True,db_column='T459IdDocumentoFormularioRecaudo')
    id_persona = models.ForeignKey('transversal.Personas', on_delete=models.CASCADE,db_column='TXXXId_Persona')	
    radicado = models.CharField(max_length=225, db_column='T459Radicado')
    id_archivo_sistema	= models.ForeignKey('gestion_documental.ArchivosDigitales', on_delete=models.CASCADE, db_column='T459Id_ArchivoEnSistema')
    ids_destinatarios_personas = models.CharField(max_length=225, db_column='T459Ids_Destinatarios_Personas')
    ids_destinatarios_unidades = models.CharField(max_length=225, db_column='T459Ids_Destinatarios_Unidades')



    class Meta:
        db_table = 'T460DocumentoFormularioRecuado'
        verbose_name = 'Documento de Formulario de Recuado'
        verbose_name_plural = 'Documentos de Formularios de Recuado'
        #unique_together = ('codigo_exp_und_serie_subserie', 'codigo_exp_Agno', 'codigo_exp_consec_por_agno')



class InformacionFuente(models.Model):
    numero = models.TextField(blank=True, null=True, db_column='T464_numero')
    tipo = models.TextField(max_length=255, blank=True, null=True, db_column='T464_tipo')
    nombreFuente = models.TextField(max_length=255, blank=True, null=True, db_column='T464_nombreFuente')
    caudalConcesionado = models.TextField(max_length=255, blank=True, null=True, db_column='T464_caudalConcesionado')
    sistemaMedicionAguaCaptada = models.TextField(max_length=255, blank=True, null=True, db_column='T464_sistemaMedicionAguaCaptada')
    cordenadaX = models.FloatField(blank=True, null=True, db_column='T464_cordenadaX')
    cordenadaY = models.FloatField(blank=True, null=True, db_column='T464_cordenadaY')

    def __str__(self):
        return f"aT452_{self.numero} - {self.nombreFuente}"

    class Meta:
        db_table = 'T464TInformacionFuente'
        verbose_name = 'Información de Fuente'
        verbose_name_plural = 'Información de Fuentes'

# class CoordenadasSitioCaptacion(models.Model):
#     cordenadaX = models.FloatField()
#     cordenadaY = models.FloatField()

#     def __str__(self):
#         return f"T453_{self.cordenadaX}, {self.cordenadaY}"

#     class Meta:
#         verbose_name = 'Coordenadas de Sitio de Captación'
#         verbose_name_plural = 'Coordenadas de Sitios de Captación'


class FactoresUtilizacion(models.Model):
    numeroUsuarios = models.TextField(blank=True, null=True, db_column='T463_numeroUsuarios')
    numeroBovinos = models.TextField(blank=True, null=True, db_column='T463_numeroBovinos')
    numeroPorcinos = models.TextField(blank=True, null=True, db_column='T463_numeroPorcinos')
    numeroHectareas = models.TextField(blank=True, null=True, db_column='T463_numeroHectareas')
    consumoNumeroUsuarios = models.TextField(blank=True, null=True, db_column='T463_consumoNumeroUsuarios')
    consumoNumeroBovinos = models.TextField(blank=True, null=True, db_column='T463_consumoNumeroBovinos')
    consumoNumeroPorcinos = models.TextField(blank=True, null=True, db_column='T463_consumoNumeroPorcinos')
    consumoNumeroHectareas = models.TextField(blank=True, null=True, db_column='T463_consumoNumeroHectareas')

    def __str__(self):
        return f"T454_{self.numeroUsuarios} - {self.numeroBovinos} - {self.numeroPorcinos} - {self.numeroHectareas}"

    class Meta:
        db_table = 'T463FactoresUtilización'
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

    periodoUso = models.TextField(blank=True, null=True, db_column='T462_periodoUso')
    tiempoUso = models.TextField(blank=True, null=True, db_column='T462_tiempoUso')
    caudalUtilizado = models.TextField(blank=True, null=True, db_column='T462_caudalUtilizado')
    volumenAguaCaptada = models.TextField(blank=True, null=True, db_column='T462_volumenAguaCaptada')
    mes = models.TextField(choices=MES_CHOICES, blank=True, null=True, db_column='T462_mes')

    def __str__(self):
        return f"T455_{self.periodoUso} - {self.mes}"

    class Meta:
        db_table = 'T462TCaptacionMensualAgua'
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

    tipoUsuario = models.TextField(max_length=15, choices=TIPO_USUARIO_CHOICES, blank=True, null=True, db_column='T461_tipoUsuario')
    otrotipo = models.TextField(max_length=255, blank=True, null=True, db_column='T461_otrotipo')
    idpersona = models.TextField(max_length=255, blank=True, null=True, db_column='T461_idpersona')
    razonSocial = models.TextField(max_length=255, blank=True, null=True, db_column='T461_razonSocial')
    nit = models.TextField(blank=True, null=True, db_column='T461_nit')
    nombreRepresentanteLegal = models.TextField(max_length=255, blank=True, null=True, db_column='T461_nombreRepresentanteLegal')
    cc = models.TextField(blank=True, null=True, db_column='T461_cc')
    actividadEconomica = models.TextField(max_length=255, blank=True, null=True, db_column='T461_actividadEconomica')
    telefono = models.TextField(max_length=15, blank=True, null=True, db_column='T461_telefono')
    fax = models.TextField(max_length=15, blank=True, null=True, db_column='T461_fax')
    codigoCIIU = models.TextField(blank=True, null=True, db_column='T461_codigoCIIU')
    direccion = models.TextField(blank=True, null=True, db_column='T461_direccion')
    municipio = models.TextField(max_length=255, blank=True, null=True, db_column='T461_municipio')
    expediente = models.TextField(blank=True, null=True, db_column='T461_expediente')
    numConcesion = models.TextField(blank=True, null=True, db_column='T461_numConcesion')
    fechaCreacion = models.DateTimeField(auto_now_add=True, blank=True, null=True, db_column='T461_fechaCreacion')
    informacionFuentesAbastecimiento = models.ManyToManyField(InformacionFuente, db_column='T461_informacionFuentesAbastecimiento')
    factoresUtilizacion = models.OneToOneField(FactoresUtilizacion, on_delete=models.CASCADE, db_column='T461_factoresUtilizacion')
    captacionesMensualesAgua = models.ManyToManyField(CaptacionMensualAgua, db_column='T461_captacionesMensualesAgua')
    aprobado = models.BooleanField(default=False, db_column='T461_aprobado')
    id_archivo_sistema	= models.ForeignKey('gestion_documental.ArchivosDigitales', on_delete=models.CASCADE, blank=True, null=True, db_column='T461_id_archivo_sistema')


    def __str__(self):
        return f"T456_{self.id} - {self.razonSocial}"

    class Meta:
        db_table = 'T461TFormulario'
        verbose_name = 'T457ormulario '
        verbose_name_plural = 'T467Formularios '


class T459TablaTercerosss(models.Model):



    T459nroDocumentoID = models.TextField(primary_key=True,db_column='T459nroDocumentoID')
    Fecha = models.DateTimeField(db_column='Fecha')
    T459Cod_TipoDocumentoID = models.TextField(db_column='T459Cod_TipoDocumentoID')
    T459Cod_MunicipioExpID = models.TextField(db_column='T459Cod_MunicipioExpID',null=True)
    T459digitoVerificacion = models.TextField(db_column='T459digitoVerificacion',null=True)
    T459tipoPersona = models.TextField(db_column='T459tipoPersona',null=True)
    T459codNaturalezaEmpresa = models.TextField(db_column='T459codNaturalezaEmpresa',null=True)
    T459primerNombre = models.TextField(db_column='T459primerNombre',null=True)
    T459segundoNombre = models.TextField(db_column='T459segundoNombre',null=True)
    T459primerApellido = models.TextField(db_column='T459primerApellido',null=True)
    T459segundoApellido = models.TextField(db_column='T459segundoApellido',null=True)
    T459razonSocial = models.TextField(db_column='T459razonSocial',null=True)
    T459nombreComercial = models.TextField(db_column='T459nombreComercial',null=True)
    T459dirResidencia = models.TextField(db_column='T459dirResidencia',null=True)
    T459dirResidenciaReferencia = models.TextField(db_column='T459dirResidenciaReferencia',null=True)
    T459dirResidenciaGeoref = models.TextField(db_column='T459dirResidenciaGeoref',null=True)
    T459Cod_MunicipioResidenciaNal = models.TextField(db_column='T459Cod_MunicipioResidenciaNal',null=True)
    T459Cod_PaisResidenciaExterior = models.TextField(db_column='T459Cod_PaisResidenciaExterior',null=True)
    T459dirLaboralNal = models.TextField(db_column='T459dirLaboralNal',null=True)
    T459Cod_MunicipioLaboralNal = models.TextField(db_column='T459Cod_MunicipioLaboralNal',null=True)
    T459dirNotificacionNal = models.TextField(db_column='T459dirNotificacionNal',null=True)
    T459dirNotificacionNalReferencia = models.TextField(db_column='T459dirNotificacionNalReferencia',null=True)
    T459Cod_MunicipioNotificacionNal = models.TextField(db_column='T459Cod_MunicipioNotificacionNal',null=True)
    T459emailNotificacion = models.TextField(db_column='T459emailNotificacion',null=True)
    T459emailEmpresarial = models.TextField(db_column='T459emailEmpresarial',null=True)
    T459telFijoResidencial = models.TextField(db_column='T459telFijoResidencial',null=True)
    T459telEmpresa = models.TextField(db_column='T459telEmpresa',null=True)
    T459telCelularEmpresa = models.TextField(db_column='T459telCelularEmpresa',null=True)
    T459telEmpresa2 = models.TextField(db_column='T459telEmpresa2',null=True)
    T459Cod_PaisNacionalidadDeEmpresa = models.TextField(db_column='T459Cod_PaisNacionalidadDeEmpresa',null=True)
    T459Id_PersonaRepLegal = models.TextField(db_column='T010Id_PersonaRepLegal',null=True)
    T459fechaNacimiento = models.DateTimeField(db_column='T459fechaNacimiento',null=True)

    class Meta:
        db_table = 'T459TablaTerceros'
        verbose_name = 'TablaTerceros'
        verbose_name_plural = 'TablaTerceros'


class T458PrincipalLiquidacion(models.Model):
    T458fecha = models.DateTimeField(db_column='T458fecha')
    T458t908codcia = models.FloatField(db_column='T458t908codcia', null=True)
    T458tiporenta = models.TextField(db_column='T458tiporenta', null=True)
    T458cuentacontable = models.TextField(db_column='T458cuentacontable', null=True)
    T458nombredeudor = models.TextField(db_column='T458nombredeudor', null=True)
    T458fechafact = models.DateTimeField(db_column='T458fechafact', null=True)
    T458fechanotificacion = models.DateTimeField(db_column='T458fechanotificacion', null=True)
    T458fechaenfirme = models.DateTimeField(db_column='T458fechaenfirme', null=True)
    T458cortedesde = models.TextField(db_column='T458cortedesde', null=True)
    T458cortehasta = models.TextField(db_column='T458cortehasta', null=True)
    T458numfactura = models.TextField(db_column='T458numfactura', null=True)
    T458numliquidacion = models.FloatField(db_column='T458numliquidacion', null=True)
    T458periodo = models.TextField(db_column='T458periodo', null=True)
    T458año = models.FloatField(db_column='T458año', null=True)
    T458expediente = models.TextField(db_column='T458expediente', null=True)
    T458numresolucion = models.TextField(db_column='T458numresolucion', null=True)
    T458recurso = models.TextField(db_column='T458recurso', null=True)
    T458docauto = models.TextField(db_column='T458docauto', null=True)
    T458saldocapital = models.FloatField(db_column='T458saldocapital', null=True)
    T458saldointeres = models.FloatField(db_column='T458saldointeres', null=True)
    T458diasmora = models.FloatField(db_column='T458diasmora', null=True)
    T458nit = models.TextField(db_column='T458nit', null=True)


    class Meta:
        db_table = 'T458Principal'
        verbose_name = 'Principal'
        verbose_name_plural = 'Principal'

class CarteraPrincipal(models.Model):
    T457id_cartera = models.AutoField(primary_key=True, db_column='T457IdCarteraPrincipal')
    T457fecha = models.DateField(db_column='T457Fecha')
    T457t908_cod_cia = models.CharField(max_length=255, db_column='T457T908CodCia')
    T457tipo_renta = models.CharField(max_length=255, db_column='T457TipoRenta')
    T457cuenta_contable = models.CharField(max_length=255, db_column='T457CuentaContable')
    T457nit = models.CharField(max_length=255, db_column='T457Nit')
    T457nombre_deudor = models.CharField(max_length=255, db_column='T457NombreDeudor')
    T457fecha_fact = models.DateField(db_column='T457FechaFact')
    T457fecha_notificacion = models.DateField(db_column='T457FechaNotificacion')
    T457fecha_en_firme = models.DateField(db_column='T457FechaEnFirme')
    T457corte_desde = models.DateField(db_column='T457CorteDesde')
    T457corte_hasta = models.DateField(db_column='T457CorteHasta')
    T457num_factura = models.CharField(max_length=255, db_column='T457NumFactura')
    T457num_liquidacion = models.CharField(max_length=255, db_column='T457NumLiquidacion')
    T457periodo = models.CharField(max_length=255, db_column='T457Periodo')
    T457agno = models.PositiveIntegerField(db_column='T457Agno')
    T457expediente = models.CharField(max_length=255, db_column='T457Expediente')
    T457num_resolucion = models.CharField(max_length=255, db_column='T457NumResolucion')
    T457recurso = models.CharField(max_length=255, db_column='T457Recurso')
    T457doc_auto = models.CharField(max_length=255, db_column='T457DocAuto')
    T457saldo_capital = models.DecimalField(max_digits=10, decimal_places=2, db_column='T457SaldoCapital')
    T457saldo_interes = models.DecimalField(max_digits=10, decimal_places=2, db_column='T457SaldoInteres')
    T457dias_mora = models.PositiveIntegerField(db_column='T457DiasMora')

    class Meta:
        db_table = 'T457CarteraPrincipal'
        verbose_name = 'Cartera Principal'
        verbose_name_plural = 'Carteras Principales'


