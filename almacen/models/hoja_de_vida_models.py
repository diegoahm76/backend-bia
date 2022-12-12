from django.db import models
from almacen.choices.tipo_documento_choices import tipo_documento_CHOICES
from almacen.choices.tipo_vehiculo_choices import tipo_vehiculo_CHOICES
from almacen.choices.tipo_combustible_choices import tipo_combustible_CHOICES
# from seguridad.models import Personas
from almacen.models.bienes_models import CatalogoBienes

class VehiculosArrendados(models.Model):
    pass

class HojaDeVidaComputadores(models.Model):
    id_hoja_de_vida = models.AutoField(primary_key=True, db_column='T065IdHojaDeVida')
    id_articulo = models.ForeignKey(CatalogoBienes, on_delete=models.CASCADE, db_column='T065Id_Articulo')
    sistema_operativo = models.CharField(max_length=40, db_column='T065sistemaOperativo', blank=True, null=True)
    suite_ofimatica = models.CharField(max_length=40, db_column='T065suiteOfimatica', blank=True, null=True)
    antivirus = models.CharField(max_length=40, db_column='T065antivirus', blank=True, null=True)
    otras_aplicaciones = models.CharField(max_length=255, db_column='T065otrasAplicaciones', blank=True, null=True)
    color = models.CharField(max_length=20, db_column='T065color', blank=True, null=True)
    tipo_de_equipo = models.CharField(max_length=20, db_column='T065tipoDeEquipo', blank=True, null=True)
    tipo_almacenamiento = models.CharField(max_length=30, db_column='T065tipoAlmacenamiento', blank=True, null=True)
    capacidad_almacenamiento = models.CharField(max_length=20, db_column='T065capacidadAlmacenamiento', blank=True, null=True)
    procesador = models.CharField(max_length=20, db_column='T065procesador', blank=True, null=True)
    memoria_ram = models.SmallIntegerField(db_column='T065memoriaRAM', blank=True, null=True)
    observaciones_adicionales = models.CharField(max_length=255, db_column='T065observacionesAdicionales', blank=True, null=True)
    otras_aplicaciones = models.CharField(max_length=255, db_column='T065otrasAplicaciones', blank=True, null=True)
    ruta_imagen_foto = models.ImageField(db_column='T065rutaImagenFoto', blank=True, null=True)
    
    def __str__(self):
        return str(self.id_hoja_de_vida)

    class Meta:
        db_table = 'T065HojaDeVidaComputadores'
        verbose_name = 'Hoja de vida computadores'
        verbose_name_plural = 'Hojas de vida computadores'
    
class HojaDeVidaVehiculos(models.Model):
    id_hoja_de_vida = models.AutoField(primary_key=True, db_column='T066IdHojaDeVida')
    id_articulo = models.ForeignKey(CatalogoBienes, on_delete=models.SET_NULL, db_column='T066Id_Articulo', blank=True, null=True)
    id_vehiculo_arrendado = models.ForeignKey(VehiculosArrendados, on_delete=models.SET_NULL, db_column='T066Id_VehiculoArrendado', blank=True, null=True)
    cod_tipo_vehiculo = models.CharField(max_length=1, choices=tipo_vehiculo_CHOICES, db_column='T066codTipoVehiculo', blank=True, null=True)
    tiene_platon = models.BooleanField(db_column='T066tienePlaton', blank=True, null=True)
    capacidad_pasajeros = models.SmallIntegerField(db_column='T066capacidadPasajeros', blank=True, null=True)
    color = models.CharField(max_length=20, db_column='T066color', blank=True, null=True)
    linea = models.CharField(max_length=20, db_column='T066linea', blank=True, null=True)
    tipo_combustible = models.CharField(max_length=3, choices=tipo_combustible_CHOICES, db_column='T066tipoCombustible', blank=True, null=True)
    es_arrendado = models.BooleanField(db_column='T066esArrendado', blank=True, null=True)
    ultimo_kilometraje = models.IntegerField(db_column='T066ultimoKilometraje', blank=True, null=True)
    fecha_ultimo_kilometraje = models.DateField(db_column='T066fechaUltimoKilometraje', blank=True, null=True)
    fecha_adquisicion = models.DateField(db_column='T066fechaAdquisicion', blank=True, null=True)
    fecha_vigencia_garantia = models.DateField(db_column='T066fechaVigenciaGarantia', blank=True, null=True)
    numero_motor = models.CharField(max_length=40, db_column='T066numeroMotor', blank=True, null=True)
    numero_chasis = models.CharField(max_length=40, db_column='T066numeroChasis', blank=True, null=True)
    cilindraje = models.SmallIntegerField(db_column='T066cilindraje', blank=True, null=True)
    transmision = models.CharField(max_length=20, db_column='T066transmision', blank=True, null=True)
    dimesion_llantas = models.SmallIntegerField(db_column='T066dimensionLlantas', blank=True, null=True)
    id_proveedor = models.ForeignKey('seguridad.Personas', on_delete=models.SET_NULL, db_column='T066Id_Proveedor', blank=True, null=True)
    capacidad_extintor = models.SmallIntegerField(db_column='T066capacidadExtintor', blank=True, null=True)
    tarjeta_operacion = models.CharField(max_length=20, db_column='T066tarjetaOperacion', blank=True, null=True)
    observaciones_adicionales = models.CharField(max_length=255, db_column='T066observacionesAdicionales', blank=True, null=True)
    es_agendable = models.BooleanField(db_column='T066esAgendable', blank=True, null=True)
    en_circulacion = models.BooleanField(db_column='T066enCirculacion', blank=True, null=True)
    fecha_circulacion = models.DateField(db_column='T066fechaCirculacion', blank=True, null=True)
    ruta_imagen_foto = models.ImageField(db_column='T066rutaImagenFoto', blank=True, null=True)
    
    def __str__(self):
        return str(self.id_hoja_de_vida)

    class Meta:
        db_table = 'T066HojaDeVidaVehiculos'
        verbose_name = 'Hoja de vida vehiculos'
        verbose_name_plural = 'Hojas de vida vehiculos'

class HojaDeVidaOtrosActivos(models.Model):
    id_hoja_de_vida = models.AutoField(primary_key=True, db_column='T067IdHojaDeVida')
    id_articulo = models.ForeignKey(CatalogoBienes, on_delete=models.CASCADE, db_column='T067Id_Articulo')
    caracteristicas_fisicas = models.TextField(db_column='T067caracteristicasFisicas', blank=True, null=True)
    especificaciones_tecnicas = models.TextField(db_column='T067especificacionesTecnicas', blank=True, null=True)
    observaciones_adicionales = models.CharField(max_length=255, db_column='T067observacionesAdicionales', blank=True, null=True)
    ruta_imagen_foto = models.ImageField(db_column='T067rutaImagenFoto', blank=True, null=True)
    
    def __str__(self):
        return str(self.id_hoja_de_vida)

    class Meta: 
        db_table = 'T065HojaDeVidaOtrosActivos'
        verbose_name = 'Hoja de vida otros activos'
        verbose_name_plural = 'Hojas de vida otros activos'

class DocumentosVehiculo(models.Model):
    id_documentos_vehiculos = models.AutoField(primary_key=True, db_column='T068IdDocumentosVehiculos')
    id_articulo = models.ForeignKey(CatalogoBienes, on_delete=models.CASCADE, db_column='T068Id_Articulo')
    cod_tipo_documento = models.CharField(max_length=4, choices=tipo_documento_CHOICES, db_column='T068codTipoDocumento')
    nro_documento = models.CharField(max_length=20, db_column='T068nroDocumento')
    fecha_inicio_vigencia = models.DateField(db_column='T068fechaInicioVigencia')
    fecha_expiracion = models.DateField(db_column='T068fechaExpiracion')
    id_empresa_proveedora = models.ForeignKey('seguridad.Personas', on_delete=models.SET_NULL, null=True, blank=True, db_column='T068Id_EmpresaProveedora')
    
    def __str__(self):
        return str(self.id_hoja_de_vida)

    class Meta:
        db_table = 'T068DocumentosVehiculo'
        verbose_name = 'Documento Vehiculo'
        verbose_name_plural = 'Documentos Vehiculo'
        unique_together = ['id_articulo', 'cod_tipo_documento', 'nro_documento']