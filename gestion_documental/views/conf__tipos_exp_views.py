
from gestion_documental.models.ccd_models import CatalogosSeries, CatalogosSeriesUnidad
from gestion_documental.models.conf__tipos_exp_models import ConfiguracionTipoExpedienteAgno
from gestion_documental.models.trd_models import CatSeriesUnidadOrgCCDTRD, TablaRetencionDocumental
from gestion_documental.serializers.conf__tipos_exp_serializers import CatalogosSeriesSecSubGetSerializer, ConfiguracionTipoExpedienteAgnoCreateSerializer, SecSubUnidadOrgaGetSerializer, XXGetSerializer, XYGetSerializer
from seguridad.utils import Util
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from datetime import date
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
    #serializer_class = XYGetSerializer
    serializer_class = XXGetSerializer
    permission_classes = [IsAuthenticated]
    
    def get (self, request,uni):
        #CatalogosSeriesUnidad es forarena de CatSeriesUnidadOrgCCDTRD

        #instance=CatalogosSeriesUnidad.objects.filter(id_unidad_organizacional=uni).values_list('id_catalogo_serie', flat=True)#T218CatSeries_UndOrg_CCD_TRD
        instance=CatalogosSeriesUnidad.objects.filter(id_unidad_organizacional=uni)


        if not instance:
            raise NotFound("No existen registros asociados.")
        
        
        
       
        catalogo_serie_unidad=CatSeriesUnidadOrgCCDTRD.objects.filter(id_cat_serie_und__in=instance)
        # for x in catalogo_serie_unidad:
        #     print((x))
        
        #serializador=self.serializer_class(catalogo_serie_unidad,many=True)
        serializador=self.serializer_class(catalogo_serie_unidad,many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializador.data}, status=status.HTTP_200_OK)
    

class ConfiguracionTipoExpedienteAgnoCreate(generics.CreateAPIView):
    serializer_class = ConfiguracionTipoExpedienteAgnoCreateSerializer
    permission_classes = [IsAuthenticated]
    queryset = ConfiguracionTipoExpedienteAgno.objects.all()
    
    def post(self,request):    
        hoy = date.today()
        age = hoy.year 
        data_in = request.data

        if data_in['agno_expediente'] != age and data_in['agno_expediente'] != age+1:
            raise ValidationError('Solo se pueden crear configuraciones correspondientes a '+str(age)+' o '+str(age+1))
 
        
        if 'cod_tipo_expediente' in data_in and data_in['cod_tipo_expediente'] == 'C':
            if 'consecutivo_inicial' in data_in and data_in['consecutivo_inicial']:
                if data_in['consecutivo_inicial'] <=0:
                    raise ValidationError('El consecutivo inicial debe ser mayor a 0')
                data_in['consecutivo_actual']= data_in['consecutivo_inicial']-1
            else:
                raise ValidationError('Debe asigar un consecutivo inicial')
            if 'cantidad_digitos' in data_in and data_in['cantidad_digitos']:
                if data_in['cantidad_digitos'] > 20:
                    raise ValidationError('El numero de digitos debe ser menor o igual a 20.')
            else:
                raise ValidationError('Debe asigar un numero de digitos.')


        serializer = self.serializer_class(data=data_in)
        serializer.is_valid(raise_exception=True)
            
        instance=serializer.save()

        id_unidad=instance.id_cat_serie_undorg_ccd.id_cat_serie_und.id_unidad_organizacional.id_unidad_organizacional
        unidad_nombre=instance.id_cat_serie_undorg_ccd.id_cat_serie_und.id_unidad_organizacional.nombre
                    #AUDITORIA 
        if instance.agno_expediente == age:
                modulo=147
        if instance.agno_expediente == age+1:
                modulo=148

        usuario = request.user.id_usuario
        direccion=Util.get_client_ip(request)
        descripcion = {"IdUnidad":id_unidad,"Nombre":unidad_nombre}
        #valores_actualizados = {'current': instance, 'previous': instance_previous}
        auditoria_data = {
                "id_usuario" : usuario,
                "id_modulo" : modulo,
                "cod_permiso": "CR",
                "subsistema": 'GEST',
                "dirip": direccion,
                "descripcion": descripcion, 
               
            }
        Util.save_auditoria(auditoria_data) 
        return Response({'success':True,'detail':'Se crearon los registros correctamente','data':serializer.data},status=status.HTTP_201_CREATED)
    
class ConfiguracionTipoExpedienteAgnoUpdate(generics.UpdateAPIView):
    serializer_class = ConfiguracionTipoExpedienteAgnoCreateSerializer
    queryset = ConfiguracionTipoExpedienteAgno.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self,request,pk):
    
        try:
            hoy = date.today()
            age = hoy.year
            fecha_actual=datetime.now()
   
          
            data = request.data
            instance = ConfiguracionTipoExpedienteAgno.objects.filter(id_config_tipo_expediente_agno=pk).first()
            
            if not instance:
                raise NotFound("No se existe un registro con este codigo.")
            
            if instance.item_ya_usado:
                raise ValidationError("No se puede modificar una configuracion que ya este en uso.")
            

            if age != instance.agno_expediente and (age+1) != instance.agno_expediente:
                raise ValidationError("No se puede editar una configuracion antigua.")
            if 'cod_tipo_expediente' in data and data['cod_tipo_expediente'] == 'C':
                if 'consecutivo_inicial' in data and data['consecutivo_inicial']:
                    if data['consecutivo_inicial'] <=0:
                        raise ValidationError('El consecutivo inicial debe ser mayor a 0')
                    data['consecutivo_actual']= data['consecutivo_inicial']-1
                else:
                    raise ValidationError('Debe asigar un consecutivo inicial')
                if 'cantidad_digitos' in data and data['cantidad_digitos']:
                    if data['cantidad_digitos'] > 20:
                        raise ValidationError('El numero de digitos debe ser menor o igual a 20.')
                else:
                    raise ValidationError('Debe asigar un numero de digitos.')
            data['fecha_ult_config_implement']=fecha_actual
            instance_previous=copy.copy(instance)
            serializer = self.serializer_class(instance,data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            
            intance=serializer.save()
            id_unidad=instance.id_cat_serie_undorg_ccd.id_cat_serie_und.id_unidad_organizacional.id_unidad_organizacional
            unidad_nombre=instance.id_cat_serie_undorg_ccd.id_cat_serie_und.id_unidad_organizacional.nombre
   
            #nombre
            
            #AUDITORIA 
            if instance.agno_expediente == age:
                modulo=147
            if instance.agno_expediente == age+1:
                modulo=148

            usuario = request.user.id_usuario
            direccion=Util.get_client_ip(request)
            descripcion = {"IdUnidad":id_unidad,"Nombre":unidad_nombre}
            valores_actualizados = {'current': instance, 'previous': instance_previous}
            auditoria_data = {
                    "id_usuario" : usuario,
                    "id_modulo" : modulo,
                    "cod_permiso": "AC",
                    "subsistema": 'GEST',
                    "dirip": direccion,
                    "descripcion": descripcion, 
                    "valores_actualizados": valores_actualizados
                }
            Util.save_auditoria(auditoria_data) 

            return Response({'success':True,'detail':"Se actualizo la actividad Correctamente.","data":serializer.data},status=status.HTTP_200_OK)
        
        except ValidationError  as e:
            error_message = {'error': e.detail}
            raise ValidationError  (e.detail) 
        

class ConfiguracionTipoExpedienteAgnoGetbyCatalogoUnidad(generics.ListAPIView):
    #erializer_class = CatalogosSeriesSecSubGetSerializer
    #serializer_class = XYGetSerializer
    serializer_class = ConfiguracionTipoExpedienteAgnoCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def get (self, request,uni,agno):
        hoy = date.today()
        age = hoy.year

        if agno=='sig':
            age=age+1
        #CatalogosSeriesUnidad es forarena de CatSeriesUnidadOrgCCDTRD

        #instance=CatalogosSeriesUnidad.objects.filter(id_unidad_organizacional=uni).values_list('id_catalogo_serie', flat=True)#T218CatSeries_UndOrg_CCD_TRD
        instance=ConfiguracionTipoExpedienteAgno.objects.filter(id_cat_serie_undorg_ccd=uni,agno_expediente=age)


        if not instance:
            raise NotFound("No existen registros asociados.")
        
        serializador=self.serializer_class(instance,many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializador.data}, status=status.HTTP_200_OK)
    


class ConfiguracionTipoExpedienteAgnoGetHistorico(generics.ListAPIView):

    serializer_class = ConfiguracionTipoExpedienteAgnoCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def get (self, request,uni,agno):
       
  

    
        instance=ConfiguracionTipoExpedienteAgno.objects.filter(id_cat_serie_undorg_ccd=uni,agno_expediente=agno)


        if not instance:
            raise NotFound("No existen registros asociados.")
        
        serializador=self.serializer_class(instance,many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializador.data}, status=status.HTTP_200_OK)
    
