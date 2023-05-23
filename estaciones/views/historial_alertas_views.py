import calendar
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from estaciones.serializers.historial_alertas_serializer import HistorialAlarmasEnviadasEstacionSerializer, AlertasEquipoEstacionSerializer
from estaciones.models.estaciones_models import HistorialAlarmasEnviadasEstacion, AlertasEquipoEstacion
from datetime import datetime


class ConsultarDatosAlertas(generics.ListAPIView):
    serializer_class = HistorialAlarmasEnviadasEstacionSerializer
    queryset = HistorialAlarmasEnviadasEstacion.objects.all().using("bia-estaciones")
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        mes_str = kwargs.get('mes')
        if not mes_str:
            return Response({'success': False, 'detail': 'El mes es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            fecha_inicio = datetime.strptime(mes_str, '%Y-%m')
            fecha_fin = fecha_inicio.replace(day=calendar.monthrange(
                fecha_inicio.year, fecha_inicio.month)[1])
        except ValueError:
            return Response({'success': False, 'detail': 'El mes debe estar en el formato YYYY-MM'}, status=status.HTTP_400_BAD_REQUEST)

        alertas = self.queryset.filter(fecha_hora_envio__range=[
            fecha_inicio, fecha_fin], id_estacion=pk)

        if alertas:
            serializador = self.serializer_class(alertas, many=True)
            return Response({'success': True, 'detail': 'Se encontraron los siguientes datos de historial alertas', 'data': serializador.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success': True, 'detail': 'No se encontraron datos de historial alertas'}, status=status.HTTP_404_NOT_FOUND)


class ConsultarDatosEquipos(generics.ListAPIView):
    serializer_class = AlertasEquipoEstacionSerializer
    queryset = AlertasEquipoEstacion.objects.all().using("bia-estaciones")
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        mes_str = kwargs.get('mes')
        if not mes_str:
            return Response({'success': False, 'detail': 'El mes es requerido'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            fecha_inicio = datetime.strptime(mes_str, '%Y-%m')
            fecha_fin = fecha_inicio.replace(day=calendar.monthrange(
                fecha_inicio.year, fecha_inicio.month)[1])
        except ValueError:
            return Response({'success': False, 'detail': 'El mes debe estar en el formato YYYY-MM'}, status=status.HTTP_400_BAD_REQUEST)

        alertas = self.queryset.filter(fecha_generacion__range=[
            fecha_inicio, fecha_fin], id_estacion=pk)

        if alertas:
            serializador = self.serializer_class(alertas, many=True)
            return Response({'success': True, 'detail': 'Se encontraron los siguientes datos de historial alertas equipos', 'data': serializador.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success': True, 'detail': 'No se encontraron datos de historial alertas equipos'}, status=status.HTTP_404_NOT_FOUND)
