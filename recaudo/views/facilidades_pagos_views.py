from recaudo.models.pagos_models import (
    FacilidadesPago,
    RequisitosActuacion,
    CumplimientoRequisitos,
    DetallesFacilidadPago,
    GarantiasFacilidad,
    PlanPagos,
    TasasInteres
)

from recaudo.serializers.pagos_serializers import (
    FacilidadesPagoSerializer,
    FacilidadesPagoPutSerializer,
    DeudorFacilidadPagoSerializer,
    TipoActuacionSerializer,
    FuncionariosSerializer,    
    RequisitosActuacionSerializer,
    CumplimientoRequisitosSerializer,
    DatosContactoDeudorSerializer,
    DetallesFacilidadPagoSerializer,
    PlanPagosSerializer,
    TasasInteresSerializer,
    ObligacionesSerializer,
    ConsultaObligacionesSerializer,
    ListadoFacilidadesPagoSerializer,
    ConsultaFacilidadesPagosSerializer,
    ListadoDeudoresUltSerializer,
    AutorizacionNotificacionesSerializer,
    RespuestaSolicitudFacilidadSerializer
)

from recaudo.serializers.garantias_serializers import (
    RolesGarantiasSerializer,
    GarantiasFacilidadSerializer,
    TipoBienSerializer,
    BienSerializer,
    BienesDeudorSerializer
    )

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.db.models import Value as V
from django.db.models.functions import Concat
from seguridad.models import Personas, ClasesTerceroPersona, User
from recaudo.models.base_models import TipoActuacion, TiposPago
from recaudo.models.cobros_models import Obligaciones, Expedientes, Deudores, Cartera
from recaudo.models.liquidaciones_models import Deudores
from rest_framework import generics, status
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend


### VISTAS QUE SE MUESTRAN AL MOMENTO DE CREAR UNA FACILIDAD

class DatosContactoDeudorView(generics.ListAPIView):
    serializer_class = DatosContactoDeudorSerializer

    def get(self, request, id):
        queryset = Deudores.objects.filter(id=id).first()

        if not queryset:
            raise NotFound('No se encontró ningun registro con el parámetro ingresado')
        queryset = Personas.objects.filter(numero_documento = queryset.identificacion).first()
        serializer = self.serializer_class(queryset)
        return Response({'success': True, 'detail':'Se muestra los datos de contacto del deudor', 'data': serializer.data}, status=status.HTTP_200_OK) 


class TipoActuacionView(generics.ListAPIView):
    queryset = TipoActuacion.objects.all()
    serializer_class = TipoActuacionSerializer

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'detail':'Se muestran los tipos de actuacion de deudor', 'data': serializer.data}, status=status.HTTP_200_OK)
    

### VISTAS QUE SE CREAN AL MOMENTO DE CREAR UNA FACILIDAD

# class CrearBienView(generics.CreateAPIView):
#     serializer_class = BienSerializer
#     serializer_class_avaluos = AvaluosSerializer
    
#     def crear_bien(self, data):
#         serializer = self.serializer_class(data=data)
#         serializer.is_valid(raise_exception=True)
#         bien_creado = serializer.save()
#         return bien_creado

#     def post(self, request):
#         data_in = request.data

#         # CREAR BIEN
#         bien = self.crear_bien(data_in)

#         # CREAR AVALUO
#         fecha_avaluo = date.today()
#         fecha_fin_vigencia = fecha_avaluo + timedelta(days=bien.id_tipo_bien.vigencia_avaluo)
#         data = {
#             'id_bien' : bien.id,
#             'fecha_avaluo': fecha_avaluo,
#             'fecha_fin_vigencia': fecha_fin_vigencia,
#             'cod_funcionario_perito': 1,
#             'valor': data_in['valor']
#         }
#         serializer = self.serializer_class_avaluos(data=data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response({'success': True, 'detail':'Se crea el bien que coloca el deudor'},status=status.HTTP_200_OK)

