from recaudo.models.pagos_models import (
    FacilidadesPago,
    RequisitosActuacion,
    CumplimientoRequisitos,
    DetallesFacilidadPago,
    GarantiasFacilidad,
    PlanPagos,
    TasasInteres
)

from recaudo.models.liquidaciones_models import Deudores
from seguridad.models import Personas, ClasesTerceroPersona

from recaudo.serializers.pagos_serializers import (
    FacilidadesPagoSerializer,
    FacilidadesPagoPutSerializer,
    DeudorFacilidadPagoSerializer,
    TipoActuacionSerializer,
    FuncionariosSerializer
)
from recaudo.models.base_models import TipoActuacion, TiposPago
from rest_framework import generics, status
from rest_framework.response import Response

from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

class DatosDeudorView(generics.ListAPIView):
    queryset = Deudores.objects.all()
    serializer_class = DeudorFacilidadPagoSerializer

    def get(self, request, id):
        queryset = Deudores.objects.filter(id=id).first()
        if not queryset:
            return Response({'success': False, 'detail': 'No se encontró ningun registro con el parámetro ingresado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(queryset)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)   


class TipoActuacionView(generics.ListAPIView):
    queryset = TipoActuacion.objects.all()
    serializer_class = TipoActuacionSerializer

    def get(self, request, id):
        queryset = TipoActuacion.objects.filter(id=id).first()
        serializer = self.serializer_class(queryset)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)
    

class CrearFacilidadPagoView(generics.CreateAPIView):
    serializer_class = FacilidadesPagoSerializer
    queryset = FacilidadesPago.objects.all()
    
    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        periodicidad = serializer.validated_data.get('periodicidad')
        cuotas = serializer.validated_data.get('cuotas')
        total_plazos = periodicidad * cuotas
        if total_plazos > 61:
            return Response({'success': False, 'detail':'Las cuotas deben ser menor de 60 meses'})
        else:
            serializer.save()
            return Response({'success': True, 'data':serializer.data})


class FacilidadPagoUpdateView(generics.UpdateAPIView):
    serializer_class = FacilidadesPagoPutSerializer
    queryset = FacilidadesPago.objects.all()
    
    def put(self, request, id):
        data = request.data
        facilidad_de_pago = FacilidadesPago.objects.filter(id=id).first()
        if facilidad_de_pago:
            serializer = self.serializer_class(facilidad_de_pago, data=data, many=False)
            serializer.is_valid(raise_exception=True)
            
            id_funcionario = serializer.validated_data.get('id_funcionario')

            if not id_funcionario:
                return Response({'success': False, 'detail':'Falta asignar funcionario'})
            else:
                serializer.save(update_fields=['id_funcionario'])
                return Response({'success': True, 'data':serializer.data})
        else:
            return Response({'success': False, 'detail':'La facilidad de pago ingresada no existe'})
    

class FuncionariosView(generics.ListAPIView):
    serializer_class = FuncionariosSerializer
    queryset = Personas.objects.all()

    def get(self, request):
        funcionarios = ClasesTerceroPersona.objects.filter(id_clase_tercero=2)
        funcionarios = [funcionario.id_persona for funcionario in funcionarios]
        serializer = self.serializer_class(funcionarios, many=True)
        return Response({'success': True, 'data':serializer.data})
    
        
