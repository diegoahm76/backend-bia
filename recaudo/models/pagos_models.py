from django.db import models
from gestion_documental.models.expedientes_models import ArchivosDigitales
from recaudo.models.liquidaciones_models import LiquidacionesBase
from transversal.models.personas_models import Personas
from recaudo.choices.pagos_estados_choices import pagos_estados_CHOICES

class Pagos(models.Model):
    id_pago = models.AutoField(primary_key=True, editable=False, db_column='T468IdPago')
    id_liquidacion = models.ForeignKey(LiquidacionesBase, on_delete=models.CASCADE, db_column='T468Id_Liquidacion')
    fecha_inicio_pago = models.DateTimeField(auto_now_add=True, db_column='T468FechaInicioPago')
    fecha_pago = models.DateTimeField(blank=True, null=True, db_column='T468FechaPago')
    estado_pago = models.CharField(max_length=4, choices=pagos_estados_CHOICES, db_column='T468EstadoPago')
    notificacion = models.BooleanField(default=False, db_column='T468Notificacion')
    id_persona_pago = models.ForeignKey(Personas, on_delete=models.CASCADE, db_column='T468Id_PersonaPaga')
    comprobante_pago = models.ForeignKey(ArchivosDigitales, on_delete=models.SET_NULL, blank=True, null=True, db_column='T468ComprobantePago')

    def __str__(self):
        return str(self.id_pago)
    
    class Meta:
        db_table='T468Pagos'
        verbose_name='Pago'
        verbose_name_plural='Pagos'