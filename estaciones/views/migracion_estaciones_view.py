from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from estaciones.serializers.migracion_estaciones_serializer import MigracionSerializer
from estaciones.models.estaciones_models import Migracion
from datetime import datetime
# Listar Estaciones


class ConsultarMigracionId(generics.ListAPIView):
    serializer_class = MigracionSerializer
    queryset = Migracion.objects.all().using("bia-estaciones")
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        fecha_inicio = request.query_params.get('fecha')
        fecha_desde = request.query_params.get('fecha-desde')
        fecha_hasta = request.query_params.get('fecha-hasta')

        estacion = self.queryset.all().filter(id_estacion=pk).first()
        if estacion:
            data = []

            sensor1_data = {}
            sensor2_data = {}
            sensor3_data = {}
            sensor4_data = {}
            sensor5_data = {}
            sensor6_data = {}
            sensor7_data = {}
            sensor8_data = {}
            sensor9_data = {}
            sensor10_data = {}
            sensor11_data = {}
            sensor12_data = {}
            sensor13_data = {}
            sensor14_data = {}
            sensor15_data = {}

            # Procesar los datos del sensor 1
            sensor1_raw_data = estacion.sensor1.strip('{}').split(',')
            for raw_data in sensor1_raw_data:
                values = raw_data.split(';')
                if len(values) == 3:
                    date, time, value = values
                    timestamp = date + time
                    sensor1_data[timestamp] = value

            # Procesar los datos del sensor 2
            sensor2_raw_data = estacion.sensor2.strip('{}').split(',')
            for raw_data in sensor2_raw_data:
                values = raw_data.split(';')
                if len(values) == 3:
                    date, time, value = values
                    timestamp = date + time
                    sensor2_data[timestamp] = value

            # Procesar los datos del sensor 3
            sensor3_raw_data = estacion.sensor3.strip('{}').split(',')
            for raw_data in sensor3_raw_data:
                values = raw_data.split(';')
                if len(values) == 3:
                    date, time, value = values
                    timestamp = date + time
                    sensor3_data[timestamp] = value

             # Procesar los datos del sensor 4
            sensor4_raw_data = estacion.sensor4.strip('{}').split(',')
            for raw_data in sensor4_raw_data:
                values = raw_data.split(';')
                if len(values) == 3:
                    date, time, value = values
                    timestamp = date + time
                    sensor4_data[timestamp] = value

             # Procesar los datos del sensor 5
            sensor5_raw_data = estacion.sensor5.strip('{}').split(',')
            for raw_data in sensor5_raw_data:
                values = raw_data.split(';')
                if len(values) == 3:
                    date, time, value = values
                    timestamp = date + time
                    sensor5_data[timestamp] = value

            # Procesar los datos del sensor 6
            sensor6_raw_data = estacion.sensor6.strip('{}').split(',')
            for raw_data in sensor6_raw_data:
                values = raw_data.split(';')
                if len(values) == 3:
                    date, time, value = values
                    timestamp = date + time
                    sensor6_data[timestamp] = value

            # Procesar los datos del sensor 7
            sensor7_raw_data = estacion.sensor7.strip('{}').split(',')
            for raw_data in sensor7_raw_data:
                values = raw_data.split(';')
                if len(values) == 3:
                    date, time, value = values
                    timestamp = date + time
                    sensor7_data[timestamp] = value

            # Procesar los datos del sensor 8
            sensor8_raw_data = estacion.sensor8.strip('{}').split(',')
            for raw_data in sensor8_raw_data:
                values = raw_data.split(';')
                if len(values) == 3:
                    date, time, value = values
                    timestamp = date + time
                    sensor8_data[timestamp] = value

            # Procesar los datos del sensor 9
            sensor9_raw_data = estacion.sensor9.strip('{}').split(',')
            for raw_data in sensor9_raw_data:
                values = raw_data.split(';')
                if len(values) == 3:
                    date, time, value = values
                    timestamp = date + time
                    sensor9_data[timestamp] = value

            # Procesar los datos del sensor 10
            sensor10_raw_data = estacion.sensor10.strip('{}').split(',')
            for raw_data in sensor10_raw_data:
                values = raw_data.split(';')
                if len(values) == 3:
                    date, time, value = values
                    timestamp = date + time
                    sensor10_data[timestamp] = value

            # Procesar los datos del sensor 11
            sensor11_raw_data = estacion.sensor11.strip('{}').split(',')
            for raw_data in sensor11_raw_data:
                values = raw_data.split(';')
                if len(values) == 3:
                    date, time, value = values
                    timestamp = date + time
                    sensor11_data[timestamp] = value

            # Procesar los datos del sensor 12
            sensor12_raw_data = estacion.sensor12.strip('{}').split(',')
            for raw_data in sensor12_raw_data:
                values = raw_data.split(';')
                if len(values) == 3:
                    date, time, value = values
                    timestamp = date + time
                    sensor12_data[timestamp] = value

            # Procesar los datos del sensor 13
            sensor13_raw_data = estacion.sensor13.strip('{}').split(',')
            for raw_data in sensor13_raw_data:
                values = raw_data.split(';')
                if len(values) == 3:
                    date, time, value = values
                    timestamp = date + time
                    sensor13_data[timestamp] = value

            # Procesar los datos del sensor 14
            sensor14_raw_data = estacion.sensor14.strip('{}').split(',')
            for raw_data in sensor14_raw_data:
                values = raw_data.split(';')
                if len(values) == 3:
                    date, time, value = values
                    timestamp = date + time
                    sensor14_data[timestamp] = value

            # Procesar los datos del sensor 14
            sensor15_raw_data = estacion.sensor15.strip('{}').split(',')
            for raw_data in sensor15_raw_data:
                values = raw_data.split(';')
                if len(values) == 3:
                    date, time, value = values
                    timestamp = date + time
                    sensor15_data[timestamp] = value

            # Crear objetos con los datos procesados
            common_timestamps = set(sensor1_data.keys()).intersection(sensor2_data.keys()).intersection(sensor3_data.keys()).intersection(sensor4_data.keys()).intersection(sensor5_data.keys()).intersection(sensor6_data.keys()).intersection(sensor7_data.keys()).intersection(
                sensor8_data.keys()).intersection(sensor9_data.keys()).intersection(sensor10_data.keys()).intersection(sensor11_data.keys()).intersection(sensor12_data.keys()).intersection(sensor13_data.keys()).intersection(sensor14_data.keys()).intersection(sensor15_data.keys())

            for timestamp in common_timestamps:
                dt = datetime.strptime(timestamp, '%Y%m%d%H%M%S')
                fecha = dt.strftime('%Y-%m-%d %H:%M:%S')
                data.append({
                    'id_migracion_estacion': estacion.id_migracion_estacion,
                    'id_estacion': estacion.id_estacion,
                    'nombre': estacion.nombre,
                    'fecha': fecha,
                    'sensor1_data': sensor1_data.get(timestamp, None),
                    'sensor2_data': sensor2_data.get(timestamp, None),
                    'sensor3_data': sensor3_data.get(timestamp, None),
                    'sensor4_data': sensor4_data.get(timestamp, None),
                    'sensor5_data': sensor5_data.get(timestamp, None),
                    'sensor6_data': sensor6_data.get(timestamp, None),
                    'sensor7_data': sensor7_data.get(timestamp, None),
                    'sensor8_data': sensor8_data.get(timestamp, None),
                    'sensor9_data': sensor9_data.get(timestamp, None),
                    'sensor10_data': sensor10_data.get(timestamp, None),
                    'sensor11_data': sensor11_data.get(timestamp, None),
                    'sensor12_data': sensor12_data.get(timestamp, None),
                    'sensor13_data': sensor13_data.get(timestamp, None),
                    'sensor14_data': sensor14_data.get(timestamp, None),
                    'sensor15_data': sensor15_data.get(timestamp, None),
                })

            lista_data = []

            # TENER EN CUENTA CUANDO NINGUN REGISTRO CUMPLE CON LA CONDICION
        
            if fecha_desde and fecha_hasta:
                print("acaa entro 1")
                fecha_formateada_desde = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
                fecha_formateada_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()

                if fecha_inicio:
                    print("acaa entro 2")
                    return Response({'success': False, 'detail': 'Solo puede enviar una fecha desde y fecha hasta'}, status=status.HTTP_403_FORBIDDEN)

                if fecha_formateada_desde > fecha_formateada_hasta:
                    print("acaa entro 2")
                    return Response({'success': False, 'detail': 'La fecha desde no puede ser posterior a la fecha hasta'}, status=status.HTTP_403_FORBIDDEN)

                for estacion in data:
                    fecha_est = datetime.strptime(estacion['fecha'], '%Y-%m-%d %H:%M:%S').date()

                    if fecha_est >= fecha_formateada_desde and fecha_est <= fecha_formateada_hasta:
                        print("acaa entro 3")
                        lista_data.append(estacion)

                serializador = self.serializer_class(lista_data, many=True)

            if fecha_inicio:
                print("acaa entro 4")

                fecha_formateada = datetime.strptime(fecha_inicio, '%Y-%m')
                year_inicio = fecha_formateada.year
                month_inicio = fecha_formateada.month

                for estacion in data:
                    fecha_estacion = datetime.strptime(
                        estacion['fecha'], '%Y-%m-%d %H:%M:%S')
                    year_estacion = fecha_estacion.year
                    month_estacion = fecha_estacion.month

                    if year_inicio == year_estacion and month_inicio == month_estacion:
                        lista_data.append(estacion)

                serializador = self.serializer_class(lista_data, many=True)

            if not lista_data:
                if fecha_desde is None and fecha_hasta is None and fecha_inicio is None:
                    serializador = self.serializer_class(data, many=True)
                else:
                    return Response({'success': False, 'detail': 'No se encontraron resultados'}, status=status.HTTP_404_NOT_FOUND)

            if serializador:
                data = sorted(serializador.data, key=lambda x: x['fecha'])

                print("acaa entro 6")
                return Response({'success': True, 'detail': 'Se encontró la siguiente estación', 'data': data}, status=status.HTTP_200_OK)

        return Response({'success': False, 'detail': 'No se encontro estación'}, status=status.HTTP_404_NOT_FOUND)
    

