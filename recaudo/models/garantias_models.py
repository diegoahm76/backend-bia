from django.db import models
from recaudo.models.procesos_models import Bienes, Procesos


class RolesGarantias(models.Model):
    id = models.AutoField(primary_key=True, db_column='T414id')
    descripcion = models.CharField(max_length=255, db_column='T414descripcion')

    class Meta:
        db_table = 'T414roles_garantias'
        verbose_name = 'Roles garantia'
        verbose_name_plural = 'Roles garantias'


class Garantias(models.Model):
    id = models.AutoField(primary_key=True, db_column='T424id')
    id_proceso = models.ForeignKey(Procesos, on_delete=models.CASCADE, db_column='T424id_proceso')
    id_rol = models.ForeignKey(RolesGarantias, on_delete=models.CASCADE, db_column='T424id_rol')
    id_bien = models.ForeignKey(Bienes, on_delete=models.CASCADE, db_column='T424id_bien')
    valor = models.DecimalField(max_digits=30, decimal_places=2, db_column='T424valor')

    class Meta:
        db_table = 'T424garantias'
        verbose_name = 'Garantia'
        verbose_name_plural = 'Garantias'