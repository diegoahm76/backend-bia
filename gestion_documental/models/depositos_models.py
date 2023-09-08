from django.db import models
from transversal.models.base_models import (
    Municipio
)
from transversal.models.base_models import Paises
from transversal.models.entidades_models import SucursalesEmpresas

#DEPOSITOS
class Deposito(models.Model):
    id_deposito = models.AutoField(primary_key=True, db_column='T230IdDeposito')
    nombre_deposito = models.CharField(max_length=100, db_column='T230nombreDeposito')
    identificacion_por_entidad = models.CharField(max_length=10, db_column='T230identificacionPorEntidad')
    orden_ubicacion_por_entidad = models.SmallIntegerField(db_column='T230ordenUbicacionPorEntidad')
    direccion_deposito = models.CharField(max_length=255, db_column='T230direccionDeposito')
    cod_municipio_nal = models.ForeignKey(Municipio, on_delete=models.SET_NULL, db_column='T230Cod_MunicipioNal',null=True)
    cod_pais_exterior = models.ForeignKey(Paises, on_delete=models.SET_NULL, db_column='T230Cod_PaisExterior',null=True)
    id_sucursal_entidad = models.ForeignKey(SucursalesEmpresas, on_delete=models.CASCADE, db_column='T230Id_SucursalEntidad')
    activo = models.BooleanField(db_column='T230activo')

    def __str__(self):
        return str(self.nombre_deposito)

    class Meta:
        db_table = 'T230Depositos'
        verbose_name = 'Depósito'
        verbose_name_plural = 'Depósitos'
        unique_together = [('identificacion_por_entidad'),( 'orden_ubicacion_por_entidad')]


#ESTANTES
class EstanteDeposito(models.Model):
    id_estante_deposito = models.AutoField(primary_key=True, db_column='T231IdEstante_Deposito')
    id_deposito = models.ForeignKey(Deposito, on_delete=models.CASCADE, db_column='T231Id_Deposito')
    identificacion_por_deposito = models.CharField(max_length=10, db_column='T231identificacionPorDeposito')
    orden_ubicacion_por_deposito = models.SmallIntegerField(db_column='T231ordenUbicacionPorDeposito')

    def __str__(self):
        return str(self.identificacion_por_deposito)

    class Meta:
        db_table = 'T231Estantes_Deposito'
        verbose_name = 'Estante en Depósito'
        verbose_name_plural = 'Estantes en Depósito'
        unique_together = [('id_deposito', 'identificacion_por_deposito'),('id_deposito', 'orden_ubicacion_por_deposito')]

#BANDEJAS
class BandejaEstante(models.Model):
    id_bandeja_estante = models.AutoField(primary_key=True, null=False, db_column='T232IdBandeja_Estante')
    id_estante_deposito = models.ForeignKey(EstanteDeposito, on_delete=models.CASCADE, db_column='T232Id_Estante_Deposito')
    identificacion_por_estante = models.CharField(max_length=10, db_column='T232identificacionPorEstante')
    orden_ubicacion_por_estante = models.SmallIntegerField(db_column='T232ordenUbicacionPorEstante')

    def __str__(self):
        return str(self.orden_ubicacion_por_estante)

    class Meta:
        db_table = 'T232Bandejas_Estante'
        verbose_name = 'Bandeja en Estante'
        verbose_name_plural = 'Bandejas en Estante'
        unique_together = [('id_estante_deposito','identificacion_por_estante'),('id_estante_deposito','orden_ubicacion_por_estante')]

#CAJAS
class CajaBandeja(models.Model):
    id_caja_bandeja= models.AutoField(primary_key=True, null=False, db_column='T233IdCaja_Bandeja')
    id_bandeja_estante =models.ForeignKey(BandejaEstante, on_delete=models.CASCADE, db_column='T233Id_Bandeja_Estante')
    identificacion_por_bandeja=models.CharField(max_length=10, db_column='T233identificacionPorBandeja')
    orden_ubicacion_por_bandeja  = models.SmallIntegerField(db_column='T233ordenUbicacionPorBandeja', )
    
    class Meta:
        db_table = 'T233Cajas_Bandeja'
        verbose_name = 'Caja en Bandeja'
        verbose_name_plural = 'Cajas en Bandeja'
        unique_together = [('id_bandeja_estante','identificacion_por_bandeja'),('id_bandeja_estante','orden_ubicacion_por_bandeja')]

#CARPETAS
class CarpetaCaja(models.Model):
    id_carpeta_caja = models.AutoField(primary_key=True, db_column='T234IdCarpeta_Caja')
    id_caja_bandeja = models.ForeignKey(CajaBandeja, on_delete=models.CASCADE, db_column='T234Id_Caja_Bandeja')
    identificacion_por_caja = models.CharField(max_length=10, db_column='T234identificacionPorCaja')
    orden_ubicacion_por_caja = models.SmallIntegerField(db_column='T234ordenUbicacionPorCaja')
    id_expediente = models.SmallIntegerField(null=True, blank=True, db_column='T234Id_Expediente')
    id_prestamo_expediente = models.SmallIntegerField(null=True, blank=True, db_column='T234Id_PrestamoExpediente')

    # T234Id_PrestamoExpediente & T234Id_Expediente cambiar en modelo cuando se genere el tabla de expediente (kc)
    class Meta:
        db_table = 'T234Carpetas_Caja'
        verbose_name = 'Carpeta en Caja'
        verbose_name_plural = 'Carpetas en Caja'
        unique_together = [('id_caja_bandeja','identificacion_por_caja'),('id_caja_bandeja','orden_ubicacion_por_caja')]
