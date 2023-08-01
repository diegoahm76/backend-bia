from rest_framework import serializers
from seguridad.models import Personas
from recaudo.models.base_models import TipoActuacion, TiposPago, Ubicaciones
from recaudo.models.facilidades_pagos_models import (
    FacilidadesPago,
    RequisitosActuacion,
    CumplimientoRequisitos,
    DetallesFacilidadPago,
    RespuestaSolicitud
)
from recaudo.models.cobros_models import Cartera, Deudores
from seguridad.models import Personas, Municipio


