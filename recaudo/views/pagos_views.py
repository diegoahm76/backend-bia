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


# OBLIGACIONES
class ObligacionesDeudorListViews(generics.ListAPIView):
    serializer_class = ObligacionesSerializer

    def get_monto_total(self, obligaciones):
        monto_total = 0
        intereses_total = 0
        for obligacion in obligaciones:
            monto_total += obligacion.monto_inicial
            carteras = obligacion.cartera_set.filter(fin__isnull=True)
            for cartera in carteras:
                intereses_total += cartera.valor_intereses
        return monto_total, intereses_total, monto_total + intereses_total
    
    def obligaciones_deudor(self, id):
        deudor = Deudores.objects.get(id=id)
        facilidad = FacilidadesPago.objects.filter(id_deudor=deudor.id).exists()
        nombre_completo = deudor.nombres + ' ' + deudor.apellidos
        obligaciones = Obligaciones.objects.filter(id_expediente__id_deudor=deudor)
        serializer = self.serializer_class(obligaciones, many=True)
        monto_total, intereses_total, monto_total_con_intereses = self.get_monto_total(obligaciones)
        data = {
            'id_deudor': deudor.id,
            'nombre_completo': nombre_completo,
            'numero_identificacion': deudor.identificacion,
            'email': deudor.email,
            'obligaciones': serializer.data,
            'monto_total': monto_total,
            'intereses_total': intereses_total,
            'monto_total_con_intereses': monto_total_con_intereses,
            'tiene_facilidad' : facilidad
        }
        return data

    
class ListadoObligacionesViews(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        numero_identificacion = user.persona.numero_documento
        try:
            deudor = Deudores.objects.get(identificacion=numero_identificacion)
        except ObjectDoesNotExist:
            raise NotFound('No se encontró un objeto deudor para este usuario.')
        
        instancia_obligaciones = ObligacionesDeudorListViews()
        response_data = instancia_obligaciones.obligaciones_deudor(deudor.id)

        if response_data:
            return Response({'success': True, 'data': response_data}, status=status.HTTP_200_OK)
        else:
            raise ValidationError('El dato ingresado no es valido')


class DatosDeudorView(generics.ListAPIView):
    queryset = Deudores.objects.all()
    serializer_class = DeudorFacilidadPagoSerializer

    def get(self, request, id):
        queryset = Deudores.objects.filter(id=id).first()

        if not queryset:
            raise NotFound('No se encontró ningun registro con el parámetro ingresado')
        serializer = self.serializer_class(queryset)
        return Response({'success': True, 'detail':'Se muestra los datos del deudor', 'data': serializer.data}, status=status.HTTP_200_OK)   


class ConsultaObligacionesDeudoresViews(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, identificacion):
        numero_identificacion = identificacion

        try:
            deudor = Deudores.objects.get(identificacion=numero_identificacion)
        except ObjectDoesNotExist:
            raise NotFound('No se encontraron resultados.')
        
        instancia_obligaciones = ObligacionesDeudorListViews()
        response_data = instancia_obligaciones.obligaciones_deudor(deudor.id)

        if response_data:
            return Response({'success': True, 'data': response_data}, status=status.HTTP_200_OK)
        else:
            raise ValidationError('El dato ingresado no es valido')


# FACILIDAD DE PAGO      














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
                return Response({'success': True, 'detail':'Se le asigna el funcionario a la facilidad de pago', 'data':serializer.data}, status=status.HTTP_200_OK)
            else:
                raise PermissionDenied('El funcionario ingresado no tiene permisos')
        else:
            raise NotFound('La facilidad de pago ingresada no existe')
    

class FuncionariosView(generics.ListAPIView):
    serializer_class = FuncionariosSerializer
    queryset = Personas.objects.all()

    def get(self, request):
        funcionarios = ClasesTerceroPersona.objects.filter(id_clase_tercero=2)
        funcionarios = [funcionario.id_persona for funcionario in funcionarios]
        serializer = self.serializer_class(funcionarios, many=True)
        return Response({'success': True, 'detail':'Se muestra los funcionarios para facilidades de pago', 'data':serializer.data}, status=status.HTTP_200_OK)


class ConsultaObligacionesViews(generics.ListAPIView):
    serializer_class = ConsultaObligacionesSerializer
    
    def get_queryset(self):
        id_obligaciones = self.kwargs['id_obligaciones']
        queryset = Obligaciones.objects.filter(id=id_obligaciones)
        
        if not queryset.exists():
            raise NotFound("La obligación consultada no existe")
        return queryset


class ListadoFacilidadesPagoViews(generics.ListAPIView):
    serializer_class = ListadoFacilidadesPagoSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):

        facilidades_pago = FacilidadesPago.objects.annotate(nombre_de_usuario=Concat('id_deudor__nombres', V(' '), 'id_deudor__apellidos'))
        identificacion = self.request.query_params.get('identificacion', '')
        nombre_de_usuario = self.request.query_params.get('nombre_de_usuario', '')
        facilidades_pago = facilidades_pago.filter(id_deudor__identificacion__icontains=identificacion)
        nombres_apellidos = nombre_de_usuario.split()
        
        for x in range(len(nombres_apellidos)):
            facilidades_pago = facilidades_pago.filter(nombre_de_usuario__icontains=nombres_apellidos[x])
        
        if not facilidades_pago.exists():
            raise NotFound("La facilidad de pagos consultada no existe")

        serializer = ListadoFacilidadesPagoSerializer(facilidades_pago, many=True)
        return Response({'success':True, 'detail':'Se muestra las facilidades de pago del deudor', 'data':serializer.data},status=status.HTTP_200_OK)


class ConsultaFacilidadesPagosViews(generics.ListAPIView):
    serializer_class = ConsultaFacilidadesPagosSerializer
    
    def get(self, request, id):
        queryset = FacilidadesPago.objects.filter(id=id).first()
        if not queryset:
            raise NotFound('No se encontró ningun registro con el parámetro ingresado')
        serializer = self.serializer_class(queryset, many=False)
        return Response({'success': True, 'detail':'Se muestra los datos la facilidad de pago', 'data': serializer.data}, status=status.HTTP_200_OK)   
        

class ListadoDeudoresViews(generics.ListAPIView):
    queryset = Deudores.objects.all()
    serializer_class = ListadoDeudoresUltSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        identificacion = self.request.query_params.get('identificacion', '')
        nombre_contribuyente = self.request.query_params.get('nombre_contribuyente', '')
        deudores = Deudores.objects.annotate(nombre_contribuyente=Concat('nombres', V(' '), 'apellidos')).filter(identificacion__icontains=identificacion)
        nombres_apellidos = nombre_contribuyente.split()
        
        for x in range(len(nombres_apellidos)):
            deudores = deudores.filter(nombre_contribuyente__icontains=nombres_apellidos[x])

        return deudores.values('id','identificacion', 'nombres', 'apellidos')

    def list(self, request, *args, **kwargs):
        current_user = self.request.user
        try:
            user = User.objects.get(pk=current_user.pk)
        except User.DoesNotExist:
            raise NotFound('El usuario no tiene deudas')

        queryset = self.get_queryset()
        if not queryset.exists():
            raise NotFound('No se encontraron resultados.')
    
        data = [{'id_deudor': item['id'],'identificacion': item['identificacion'], 'nombre_contribuyente': f"{item['nombres']} {item['apellidos']}"} for item in queryset]
        return Response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': data}, status=status.HTTP_200_OK)


class ListadoFacilidadesPagoFuncionariosViews(generics.ListAPIView):
    serializer_class = ListadoFacilidadesPagoSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = self.request.user
        facilidades_pago = FacilidadesPago.objects.annotate(nombre_de_usuario=Concat('id_deudor__nombres', V(' '), 'id_deudor__apellidos')).filter(id_funcionario=user.pk)
        identificacion = self.request.query_params.get('identificacion', '')
        nombre_de_usuario = self.request.query_params.get('nombre_de_usuario', '')
        facilidades_pago = facilidades_pago.filter(id_deudor__identificacion__icontains=identificacion)
        nombres_apellidos = nombre_de_usuario.split()
        
        for x in range(len(nombres_apellidos)):
            facilidades_pago = facilidades_pago.filter(nombre_de_usuario__icontains=nombres_apellidos[x])
        
        serializer = ListadoFacilidadesPagoSerializer(facilidades_pago, many=True)
        return Response( {'success': True, 'detail':'Se le asignaron las siguientes facilidades de pago','data':serializer.data},status=status.HTTP_200_OK)


class RequisitosActuacionView(generics.ListAPIView):
    serializer_class = RequisitosActuacionSerializer
    queryset = RequisitosActuacion
    
    def get(self, request, id):
        queryset = RequisitosActuacion.objects.filter(id_tipo_actuacion=id)
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'detail':'Se muestra los requisitos deltipo de actuacion del deudor',  'data': serializer.data}, status=status.HTTP_200_OK)


class AgregarDocumentosRequisitosView(generics.CreateAPIView):
    serializer_class = CumplimientoRequisitosSerializer
    queryset = CumplimientoRequisitos.objects.all()

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail':'Se agregar los documentos requeridos para el deudor actuacion', 'data':serializer.data},status=status.HTTP_200_OK)


class AutorizacionNotificacionesView(generics.RetrieveUpdateAPIView):
    serializer_class = AutorizacionNotificacionesSerializer
    queryset = FacilidadesPago.objects.all()

    def put(self, request, *args, **kwargs):
        facilidad_pago = self.get_object()
        data = request.data
        notificaciones = data.get('notificaciones')

        if notificaciones:
            facilidad_pago.notificaciones = True
            facilidad_pago.save()
            return Response({'success': True, 'detail': 'El usuario acepta las notificaciones por correo electrónico'}, status=status.HTTP_200_OK)
        else:
            facilidad_pago.notificaciones = False
            facilidad_pago.save()
            raise ValidationError('El usuario no acepta notificaciones por correo electrónico')
    

class DocumentosRequisitosView(generics.ListAPIView):
    serializer_class = CumplimientoRequisitosSerializer
    queryset = CumplimientoRequisitos.objects.all()

    def get(self, request, id):
        queryset = CumplimientoRequisitos.objects.filter(id_facilidad_pago=id)
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'detail':'Se muestra los documentos del tipo de actuacion del deudor',  'data': serializer.data}, status=status.HTTP_200_OK) 


class RespuestaSolicitudFacilidadView(generics.CreateAPIView):
    serializer_class = RespuestaSolicitudFacilidadSerializer

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'success': True, 'detail':'Se registra la respuesta la respuesta dada por el funcionario', 'data':serializer.data},status=status.HTTP_200_OK)
   