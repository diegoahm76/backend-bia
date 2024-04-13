from django.db import models
from recaudo.models.liquidaciones_models import LiquidacionesBase
from transversal.models.personas_models import Personas
from recaudo.choices.pagos_estados_choices import pagos_estados_CHOICES

class Pagos(models.Model):
    id_pago = models.AutoField(primary_key=True, editable=False, db_column='TXXXIdPago')
    id_liquidacion = models.ForeignKey(LiquidacionesBase, on_delete=models.CASCADE, db_column='TXXXId_Liquidacion')
    fecha_inicio_pago = models.DateTimeField(auto_now_add=True, db_column='TXXXFechaInicioPago')
    fecha_pago = models.DateTimeField(blank=True, null=True, db_column='TXXXFechaPago')
    estado_pago = models.CharField(max_length=4, choices=pagos_estados_CHOICES, db_column='TXXXEstadoPago')
    notificacion = models.BooleanField(default=False, db_column='TXXXNotificacion')
    id_persona_pago = models.ForeignKey(Personas, on_delete=models.CASCADE, db_column='TXXXId_PersonaPaga')

    def __str__(self):
        return str(self.id_pago)
    
    class Meta:
        db_table='TXXXPagos'
        verbose_name='Pago'
        verbose_name_plural='Pagos'