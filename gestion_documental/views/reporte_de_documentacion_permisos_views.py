from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from gestion_documental.models.ccd_models import CatalogosSeriesUnidad
from gestion_documental.models.expedientes_models import ArchivosDigitales
from gestion_documental.models.plantillas_models import AccesoUndsOrg_PlantillaDoc, PlantillasDoc
from gestion_documental.models.tca_models import TablasControlAcceso
from gestion_documental.models.trd_models import CatSeriesUnidadOrgCCDTRD, FormatosTiposMedio, TablaRetencionDocumental, TipologiasDoc
from gestion_documental.serializers.plantillas_serializers import AccesoUndsOrg_PlantillaDocCreateSerializer, AccesoUndsOrg_PlantillaDocGetSerializer, OtrasTipologiasSerializerGetSerializer, PlantillasDocBusquedaAvanzadaDetalleSerializer, PlantillasDocBusquedaAvanzadaSerializer, PlantillasDocCreateSerializer, PlantillasDocGetSeriallizer, PlantillasDocSerializer, PlantillasDocUpdateSerializer, TipologiasDocSerializerGetSerializer
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
import os
from rest_framework.permissions import IsAuthenticated
import json
from gestion_documental.serializers.trd_serializers import TablaRetencionDocumentalPermisosGetsSerializer, UnidadSeccionSubseccionGetSerializer
from gestion_documental.views.archivos_digitales_views import ArchivosDgitalesCreate
from transversal.models.organigrama_models import UnidadesOrganizacionales

#TablaRetencionDocumental
class TRDCCDOrganigramaGet(generics.ListAPIView):
    serializer_class = TablaRetencionDocumentalPermisosGetsSerializer
    queryset = TablaRetencionDocumental.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        
                
        #intance = self.queryset.all().filter(id_plantilla_doc=pk)
        intance = TablaRetencionDocumental.objects.filter(fecha_puesta_produccion__isnull=False)
        for i in intance:
            tca = TablasControlAcceso.objects.filter(id_trd=i.id_trd)  
            print(tca)

        serializador = self.serializer_class(intance,many=True)
        
        return Response({'success':True,'detail':'Se encontraron los siguientes registros.','data':serializador.data},status=status.HTTP_200_OK)
        

class UnidadesSeccionSubseccionGet(generics.ListAPIView):
    serializer_class = UnidadSeccionSubseccionGetSerializer
    queryset = TablaRetencionDocumental.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,trd):
        
        
        
        catalogo_ids = CatSeriesUnidadOrgCCDTRD.objects.filter(id_trd=trd).values_list('id_cat_serie_und', flat=True)#T218CatSeries_UndOrg_CCD_TRD
        
        catalogo_ids_list = list(catalogo_ids)
        
        catalogo_series_unidad= CatalogosSeriesUnidad.objects.filter(id_cat_serie_und__in=catalogo_ids_list).order_by('id_unidad_organizacional')

        # unidades=[]
        
        # for x in catalogo_series_unidad.distinct():
            
        #     unidad=x.id_unidad_organizacional

        #     serializer = self.serializer_class(unidad)
        #     unidades.append(serializer.data)
        serializer = self.serializer_class(catalogo_series_unidad,many=True)
        return Response({'success':True,'detail':'Se encontraron los siguientes registros.','data':serializer.data},status=status.HTTP_200_OK)