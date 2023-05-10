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
    GarantiasFacilidadSerializer,
    PlanPagosSerializer,
    TasasInteresSerializer,
    ObligacionesSerializer,
    ConsultaObligacionesSerializer,
    ListadoFacilidadesPagoSerializer,
    ConsultaFacilidadesPagosSerializer,
    ListadoDeudoresUltSerializer
)

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from seguridad.models import Personas, ClasesTerceroPersona, User
from recaudo.models.base_models import TipoActuacion, TiposPago
from recaudo.models.cobros_models import Obligaciones, Expedientes, Deudores, Cartera
from recaudo.models.liquidaciones_models import Deudores
from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class DatosDeudorView(generics.ListAPIView):
    queryset = Deudores.objects.all()
    serializer_class = DeudorFacilidadPagoSerializer

    def get(self, request, id):
        queryset = Deudores.objects.filter(codigo=id).first()
        if not queryset:
            return Response({'success': False, 'detail': 'No se encontró ningun registro con el parámetro ingresado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(queryset)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)   

        
class DatosContactoDeudorView(generics.ListAPIView):
    serializer_class = DatosContactoDeudorSerializer

    def get(self, request, id):
        queryset = Deudores.objects.filter(codigo=id).first()
        if not queryset:
            return Response({'success': False, 'detail': 'No se encontró ningun registro con el parámetro ingresado'}, status=status.HTTP_404_NOT_FOUND)
        queryset = Personas.objects.filter(numero_documento = queryset.identificacion).first()
        serializer = self.serializer_class(queryset)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK) 


class TipoActuacionView(generics.ListAPIView):
    queryset = TipoActuacion.objects.all()
    serializer_class = TipoActuacionSerializer

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
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
            id_funcionario = ClasesTerceroPersona.objects.filter(id_persona=id_funcionario, id_clase_tercero=2).first()
            if id_funcionario:
                serializer.save(update_fields=['id_funcionario'])
                return Response({'success': True, 'data':serializer.data})
            else:
                return Response({'success': False, 'detail':'El funcionario ingresado no tiene permisos'})
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


class ListadoObligacionesViews(generics.ListAPIView):
    serializer_class = ObligacionesSerializer
    permission_classes = [IsAuthenticated]

    def get_monto_total(self, obligaciones):
        monto_total = 0
        intereses_total = 0
        for obligacion in obligaciones:
            monto_total += obligacion.monto_inicial
            carteras = obligacion.cartera_set.filter(fin__isnull=True)
            for cartera in carteras:
                intereses_total += cartera.valor_intereses
        return monto_total, intereses_total, monto_total + intereses_total

    
    def get(self, request):
        if request.user.is_authenticated:
            user = request.user
            numero_identificacion = user.persona.numero_documento
            try:
                deudor = Deudores.objects.get(identificacion=numero_identificacion)
            except ObjectDoesNotExist:
                return Response({'error': 'No se encontró un objeto deudor para este usuario.'}, status=status.HTTP_404_NOT_FOUND)
            nombre_completo = user.persona.primer_nombre + ' ' + user.persona.segundo_nombre + ' ' + user.persona.primer_apellido + ' ' + user.persona.segundo_apellido
            obligaciones = Obligaciones.objects.filter(id_expediente__cod_deudor=deudor)
            serializer = self.serializer_class(obligaciones, many=True)
            
            monto_total, intereses_total, monto_total_con_intereses = self.get_monto_total(obligaciones)
            data = {
                'nombre_completo': nombre_completo,
                'numero_identificacion': numero_identificacion,
                'email': user.persona.email,
                'obligaciones': serializer.data,
                'monto_total': monto_total,
                'intereses_total': intereses_total,
                'monto_total_con_intereses': monto_total_con_intereses

            }
            return Response(data)
        else:
            return Response({'error': 'Usuario no autenticado.'}, status=status.HTTP_401_UNAUTHORIZED)


class ConsultaObligacionesViews(generics.ListAPIView):
    serializer_class = ConsultaObligacionesSerializer
    
    def get_queryset(self):
        id_obligaciones = self.kwargs['id_obligaciones']
        queryset = Obligaciones.objects.filter(id=id_obligaciones)
        return queryset
    
class ConsultaObligacionesDeudoresViews(generics.ListAPIView):
    serializer_class = ObligacionesSerializer
    permission_classes = [IsAuthenticated]

    def get_monto_total(self, obligaciones):
        monto_total = 0
        intereses_total = 0
        for obligacion in obligaciones:
            monto_total += obligacion.monto_inicial
            carteras = obligacion.cartera_set.filter(fin__isnull=True)
            for cartera in carteras:
                intereses_total += cartera.valor_intereses
        return monto_total, intereses_total, monto_total + intereses_total
    
    def get_queryset(self):
        identificacion = self.kwargs['identificacion']
        deudor = Deudores.objects.get(identificacion=identificacion)
        return Obligaciones.objects.filter(id_expediente__cod_deudor=deudor)
    
    def get(self, request, identificacion):
        try:
            queryset = self.get_queryset()
            serializer = self.serializer_class(queryset, many=True)
            monto_total, intereses_total, monto_e_intereses_total = self.get_monto_total(queryset)
            return Response({
                'success': True, 
                'detail': 'Resultados de la búsqueda', 
                'data': serializer.data,
                'monto_total': monto_total,
                'intereses_total': intereses_total,
                'monto_e_intereses_total': monto_e_intereses_total
            }, status=status.HTTP_200_OK)
        except Deudores.DoesNotExist:
            raise NotFound(detail='No se encontraron resultados')



class ListadoFacilidadesPagoViews(generics.ListAPIView):
    serializer_class = ListadoFacilidadesPagoSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        filter = {}
        for key, value in request.query_params.items():
            if key == 'identificacion':
                filter['id_deudor_actuacion__identificacion__icontains'] = value
            elif key == 'nombres' or key == 'apellidos':
                if value != '':
                    filter['id_deudor_actuacion__' + key + '__icontains'] = value
        facilidades_pago = FacilidadesPago.objects.filter(**filter)
        serializer = ListadoFacilidadesPagoSerializer(facilidades_pago, many=True)
        return Response(serializer.data)


class ConsultaFacilidadesPagosViews(generics.ListAPIView):
    serializer_class = ConsultaFacilidadesPagosSerializer
    
    def get_queryset(self):
        id_facilidades = self.kwargs['id']
        queryset = FacilidadesPago.objects.filter(id=id_facilidades)
        return queryset


class ListadoDeudoresViews(generics.ListAPIView):
    serializer_class = ListadoDeudoresUltSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        filter = {}
        for key, value in self.request.query_params.items():
            if key == 'identificacion':
                filter[key + '__icontains'] = value
            elif key == 'nombre_contribuyente':
                if value != '':
                    nombres_apellidos = value.split()
                    if len(nombres_apellidos) >= 2:
                        nombres = ' '.join(nombres_apellidos[:-1])
                        apellidos = nombres_apellidos[-1]
                        filter['nombres__icontains'] = nombres
                        filter['apellidos__icontains'] = apellidos
        return Deudores.objects.filter(**filter).values('identificacion', 'nombres', 'apellidos')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        data = [{'identificacion': item['identificacion'], 'nombre_contribuyente': f"{item['nombres']} {item['apellidos']}"} for item in queryset]
        return Response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': data})

class ListadoFacilidadesPagoFuncionariosViews(generics.ListAPIView):
    serializer_class = ListadoFacilidadesPagoSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = self.request.user
        facilidades_pago = FacilidadesPago.objects.filter(id_funcionario=user.pk)
        for key, value in request.query_params.items():
            if key == 'identificacion':
                facilidades_pago = facilidades_pago.filter(id_deudor_actuacion__identificacion__icontains=value)
            elif key == 'nombre_de_usuario':
                facilidades_pago = facilidades_pago.filter(id_deudor_actuacion__usuario__primer_nombre__icontains=value)
        serializer = ListadoFacilidadesPagoSerializer(facilidades_pago, many=True)
        return Response(serializer.data)


class RequisitosActuacionView(generics.ListAPIView):
    serializer_class = RequisitosActuacionSerializer
    queryset = RequisitosActuacion
    
    def get(self, request, id):
        queryset = RequisitosActuacion.objects.filter(id_tipo_actuacion=id)
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)


class AgregarDocumentosRequisitosView(generics.CreateAPIView):
    serializer_class = CumplimientoRequisitosSerializer
    queryset = CumplimientoRequisitos.objects.all()

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'data':serializer.data})