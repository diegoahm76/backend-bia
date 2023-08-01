from django.db import models
from recaudo.models.procesos_models import Bienes, Procesos


class RolesGarantias(models.Model):
    id = models.AutoField(primary_key=True, db_column='T408IdRolGarantia')
    descripcion = models.CharField(max_length=255, db_column='T408descripcion')

    class Meta:
        db_table = 'T408RolesGarantia'
        verbose_name = 'Rol garantia'
        verbose_name_plural = 'Roles garantia'


class Garantias(models.Model):
    id = models.AutoField(primary_key=True, db_column='T409IdGarantia')
    id_proceso = models.ForeignKey(Procesos, on_delete=models.CASCADE, db_column='T409Id_Proceso')
    id_rol = models.ForeignKey(RolesGarantias, on_delete=models.CASCADE, db_column='T409Id_RolGarantia')
    id_bien = models.ForeignKey(Bienes, on_delete=models.CASCADE, db_column='T409Id_Bien')
    valor = models.DecimalField(max_digits=30, decimal_places=2, db_column='T409valor')

    class Meta:
        db_table = 'T409Garantias'
        verbose_name = 'Garantia'
        verbose_name_plural = 'Garantias'