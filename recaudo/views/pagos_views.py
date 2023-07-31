from recaudo.models.facilidades_pagos_models import (
    FacilidadesPago,
    PlanPagos,
    TasasInteres
)
from recaudo.serializers.pagos_serializers import (
    DetallesFacilidadPagoSerializer,
    ObligacionesSerializer,
    ConsultaObligacionesSerializer,
    ListadoDeudoresUltSerializer,
)
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

        if deudor.nombres:
            if deudor.apellidos:
                nombre_completo = deudor.nombres + ' ' + deudor.apellidos
            nombre_completo = deudor.nombres
        
        obligaciones = Cartera.objects.filter(id_deudor=deudor)
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
 

class ConsultaObligacionesViews(generics.ListAPIView):
    serializer_class = ConsultaObligacionesSerializer
    
    def get_queryset(self):
        id_obligaciones = self.kwargs['id_obligaciones']
        queryset = Cartera.objects.filter(id=id_obligaciones)
        
        if not queryset.exists():
            raise NotFound("La obligación consultada no existe")
        return queryset


class ListadoDeudoresViews(generics.ListAPIView):
    serializer_class = ListadoDeudoresUltSerializer
    permission_classes = [IsAuthenticated]

    def get_lista_deudores(self):

        identificacion = self.request.query_params.get('identificacion', '')
        nombre_contribuyente = self.request.query_params.get('nombre_contribuyente', '')
        nombres_apellidos = nombre_contribuyente.split()

        deudores = Deudores.objects.annotate(nombre_contribuyente=Concat('nombres', V(' '), 'apellidos')).filter(identificacion__icontains=identificacion)

        for nombre_apellido in nombres_apellidos:
            deudores = deudores.filter(nombre_contribuyente__icontains=nombre_apellido)

        return deudores.values('id', 'identificacion', 'nombres', 'apellidos')

    def list(self, request, *args, **kwargs):
        queryset = self.get_lista_deudores()

        if not queryset.exists():
            raise NotFound('No se encontraron resultados.')
    
        data = [{'id_deudor': item['id'], 'identificacion': item['identificacion'], 'nombre_contribuyente': f"{item['nombres']} {item['apellidos']}"} for item in queryset]
        return Response({'success': True, 'detail': 'Resultados de la búsqueda', 'data': data}, status=status.HTTP_200_OK)
