from recaudo.models.facilidades_pagos_models import FacilidadesPago
from recaudo.serializers.planes_pagos_serializers import TipoPagoSerializer
from recaudo.models.base_models import TipoActuacion, TiposPago
from recaudo.models.cobros_models import Cartera
from recaudo.models.liquidaciones_models import Deudores, Expedientes
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Value as V
from django.db.models.functions import Concat
from seguridad.models import Personas, ClasesTerceroPersona, User
from rest_framework import generics, status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

