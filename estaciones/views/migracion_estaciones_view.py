from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from estaciones.serializers.migracion_estaciones_serializer import MigracionSerializer
from estaciones.models.estaciones_models import Migracion
# Listar Estaciones


class ConsultarMigracion(generics.ListAPIView):
    serializer_class = MigracionSerializer
    queryset = Migracion.objects.all().using("bia-estaciones")
    permission_classes = [IsAuthenticated]

    def get(self, request):
        estaciones = self.queryset.all()
        data = []

        for estacion in estaciones:
            sensor1_data = {}
            sensor2_data = {}

            # Procesar los datos del sensor 1
            sensor1_raw_data = estacion.sensor1.strip('{}').split(',')
            for raw_data in sensor1_raw_data:
                date, time, value = raw_data.split(';')
                timestamp = date + time
                sensor1_data[timestamp] = value
                # print("sensor data view", sensor1_data[timestamp])

            # Procesar los datos del sensor 2
            sensor2_raw_data = estacion.sensor2.strip('{}').split(',')
            for raw_data in sensor2_raw_data:
                date, time, value = raw_data.split(';')
                timestamp = date + time
                sensor2_data[timestamp] = value

            # Crear objetos con los datos procesados
            timestamps = set(sensor1_data.keys()).intersection(
                sensor2_data.keys())
            # print(timestamps)
            for timestamp in timestamps:

                data.append({
                    'id_migracion_estacion': estacion.id_migracion_estacion,
                    'id_estacion': estacion.id_estacion,
                    'nombre': estacion.nombre,
                    'fecha': timestamp,
                    'sensor1_data': sensor1_data[timestamp],
                    'sensor2_data': sensor2_data[timestamp],
                })
        # print(data)
        serializador = self.serializer_class(data, many=True)

        return Response({'success': True, 'detail': 'Se encontraron las siguientes estaciones', 'data': serializador.data}, status=status.HTTP_200_OK)
    

class ConsultarMigracionId(generics.ListAPIView):
    serializer_class = MigracionSerializer
    queryset = Migracion.objects.all().using("bia-estaciones")
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        estacion = self.queryset.all().filter(id_estacion = pk).first()
        data = []
      
        sensor1_data = {}
        sensor2_data = {}

        # Procesar los datos del sensor 1
        sensor1_raw_data = estacion.sensor1.strip('{}').split(',')
        for raw_data in sensor1_raw_data:
            date, time, value = raw_data.split(';')
            timestamp = date + time
            sensor1_data[timestamp] = value
            # print("sensor data view", sensor1_data[timestamp])

        # Procesar los datos del sensor 2
        sensor2_raw_data = estacion.sensor2.strip('{}').split(',')
        for raw_data in sensor2_raw_data:
            date, time, value = raw_data.split(';')
            timestamp = date + time
            sensor2_data[timestamp] = value

        # Crear objetos con los datos procesados
        timestamps = set(sensor1_data.keys()).intersection(
            sensor2_data.keys())
        # print(timestamps)
        for timestamp in timestamps:

            data.append({
                'id_migracion_estacion': estacion.id_migracion_estacion,
                'id_estacion': estacion.id_estacion,
                'nombre': estacion.nombre,
                'fecha': timestamp,
                'sensor1_data': sensor1_data[timestamp],
                'sensor2_data': sensor2_data[timestamp],
            })
        # print(data)
        serializador = self.serializer_class(data, many=True)
        
        return Response({'success': True, 'detail': 'Se encontraron las siguientes estaciones', 'data': serializador.data}, status=status.HTTP_200_OK)
