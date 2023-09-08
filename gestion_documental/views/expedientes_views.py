from gestion_documental.models.expedientes_models import ExpedientesDocumentales,ArchivosDigitales,DocumentosDeArchivoExpediente,IndicesElectronicosExp,Docs_IndiceElectronicoExp,CierresReaperturasExpediente,ArchivosSoporte_CierreReapertura
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from django.shortcuts import get_object_or_404
from seguridad.utils import Util
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from gestion_documental.serializers.expedientes_serializers import ExpedienteSearchSerializer
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Max 
from django.db.models import Q
from django.db import transaction
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector


########################## CRUD DE CIERRE DE EXPEDIENTES DOCUMENTALES ##########################

#BUSCAR UN EXPEDIENTE
class ExpedienteSearch(generics.ListAPIView):
    serializer_class = ExpedienteSearchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        titulo_expediente = self.request.query_params.get('titulo_expediente', '').strip()
        codigo_exp_und_serie_subserie = self.request.query_params.get('codigo_exp_und_serie_subserie', '').strip()
        fecha_apertura_expediente = self.request.query_params.get('fecha_apertura_expediente', '').strip()
        id_serie_origen = self.request.query_params.get('id_serie_origen', '').strip()
        id_subserie_origen = self.request.query_params.get('id_subserie_origen', '').strip()
        palabras_clave_expediente = self.request.query_params.get('palabras_clave_expediente', '').strip()

        # Filtrar por atributos específicos referentes a un expediente (unión de parámetros)
        queryset = ExpedientesDocumentales.objects.filter(estado='A')  # Filtrar por estado 'A'
        if titulo_expediente:
            queryset = queryset.filter(titulo_expediente__icontains=titulo_expediente)

        if codigo_exp_und_serie_subserie:
            queryset = queryset.filter(codigo_exp_und_serie_subserie=codigo_exp_und_serie_subserie)

        if fecha_apertura_expediente:
            queryset = queryset.filter(fecha_apertura_expediente__icontains=fecha_apertura_expediente)

        if id_serie_origen:
            queryset = queryset.filter(id_serie_origen=id_serie_origen)

        if id_subserie_origen:
            queryset = queryset.filter(id_subserie_origen=id_subserie_origen)

        if palabras_clave_expediente:
            search_vector = SearchVector('palabras_clave_expediente')
            search_query = SearchQuery(palabras_clave_expediente)
            queryset = queryset.annotate(rank=SearchRank(search_vector, search_query)).filter(rank__gt=0)

        return queryset

        # queryset = queryset.order_by('orden_ubicacion_por_entidad')  # Ordenar de forma ascendente

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response({
                'success': True,
                'detail': 'No se encontraron datos que coincidan con los criterios de búsqueda.',
                'data': []
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = ExpedienteSearchSerializer(queryset, many=True)

        return Response({
            'success': True,
            'detail': 'Se encontraron los siguientes registros.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
