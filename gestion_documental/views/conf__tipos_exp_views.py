
from gestion_documental.models.ccd_models import CatalogosSeries, CatalogosSeriesUnidad
from gestion_documental.models.trd_models import CatSeriesUnidadOrgCCDTRD, TablaRetencionDocumental
from gestion_documental.serializers.conf__tipos_exp_serializers import CatalogosSeriesSecSubGetSerializer, SecSubUnidadOrgaGetSerializer, XXGetSerializer, XYGetSerializer
from seguridad.utils import Util

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied

import copy

from transversal.models.organigrama_models import UnidadesOrganizacionales
class ConfiguracionTipoExpedienteAgnoGet(generics.ListAPIView):
    serializer_class = SecSubUnidadOrgaGetSerializer
    queryset = TablaRetencionDocumental.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        
        
        trd_actual = TablaRetencionDocumental.objects.filter(actual=True).first()#T212TablasRetencionDoc
        catalogo_ids = CatSeriesUnidadOrgCCDTRD.objects.filter(id_trd=trd_actual).values_list('id_cat_serie_und', flat=True)#T218CatSeries_UndOrg_CCD_TRD
        
        catalogo_ids_list = list(catalogo_ids)
        
        catalogo_series_unidad= CatalogosSeriesUnidad.objects.filter(id_cat_serie_und__in=catalogo_ids_list).order_by('id_unidad_organizacional')

        unidades=[]
        
        for x in catalogo_series_unidad.distinct():
            
            unidad=x.id_unidad_organizacional
            
            if x.id_unidad_organizacional.cod_agrupacion_documental and x.id_unidad_organizacional.activo == True and x.id_unidad_organizacional.id_organigrama.actual == True :
   
                serializer = self.serializer_class(unidad)
                unidades.append(serializer.data)
        
        
        ids_unicas = set()
        #lista ordenada
        unidades_ordenadas = sorted(unidades, key=lambda x: x['id_unidad_organizacional'])
        # Lista para almacenar los datos de unidades únicos
        unidades_unicas = []

        # Iterar sobre los datos serializados y agregar solo los únicos
        for unidad in unidades_ordenadas:
            id_unidad = unidad['id_unidad_organizacional']
            if id_unidad not in ids_unicas:
                ids_unicas.add(id_unidad)
                unidades_unicas.append(unidad)
        
        return Response({'succes':True, 'detail':'Se encontraron los siguientes registros','data':unidades_unicas}, status=status.HTTP_200_OK)

class SerieSubserioUnidadGet(generics.ListAPIView):
    #erializer_class = CatalogosSeriesSecSubGetSerializer
    serializer_class = XYGetSerializer
    permission_classes = [IsAuthenticated]
    
    def get (self, request,uni):
        #CatalogosSeriesUnidad es forarena de CatSeriesUnidadOrgCCDTRD

        #instance=CatalogosSeriesUnidad.objects.filter(id_unidad_organizacional=uni).values_list('id_catalogo_serie', flat=True)#T218CatSeries_UndOrg_CCD_TRD
        instance=CatalogosSeriesUnidad.objects.filter(id_unidad_organizacional=uni)


        if not instance:
            raise NotFound("No existen registros asociados.")
        
        
        
       
        # catalogo_serie_unidad=CatSeriesUnidadOrgCCDTRD.objects.filter(id_cat_serie_und__in=instance)
        # for x in catalogo_serie_unidad:
        #     print((x))
        
        serializador=self.serializer_class(instance,many=True)

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializador.data}, status=status.HTTP_200_OK)
    