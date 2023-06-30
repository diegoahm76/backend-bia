from django.db import models


class Deposito(models.Model):
    id_deposito = models.AutoField(primary_key=True, db_column='T230IdDeposito')
    nombre_deposito = models.CharField(max_length=100, db_column='T230nombreDeposito')
    identificacion_por_entidad = models.CharField(max_length=10, db_column='T230identificacionPorEntidad')
    orden_ubicacion_por_entidad = models.SmallIntegerField(db_column='T230ordenUbicacionPorEntidad')
    direccion_deposito = models.CharField(max_length=255, db_column='T230direccionDeposito')
    cod_municipio_nal = models.ForeignKey('Municipio', on_delete=models.CASCADE, db_column='T230Cod_MunicipioNal')
    cod_pais_exterior = models.ForeignKey('Paises', on_delete=models.CASCADE, db_column='T230Cod_PaisExterior')
    id_sucursal_entidad = models.ForeignKey('SucursalEntidad', on_delete=models.CASCADE, db_column='T230Id_SucursalEntidad')
    activo = models.BooleanField(db_column='T230activo')

    def __str__(self):
        return str(self.nombre_deposito)

    class Meta:
        db_table = 'T230Depositos'
        verbose_name = 'Depósito'
        verbose_name_plural = 'Depósitos'


class EstanteDeposito(models.Model):
    id_estante_deposito = models.AutoField(primary_key=True, db_column='T231IdEstante_Deposito')
    id_deposito = models.ForeignKey('Deposito', on_delete=models.CASCADE, db_column='T231Id_Deposito')
    identificacion_por_deposito = models.CharField(max_length=10, db_column='T231identificacionPorDeposito')
    orden_ubicacion_por_deposito = models.SmallIntegerField(db_column='T231ordenUbicacionPorDeposito')

    def __str__(self):
        return str(self.identificacion_por_deposito)

    class Meta:
        db_table = 'T231Estantes_Deposito'
        verbose_name = 'Estante en Depósito'
        verbose_name_plural = 'Estantes en Depósito'
      