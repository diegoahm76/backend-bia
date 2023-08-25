from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from gestion_documental.serializers.permisos_serializers import SerieSubserieUnidadCCDGetSerializer
from seguridad.utils import Util
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from django.db.models.functions import Cast
from django.db.models import BigIntegerField
from gestion_documental.serializers.ccd_serializers import (
    CCDPostSerializer,
    CCDPutSerializer,
    CCDActivarSerializer,
    CCDSerializer,
    CatalogoSerieSubserieSerializer,
    SeriesDocPostSerializer,
    SeriesDocPutSerializer,
    SubseriesDocPostSerializer,
    SubseriesDocPutSerializer,
    CatalogosSeriesUnidadSerializer,
    AsignacionesCatalogosOrgSerializer,
    BusquedaCCDSerializer
)
from transversal.models.organigrama_models import Organigramas
from gestion_documental.models.ccd_models import (
    CuadrosClasificacionDocumental,
    SeriesDoc,
    SubseriesDoc,
    CatalogosSeries,
    CatalogosSeriesUnidad
)
from transversal.models.organigrama_models import (
    UnidadesOrganizacionales
)
from gestion_documental.models.trd_models import (
    TablaRetencionDocumental
)

import copy

from transversal.serializers.organigrama_serializers import UnidadesGetSerializer

class BusquedaCCDPermisosGetView(generics.ListAPIView):
    serializer_class = BusquedaCCDSerializer 
    queryset = CuadrosClasificacionDocumental.objects.filter(Q(actual=True) | (Q(actual=False) & ~Q(fecha_retiro_produccion=None)))
    permission_classes = [IsAuthenticated]

    def get (self, request):
        filter={}
        for key, value in request.query_params.items():
            if key in ['nombre','version']:
                if value != '':
                    filter[key+'__icontains'] = value
        
        ccd = self.queryset.filter(**filter).order_by('fecha_terminado')
        serializador = self.serializer_class(ccd, many=True, context = {'request':request})
        return Response({'succes': True, 'detail':'Resultados de la búsqueda', 'data':serializador.data}, status=status.HTTP_200_OK)
    
class UnidadesCCDGetView(generics.ListAPIView):
    serializer_class = UnidadesGetSerializer 
    queryset = UnidadesOrganizacionales.objects.filter()
    permission_classes = [IsAuthenticated]

    def get (self, request, id_organigrama):
        nombre = request.query_params.get('nombre', '')
        unidades_org = self.queryset.filter(nombre__icontains=nombre, id_organigrama=id_organigrama).exclude(cod_agrupacion_documental=None)
        serializador = self.serializer_class(unidades_org, many=True)
        return Response({'succes': True, 'detail':'Resultados encontrados', 'data':serializador.data}, status=status.HTTP_200_OK)
    
class SerieSubserieUnidadCCDGetView(generics.ListAPIView):
    serializer_class = SerieSubserieUnidadCCDGetSerializer 
    queryset = CatalogosSeriesUnidad.objects.filter()
    permission_classes = [IsAuthenticated]

    def get (self, request):
        id_ccd = request.query_params.get('id_ccd', '')
        id_unidad_organizacional = request.query_params.get('id_unidad_organizacional', '')
        
        if id_ccd == '' or id_unidad_organizacional == '':
            raise ValidationError('Debe enviar el CCD y la Unidad Organizacional seleccionada')
        
        catalogos_serie_unidad = self.queryset.filter(id_catalogo_serie__id_serie_doc__id_ccd=id_ccd, id_unidad_organizacional=id_unidad_organizacional)
        serializador = self.serializer_class(catalogos_serie_unidad, many=True)
        return Response({'succes': True, 'detail':'Resultados encontrados', 'data':serializador.data}, status=status.HTTP_200_OK)

class UnidadesHijasCCDGetView(generics.ListAPIView):
    serializer_class = UnidadesGetSerializer 
    queryset = UnidadesOrganizacionales.objects.filter()
    permission_classes = [IsAuthenticated]
    
    def get_family(self, unidades_hijas):
        unidades_family = []
        for unidad in unidades_hijas:
            hijas = self.queryset.filter(id_unidad_org_padre=unidad.id_unidad_organizacional, cod_agrupacion_documental=None, activo=True)
            if hijas:
                hijas_serializer = self.serializer_class(hijas, many=True)
                unidades_family = unidades_family + hijas_serializer.data
                unidades_inner = self.get_family(hijas)
                unidades_family = unidades_family + unidades_inner
                print(unidades_family)
        return unidades_family

    def get(self, request, id_unidad_organizacional):
        unidades_org = self.queryset.filter(id_unidad_org_padre=id_unidad_organizacional, cod_agrupacion_documental=None, activo=True)
        # unidades_org = list(unidades_org) if unidades_org else []
        serializador = self.serializer_class(unidades_org, many=True)
        unidades_org_data = serializador.data
        unidades_family = self.get_family(unidades_org)
        unidades_family = unidades_org_data + unidades_family
        # PENDIENTE VALIDACION SI TIENEN PERMISOS
        return Response({'succes': True, 'detail':'Resultados encontrados', 'data':unidades_family}, status=status.HTTP_200_OK)