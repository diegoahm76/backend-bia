from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from gestion_documental.models.ccd_models import CatalogosSeriesUnidad
from gestion_documental.models.ctrl_acceso_models import CtrlAccesoClasificacionExpCCD
from gestion_documental.models.expedientes_models import ArchivosDigitales
from gestion_documental.models.permisos_models import PermisosUndsOrgActualesSerieExpCCD
from gestion_documental.models.plantillas_models import AccesoUndsOrg_PlantillaDoc, PlantillasDoc
from gestion_documental.models.tca_models import TablasControlAcceso
from gestion_documental.models.trd_models import CatSeriesUnidadOrgCCDTRD, FormatosTiposMedio, TablaRetencionDocumental, TipologiasDoc
from gestion_documental.serializers.ctrl_acceso_serializers import CtrlAccesoGetSerializer
from gestion_documental.serializers.permisos_serializers import DenegacionPermisosGetSerializer
from gestion_documental.serializers.plantillas_serializers import AccesoUndsOrg_PlantillaDocCreateSerializer, AccesoUndsOrg_PlantillaDocGetSerializer, OtrasTipologiasSerializerGetSerializer, PlantillasDocBusquedaAvanzadaDetalleSerializer, PlantillasDocBusquedaAvanzadaSerializer, PlantillasDocCreateSerializer, PlantillasDocGetSeriallizer, PlantillasDocSerializer, PlantillasDocUpdateSerializer, TipologiasDocSerializerGetSerializer
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
import os
from rest_framework.permissions import IsAuthenticated
import json
from gestion_documental.serializers.trd_serializers import DenegacionPermisosGetUnidadSerializer, PermisosUndsOrgActualesSerieExpCCDSerializer, SerieSubserieReporteSerializer, TablaRetencionDocumentalPermisosGetsSerializer, UnidadSeccionSubseccionGetSerializer
from gestion_documental.views.archivos_digitales_views import ArchivosDgitalesCreate
from gestion_documental.views.ctrl_acceso_views import CtrlAccesoGetView
from gestion_documental.views.permisos_views import DenegacionPermisosGetView, UnidadesExternasPermisosGetView
from transversal.models.organigrama_models import UnidadesOrganizacionales
from urllib.parse import urlencode
#TablaRetencionDocumental
class TRDCCDOrganigramaGet(generics.ListAPIView):
    serializer_class = TablaRetencionDocumentalPermisosGetsSerializer
    queryset = TablaRetencionDocumental.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        
                
        #intance = self.queryset.all().filter(id_plantilla_doc=pk)
        intance = TablaRetencionDocumental.objects.filter(fecha_puesta_produccion__isnull=False)
        # for i in intance:
        #     tca = TablasControlAcceso.objects.filter(id_trd=i.id_trd)  
            #print(tca)

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

        unidades = set()  # Usamos un conjunto para garantizar elementos únicos

        for x in catalogo_series_unidad.distinct():
            unidad = x.id_unidad_organizacional
            if unidad.cod_agrupacion_documental:
                serializer = self.serializer_class(unidad)
                unidades.add(tuple(serializer.data.items()))  # Agregamos la tupla a 'unidades'

        # Ahora 'unidades' contiene datos únicos

        # Convertimos 'unidades' de conjunto a lista para la respuesta
        unidades_unicas = [dict(item) for item in unidades]

        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros.', 'data': unidades_unicas}, status=status.HTTP_200_OK)
        
    

#PermisosUndsOrgActualesSerieExpCCD
class ReportePermisosUndsOrgActualesSerieExpCCDGet(generics.ListAPIView):
    serializer_class = PermisosUndsOrgActualesSerieExpCCDSerializer
    serializer_serie_subserie = SerieSubserieReporteSerializer
    serializer_class_seccion_subseccion = UnidadSeccionSubseccionGetSerializer
    queryset = PermisosUndsOrgActualesSerieExpCCD.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,cat):
        #nstance = CatalogosSeriesUnidad.objects.filter(id_unidad_organizacional=cat).values_list('id_cat_serie_und', flat=True)
        instance2 = CatalogosSeriesUnidad.objects.filter(id_unidad_organizacional=cat)
        unidad = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional=cat).first()
        if not unidad:
            raise NotFound("No existen registros asociados.")
        if not instance2:
            raise NotFound("No existen registros asociados.")
        data_unidad = self.serializer_class_seccion_subseccion(unidad).data
        dic = {}
        data = []
        for x in instance2:
            dic = {}
            print(x.id_catalogo_serie.id_serie_doc)
            #data.append()
            permisos = PermisosUndsOrgActualesSerieExpCCD.objects.filter(id_cat_serie_und_org_ccd=x)
           
            dic['serie_subserie'] = self.serializer_serie_subserie(x.id_catalogo_serie,many=False).data
            dic['permisos'] = self.serializer_class(permisos,many=True).data
            data.append(dic)
        
        # if not instance:
        #     raise NotFound("No existen registros asociados.")
        #raise ValidationError("SI")
        
        return Response({'success':True,'detail':'Se encontraron los siguientes registros.','data':{'unidad':data_unidad,'series':data}},status=status.HTTP_200_OK)
    

# class DenegacionPermisosGetByUnidadView(generics.ListAPIView):
#     serializer_class = DenegacionPermisosGetUnidadSerializer 
#     queryset = PermisosUndsOrgActualesSerieExpCCD.objects.filter()
#     permission_classes = [IsAuthenticated]
    
#     def get(self, request, uni):
#         data=[]
#         catalogos = CatalogosSeriesUnidad.objects.filter(id_unidad_organizacional=uni)
#         #print(catalogos)
#         for  cat in catalogos:
#             print(cat)
#             serializador = None
            
#             denegacion_permisos = self.queryset.filter(id_cat_serie_und_org_ccd=cat.id_cat_serie_und, id_und_organizacional_actual=None).first()
#             serializador = self.serializer_class(denegacion_permisos)
#             data.append(serializador.data)
#         return Response({'succes': True, 'detail':'Resultados encontrados', 'data':data}, status=status.HTTP_200_OK)
    
class PermisosExpedientesNoPropios(generics.ListAPIView):
    serializer_class = DenegacionPermisosGetSerializer
    queryset = PermisosUndsOrgActualesSerieExpCCD.objects.filter()
    permission_classes = [IsAuthenticated]
    serializer_serie_subserie = SerieSubserieReporteSerializer


    def denegaciones(self, id_cat_serie_und):
        denegacion_permisos = self.queryset.filter(id_cat_serie_und_org_ccd=id_cat_serie_und, id_und_organizacional_actual=None).first()
        #print(denegacion_permisos)
        if not denegacion_permisos:
            return None
        serializador = self.serializer_class(denegacion_permisos)
        return serializador.data
    




    
    def get(self, request, uni):
        instance2 = CatalogosSeriesUnidad.objects.filter(id_unidad_organizacional=uni)

        permisos = UnidadesExternasPermisosGetView()
        
        data=[]
        for x in instance2:
            
            response = permisos.get( request, x.id_cat_serie_und)
            data_permisos = []
            for aux in response.data['data']:
               if aux['id_permisos_und_org_actual_serie_exp_ccd']:
                   data_permisos.append(aux)
            data_denegacion = {}
            #raise ValidationError("QUE TALLL")
            respuesta = self.denegaciones(x.id_cat_serie_und)
            if respuesta:
                data_denegacion = respuesta
            #print(datos_denegacion)
            #print('$$$$')
            
            #print(response_permisos.data['data'])
            if data_denegacion and len(data_permisos) >= 0:

                data.append({
                    'catalogo':self.serializer_serie_subserie(x.id_catalogo_serie,many=False).data,
                    'permisos':data_permisos,
                    'denegacion':data_denegacion
                    })
        return Response({'succes': True, 'detail':'Resultados encontrados', 'data':data}, status=status.HTTP_200_OK)
    
class PermisosDenegacion(generics.ListAPIView):
    serializer_class = CtrlAccesoGetSerializer 
    serializer_serie_subserie = SerieSubserieReporteSerializer
    queryset = CtrlAccesoClasificacionExpCCD.objects.filter()
    permission_classes = [IsAuthenticated]

    def get(self, request,ccd,uni):
        id_ccd =ccd
        id_unidad = uni
        data = {}
        data_xclu=[]
        if id_ccd == '':
            raise ValidationError('Debe enviar el CCD seleccionado')
        catalogos = CatalogosSeriesUnidad.objects.filter(id_unidad_organizacional=uni)

        if not catalogos:
            raise NotFound("No existen registros asociados.")
        
        for x in catalogos:
            info = {}
            info['catalogo']=(self.serializer_serie_subserie(x.id_catalogo_serie,many=False).data)
            deneg = CtrlAccesoClasificacionExpCCD.objects.filter(id_cat_serie_und_org_ccd=x.id_cat_serie_und)
            data_denegacion = self.serializer_class(deneg,many=True)
            info['exclusiones'] = data_denegacion.data
            data_xclu.append(info)
        ctrl_acceso = self.queryset.filter(id_ccd=id_ccd, cod_clasificacion_exp__isnull=False)
        # elif id_cat_serie_und:
        #     ctrl_acceso = self.queryset.filter(id_ccd=id_ccd, id_cat_serie_und_org_ccd=id_cat_serie_und)
        # else:
        #     ctrl_acceso = self.queryset.filter(id_ccd=id_ccd)
        
        serializador = self.serializer_class(ctrl_acceso, many=True)
        data['permisos_acceso_clasificacion'] = serializador.data
        data['exclusiones'] = data_xclu
        return Response({'succes': True, 'detail':'Resultados encontrados', 'data':data}, status=status.HTTP_200_OK)