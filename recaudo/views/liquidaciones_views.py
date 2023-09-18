from recaudo.models.liquidaciones_models import (
    OpcionesLiquidacionBase,
    Deudores,
    LiquidacionesBase,
    DetalleLiquidacionBase,
    Expedientes
)
from recaudo.serializers.liquidaciones_serializers import (
    OpcionesLiquidacionBaseSerializer,
    OpcionesLiquidacionBasePutSerializer,
    DeudoresSerializer,
    LiquidacionesBaseSerializer,
    LiquidacionesBasePostSerializer,
    DetallesLiquidacionBaseSerializer,
    DetallesLiquidacionBasePostSerializer,
    ExpedientesSerializer
)
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from django.shortcuts import render


class OpcionesLiquidacionBaseView(generics.ListAPIView):
    queryset = OpcionesLiquidacionBase.objects.all()
    serializer_class = OpcionesLiquidacionBaseSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DetalleOpcionesLiquidacionBaseView(generics.GenericAPIView):
    queryset = OpcionesLiquidacionBase.objects.all()
    serializer_class = OpcionesLiquidacionBaseSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        queryset = OpcionesLiquidacionBase.objects.filter(pk=pk).first()
        if not queryset:
            return Response({'success': False, 'detail': 'No se encontró ningun registro con el parámetro ingresado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(queryset)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)

    def put(self, request, pk):
        opcion = OpcionesLiquidacionBase.objects.filter(pk=pk).get()
        serializer = OpcionesLiquidacionBasePutSerializer(opcion, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EliminarOpcionesLiquidacionBaseView(generics.GenericAPIView):
    queryset = OpcionesLiquidacionBase.objects.all()
    serializer_class = OpcionesLiquidacionBaseSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        opcion_liquidacion = OpcionesLiquidacionBase.objects.filter(pk=pk).first()
        if opcion_liquidacion:
            opcion_liquidacion.delete()
            return Response({'success': True, 'detail': 'La opción de liquidación ha sido eliminado exitosamente'}, status=status.HTTP_200_OK)
        else:
            raise NotFound('No existe la opción de liquidación')


class DeudoresView(generics.GenericAPIView):
    queryset = Deudores.objects.all()
    serializer_class = DeudoresSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)


class DeudoresIdentificacionView(generics.GenericAPIView):
    serializer_class = DeudoresSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request, identificacion):
        queryset = Deudores.objects.filter(identificacion=identificacion).first()
        if not queryset:
            return Response({'success': False, 'detail': 'No se encontró ningun deudor con la identificación ingresada'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(queryset)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)


class LiquidacionBaseView(generics.ListAPIView):
    queryset = LiquidacionesBase.objects.all()
    serializer_class = LiquidacionesBaseSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = LiquidacionesBasePostSerializer(data=request.data)
        if serializer.is_valid():
            id_expediente = request.data['id_expediente']
            if id_expediente is not None:
                expediente = Expedientes.objects.get(pk=id_expediente)
                expediente.liquidado = True
                serializer.save()
                expediente.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ObtenerLiquidacionBaseView(generics.GenericAPIView):
    serializer_class = LiquidacionesBaseSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        queryset = LiquidacionesBase.objects.filter(pk=pk).first()
        if not queryset:
            return Response({'success': False, 'detail': 'No se encontró ninguna liquidación base con el id ingresado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(queryset)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)


class ObtenerLiquidacionPorIdExpedienteBaseView(generics.GenericAPIView):
    serializer_class = LiquidacionesBaseSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        queryset = LiquidacionesBase.objects.filter(id_expediente=pk).first()
        if not queryset:
            return Response({'success': False, 'detail': 'No se encontró ninguna liquidación base con el id de expediente ingresado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(queryset)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)


class DetallesLiquidacionBaseView(generics.GenericAPIView):
    serializer_class = DetallesLiquidacionBaseSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request, liquidacion):
        queryset = DetalleLiquidacionBase.objects.filter(id_liquidacion__id=liquidacion)
        if len(queryset) == 0:
            return Response({'success': False, 'detail': 'No se encontró ningun detalle para la liquidación base'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = DetallesLiquidacionBasePostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExpedientesView(generics.ListAPIView):
    queryset = Expedientes.objects.all()
    serializer_class = ExpedientesSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)


class ExpedienteEspecificoView(generics.ListAPIView):
    queryset = Expedientes.objects.all()
    serializer_class = ExpedientesSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        queryset = Expedientes.objects.filter(pk=pk).first()
        if not queryset:
            return Response({'success': False, 'detail': 'No se encontró ningun expendiente con el id ingresado'}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.serializer_class(queryset)
        return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)


class ClonarOpcionLiquidacionView(generics.ListAPIView):
    queryset = OpcionesLiquidacionBase.objects.all()
    serializer_class = OpcionesLiquidacionBaseSerializer
    #permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        opcion = OpcionesLiquidacionBase.objects.filter(pk=pk)
        if len(opcion) == 0:
            return Response({'success': False, 'detail': 'No existen opción de liquidación para clonar'}, status=status.HTTP_200_OK)
        else:
            opcion_actual = opcion.get()
            opcion_nueva = OpcionesLiquidacionBase(
                nombre='Copia ' + opcion_actual.nombre,
                estado=opcion_actual.estado,
                version=opcion_actual.version,
                funcion=opcion_actual.funcion,
                variables=opcion_actual.variables,
                bloques=opcion_actual.bloques
            )
            opcion_nueva.save()
            serializer = self.serializer_class(opcion_nueva, many=False)
            return Response({'success': True, 'data': serializer.data}, status=status.HTTP_200_OK)


class ExpedientesDeudorGetView(generics.ListAPIView):
    serializer_class = ExpedientesSerializer

    def get_expedientes_deudor(self, id_deudor):
        expedientes = Expedientes.objects.filter(id_deudor=id_deudor)
        if not expedientes:
            raise NotFound('No se encontró ningún registro en expedientes con el parámetro ingresado')
        serializer = self.serializer_class(expedientes, many=True)
        return serializer.data

    def get(self, request, id_deudor):
        expedientes = self.get_expedientes_deudor(id_deudor)
        return Response({'success': True, 'detail':'Se muestra los expedientes del deudor', 'data':expedientes}, status=status.HTTP_200_OK)


def liquidacionPdf(request, pk):
    liquidacion = LiquidacionesBase.objects.filter(pk=pk).get()
    context = {
        'referencia_pago': liquidacion.id,
        'limite_pago': liquidacion.vencimiento,
        'cedula': liquidacion.id_deudor.identificacion,
        'titular': liquidacion.id_deudor.nombres + ' ' + liquidacion.id_deudor.apellidos,
        'numero_cuota': liquidacion.periodo_liquidacion,
        'valor_cuota': liquidacion.valor,
        'fecha_impresion': liquidacion.fecha_liquidacion,
        'codigo_barras': '',
    }
    return render(request, 'liquidacion.html', context=context)