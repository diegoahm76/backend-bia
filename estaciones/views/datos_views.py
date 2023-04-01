import calendar
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from estaciones.serializers.datos_serializers import DatosSerializer, DatosSerializerGuamal, DatosSerializerOcoa, DatosSerializerGuayutiba, DatosSerializerGaitan
from estaciones.models.estaciones_models import Datos, DatosGuamal, DatosOcoa, DatosGaitan, DatosGuayuriba
from datetime import datetime, timedelta
# Libreria paginación
from rest_framework.pagination import PageNumberPagination


# Listar Datos


class ConsultarDatos(generics.ListAPIView):
    serializer_class = DatosSerializer
    queryset = Datos.objects.all().using("bia-estaciones")
    permission_classes = [IsAuthenticated]

    def get(self, request):
        datos = self.queryset.all()
        if datos:
            serializador = self.serializer_class(datos, many=True)
            return Response({'success': True, 'detail': 'Se encontraron los siguentes datos', 'data': serializador.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success': True, 'detail': 'No se encontraron datos'}, status=status.HTTP_404_NOT_FOUND)

# Listar Datos


class ConsultarDatosOptimizado(generics.ListAPIView):
    serializer_class = DatosSerializer
    queryset = Datos.objects.all().using("bia-estaciones")
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Obtener los primeros 100 datos
        datos = self.queryset.order_by('-fecha_registro')[:100]
        serializador = self.serializer_class(datos, many=True)
        response_data = {
            'success': True, 'detail': 'Se encontraron los siguientes datos', 'data': serializador.data}

        # Obtener todos los datos restantes y agregarlos a la respuesta
        datos_restantes = self.queryset.order_by('-fecha_registro')[100:]
        serializador_restante = self.serializer_class(
            datos_restantes, many=True)
        response_data['data'] += serializador_restante.data

        return Response(response_data, status=status.HTTP_200_OK)

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
    serializer_class = DatosSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        return Datos.objects.using("bia-estaciones").filter(id_estacion=pk).order_by('-fecha_registro')[:2000]

    def get(self, request, pk):
        queryset = self.get_queryset()
        if queryset:
            serializador = self.serializer_class(queryset, many=True)
            return Response({'success': True, 'detail': 'Estos son los 2000 primeros datos', 'data': serializador.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'detail': 'No se encontraron datos'}, status=status.HTTP_404_NOT_FOUND)


# consultar datos por fechas


class ConsultarDatosFecha(generics.ListAPIView):
    serializer_class = DatosSerializer
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
    serializer_class = DatosSerializer
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


# usando vista Guamal

class ConsultarDatosGuamal(generics.ListAPIView):
    serializer_class = DatosSerializerGuamal
    queryset = DatosGuamal.objects.all().using("bia-estaciones")
    permission_classes = [IsAuthenticated]

    def get(self, request):
        datos = self.queryset.all()
        if datos:
            serializador = self.serializer_class(datos, many=True)
            return Response({'success': True, 'detail': 'Se encontraron los siguentes datos de la estación Guamal', 'data': serializador.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success': True, 'detail': 'No se encontraron datos de la estación Guamal'}, status=status.HTTP_404_NOT_FOUND)

# usando vista Ocoa


class ConsultarDatosOcoa(generics.ListAPIView):
    serializer_class = DatosSerializerOcoa
    queryset = DatosOcoa.objects.all().using("bia-estaciones")
    permission_classes = [IsAuthenticated]

    def get(self, request):
        datos = self.queryset.all()
        if datos:
            serializador = self.serializer_class(datos, many=True)
            return Response({'success': True, 'detail': 'Se encontraron los siguentes datos de la estación Ocoa', 'data': serializador.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success': True, 'detail': 'No se encontraron datos de la estación Ocoa'}, status=status.HTTP_404_NOT_FOUND)

# usando vista Guayuriba


class ConsultarDatosGuayuriba(generics.ListAPIView):
    serializer_class = DatosSerializerGuayutiba
    queryset = DatosGuayuriba.objects.all().using("bia-estaciones")
    permission_classes = [IsAuthenticated]

    def get(self, request):
        datos = self.queryset.all()
        if datos:
            serializador = self.serializer_class(datos, many=True)
            return Response({'success': True, 'detail': 'Se encontraron los siguentes datos de la estación Guayuriba', 'data': serializador.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success': True, 'detail': 'No se encontraron datos de la estación Guayuriba'}, status=status.HTTP_404_NOT_FOUND)


# usando vista Caño Rubiales
class ConsultarDatosGaitan(generics.ListAPIView):
    serializer_class = DatosSerializerGaitan
    queryset = DatosGaitan.objects.all().using("bia-estaciones")
    permission_classes = [IsAuthenticated]

    def get(self, request):
        datos = self.queryset.all()
        if datos:
            serializador = self.serializer_class(datos, many=True)
            return Response({'success': True, 'detail': 'Se encontraron los siguentes datos de la estación Guayuriba', 'data': serializador.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success': True, 'detail': 'No se encontraron datos de la estación Guayuriba'}, status=status.HTTP_404_NOT_FOUND)


# Vistas con paginación

class DatosPagination(PageNumberPagination):
    page_size = 500
    page_size_query_param = 'page_size'
    max_page_size = 1000

#  Caño Rubiales


class ConsultarDatosGaitanPage(generics.ListAPIView):
    serializer_class = DatosSerializerGaitan
    queryset = DatosGaitan.objects.all().using("bia-estaciones")
    permission_classes = [IsAuthenticated]
    pagination_class = DatosPagination

    def get(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({'success': True, 'detail': 'Se encontraron los siguentes datos de la estación Caño Rubiales', 'data': serializer.data}, status=status.HTTP_200_OK)

# Guayuriba


class ConsultarDatosGuayuribaPage(generics.ListAPIView):
    serializer_class = DatosSerializerGuayutiba
    queryset = DatosGuayuriba.objects.all().using("bia-estaciones")
    permission_classes = [IsAuthenticated]
    pagination_class = DatosPagination

    def get(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({'success': True, 'detail': 'Se encontraron los siguentes datos de la estación Guayuriba', 'data': serializer.data}, status=status.HTTP_200_OK)

# Ocoa


class ConsultarDatosOcoaPage(generics.ListAPIView):
    serializer_class = DatosSerializerOcoa
    queryset = DatosOcoa.objects.all().using("bia-estaciones")
    permission_classes = [IsAuthenticated]
    pagination_class = DatosPagination

    def get(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({'success': True, 'detail': 'Se encontraron los siguentes datos de la estación Ocoa', 'data': serializer.data}, status=status.HTTP_200_OK)

# Guamal


class ConsultarDatosGuamalPage(generics.ListAPIView):
    serializer_class = DatosSerializerGuamal
    queryset = DatosGuamal.objects.all().using("bia-estaciones")
    permission_classes = [IsAuthenticated]
    pagination_class = DatosPagination

    def get(self, request):
        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response({'success': True, 'detail': 'Se encontraron los siguentes datos de la estación Guamal', 'data': serializer.data}, status=status.HTTP_200_OK)
