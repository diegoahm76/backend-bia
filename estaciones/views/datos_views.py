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
    # queryset = Datos.objects.all().using("bia-estaciones")
    permission_classes = [IsAuthenticated]

    def get(self, requet, pk):
        estaciones = Datos.objects.filter(id_estacion=pk).values(
                'id_data','fecha_registro','id_estacion','temperatura_ambiente','humedad_ambiente',
                'presion_barometrica','velocidad_viento','direccion_viento','precipitacion',
                'luminosidad','nivel_agua','velocidad_agua'
            ).using("bia-estaciones")
        if estaciones:
            # serializador = self.serializer_class(estaciones, many=True)
            return Response({'success': True, 'detail': 'Se encontraron los siguentes datos', 'data': estaciones}, status=status.HTTP_200_OK)
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
        # Obtener los parámetros de consulta de la URL
        fecha_inicial = self.kwargs.get('fecha_inicial')
        fecha_final = self.kwargs.get('fecha_final')
        pk = self.kwargs.get('pk')

        # Filtrar los datos por fecha si se especificaron los parámetros de consulta
        if fecha_inicial and fecha_final and pk:
            queryset = Datos.objects.filter(fecha_registro__range=[
                                       fecha_inicial, fecha_final], id_estacion=pk).using("bia-estaciones").values(
                'id_data','fecha_registro','id_estacion','temperatura_ambiente','humedad_ambiente',
                'presion_barometrica','velocidad_viento','direccion_viento','precipitacion',
                'luminosidad','nivel_agua','velocidad_agua'
            )

        return queryset

    def get(self, request, pk, fecha_inicial, fecha_final):
        queryset = self.get_queryset()

        if queryset:
            # serializador = self.serializer_class(queryset, many=True)
            return Response({'success': True, 'detail': 'Se encontraron los siguientes datos', 'data': queryset}, status=status.HTTP_200_OK)
        else:
            return Response({'success': True, 'detail': 'No se encontraron datos'}, status=status.HTTP_200_OK)

    # Listar Datos por fecha de un mes atras


class ConsultarDatosReportes(generics.ListAPIView):
    serializer_class = DatosSerializerNombre
    # queryset = Datos.objects.all().using("bia-estaciones")
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

        datos = Datos.objects.filter(fecha_registro__range=[
                                     fecha_inicio, fecha_fin], id_estacion=pk).values(
                'id_data','fecha_registro','id_estacion','temperatura_ambiente','humedad_ambiente',
                'presion_barometrica','velocidad_viento','direccion_viento','precipitacion',
                'luminosidad','nivel_agua','velocidad_agua'
            ).using("bia-estaciones").using("bia-estaciones")

        if datos:
            #serializador = self.serializer_class(datos, many=True)
            return Response({'success': True, 'detail': 'Se encontraron los siguientes datos', 'data': datos}, status=status.HTTP_200_OK)
        else:
            return Response({'success': True, 'detail': 'No se encontraron datos'}, status=status.HTTP_404_NOT_FOUND)

class ConsultarDatosFechaDiario(generics.ListAPIView):
    serializer_class = DatosSerializerNombre
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Obtener los parámetros de consulta de la URL
        fecha_inicial = self.kwargs.get('fecha_inicial')
        pk = self.kwargs.get('pk')

        # Convertir la fecha de la URL en un objeto de fecha de Python
        fecha_inicial_dt = datetime.strptime(fecha_inicial, '%Y-%m-%d').date()

        # Filtrar los datos por fecha si se especificaron los parámetros de consulta
        lista=[]
        if fecha_inicial and pk:
            queryset = Datos.objects.filter(id_estacion=pk).using("bia-estaciones").values(
                'id_data','fecha_registro','id_estacion','temperatura_ambiente','humedad_ambiente',
                'presion_barometrica','velocidad_viento','direccion_viento','precipitacion',
                'luminosidad','nivel_agua','velocidad_agua'
            )
            for resgistro in queryset:
                fecha = resgistro['fecha_registro'].date()
                if fecha == fecha_inicial_dt:
                    lista.append(resgistro)
            print("lista",lista)
        else:
            queryset = Datos.objects.none()

        return lista


    def get(self, request, pk, fecha_inicial):
        queryset = self.get_queryset()

        if queryset:
            # serializador = self.serializer_class(queryset, many=True)
            return Response({'success': True, 'detail': 'Se encontraron los siguientes datos', 'data': queryset}, status=status.HTTP_200_OK)
        else:
            
            return Response({'success': False, 'detail': 'No se encontraron datos'}, status=status.HTTP_404_NOT_FOUND)


