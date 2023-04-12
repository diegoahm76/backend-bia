import calendar
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from estaciones.serializers.datos_serializers import DatosSerializer, DatosSerializerNombre
from estaciones.models.estaciones_models import Datos
from datetime import datetime

# consultar datos por el id estacion

class ConsultarDatosId(generics.ListAPIView):
    serializer_class = DatosSerializer
    queryset = Datos.objects.all().using("bia-estaciones")
    permission_classes = [IsAuthenticated]

    def get(self, requet, pk):
        estaciones = self.queryset.filter(id_estacion=pk)
        if estaciones:
            serializador = self.serializer_class(estaciones, many=True)
            return Response({'success': True, 'detail': 'Se encontraron los siguentes datos', 'data': serializador.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success': True, 'detail': 'No se encontraron datos'}, status=status.HTTP_404_NOT_FOUND)

# consultar datos por el id estacion primeros 500 datos

class ConsultarDatosIdPrimerosDatos(generics.ListAPIView):
    serializer_class = DatosSerializerNombre
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return Datos.objects.using("bia-estaciones").filter(id_estacion=pk).order_by('-fecha_registro')[:500]

    def get(self, request, pk):
        queryset = self.get_queryset()
        if queryset:
            serializador = self.serializer_class(queryset, many=True)
            return Response({'success': True, 'detail': 'Estos son los 500 primeros datos', 'data': serializador.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'detail': 'No se encontraron datos'}, status=status.HTTP_404_NOT_FOUND)

# consultar datos por fechas

class ConsultarDatosFecha(generics.ListAPIView):
    serializer_class = DatosSerializerNombre
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Datos.objects.all().using("bia-estaciones")

        # Obtener los parámetros de consulta de la URL
        fecha_inicial = self.kwargs.get('fecha_inicial')
        fecha_final = self.kwargs.get('fecha_final')
        pk = self.kwargs.get('pk')

        # Filtrar los datos por fecha si se especificaron los parámetros de consulta
        if fecha_inicial and fecha_final and pk:
            queryset = queryset.filter(fecha_registro__range=[
                                       fecha_inicial, fecha_final], id_estacion=pk)

        return queryset

    def get(self, request, pk, fecha_inicial, fecha_final):
        queryset = self.get_queryset()

        if queryset:
            serializador = self.serializer_class(queryset, many=True)
            return Response({'success': True, 'detail': 'Se encontraron los siguientes datos', 'data': serializador.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success': True, 'detail': 'No se encontraron datos'}, status=status.HTTP_200_OK)

    # Listar Datos por fecha de un mes atras


class ConsultarDatosReportes(generics.ListAPIView):
    serializer_class = DatosSerializerNombre
    queryset = Datos.objects.all().using("bia-estaciones")
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

        datos = self.queryset.filter(fecha_registro__range=[
                                     fecha_inicio, fecha_fin], id_estacion=pk)

        if datos:
            serializador = self.serializer_class(datos, many=True)
            return Response({'success': True, 'detail': 'Se encontraron los siguientes datos', 'data': serializador.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success': True, 'detail': 'No se encontraron datos'}, status=status.HTTP_404_NOT_FOUND)

