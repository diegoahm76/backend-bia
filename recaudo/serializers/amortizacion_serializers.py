from rest_framework import serializers
from seguridad.models import Personas
from recaudo.models.base_models import TipoActuacion, TiposPago, Ubicaciones
from recaudo.models.pagos_models import (
    FacilidadesPago,
    RequisitosActuacion,
    CumplimientoRequisitos,
    DetallesFacilidadPago,
    PlanPagos,
    TasasInteres,
    RespuestaSolicitud
)
from recaudo.models.cobros_models import Obligaciones, Cartera, Deudores
from seguridad.models import Personas, Municipio


