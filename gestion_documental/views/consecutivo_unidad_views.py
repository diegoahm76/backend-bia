import copy

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from gestion_documental.models.ccd_models import CatalogosSeriesUnidad
from gestion_documental.models.consecutivo_unidad_models import ConfigTipoConsecAgno, Consecutivo
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from datetime import date
from gestion_documental.serializers.consecutivo_unidad_serializers import CatalogosSeriesUnidadGetSerializer, ConfigTipoConsecAgnoCreateSerializer, ConfigTipoConsecAgnoGetSerializer, ConfigTipoConsecAgnoPutConSerializer, ConsecutivoCreateSerializer, ConsecutivoGetSerializer,UnidadesGetSerializer
from django.utils import timezone
from seguridad.models import Personas
from seguridad.utils import Util
from transversal.models.organigrama_models import Organigramas, UnidadesOrganizacionales
from datetime import datetime, date, timedelta


class UnidadesOrganigramaActualGet(generics.ListAPIView):
    serializer_class = UnidadesGetSerializer
    queryset = UnidadesOrganizacionales.objects.all()

    def get(self, request):
        organigrama = Organigramas.objects.filter(actual=True)
        if not organigrama:
            raise NotFound('No existe ningún organigrama activado')
        if len(organigrama) > 1:
            raise PermissionDenied('Existe más de un organigrama actual, contacte a soporte')
        
        organigrama_actual = organigrama.first()
        unidades_organigrama_actual = UnidadesOrganizacionales.objects.filter(id_organigrama=organigrama_actual.id_organigrama)
        serializer = self.serializer_class(unidades_organigrama_actual, many=True)
        return Response({'success':True, 'detail':'Consulta Exitosa', 'data': serializer.data}, status=status.HTTP_200_OK)

class ConfigTipoConsecAgnoGetView(generics.ListAPIView):
    serializer_class = ConfigTipoConsecAgnoGetSerializer
    permission_classes = [IsAuthenticated]
    queryset = ConfigTipoConsecAgno.objects.all()
    
    def get(self, request,agno,uni):
        instance = self.get_queryset().filter(agno_consecutivo=agno,id_unidad=uni).first()



        if not instance:
            raise NotFound('No existe registro')
        
        serializer = self.serializer_class(instance)
        
        return Response({'success':True, 'detail':'se encontraron los siguientes registros', 'data': serializer.data}, status=status.HTTP_200_OK)


class ConfigTipoConsecAgnoCreateView(generics.CreateAPIView):
    serializer_class = ConfigTipoConsecAgnoCreateSerializer
    permission_classes = [IsAuthenticated]

    def crear_config_tipos_consecutivo_agno(self, data):
        data_in = data
        hoy = date.today()
        age = hoy.year
        print(age)
        print(age+1)
        #print(data_in['agno_radicado'])
        if 'agno_consecutivo' in data_in:
            if data_in['agno_consecutivo']!= age and  data_in['agno_consecutivo']!= (age+1):
                raise ValidationError("El año debe ser el actual o el siguiente")
        else:
            raise ValidationError("El año del consecutivo es requerido")
        
        if 'implementar' in data_in and data_in['implementar']:

           
   
            consecutivo_inicial = data.get('consecutivo_inicial')
            cantidad_digitos = data.get('cantidad_digitos')


            if consecutivo_inicial is None:
                raise ValidationError("Se debe asignar un consecutivo inicial.")

            if cantidad_digitos is None:
                raise ValidationError("Se deben asignar una cantidad de dígitos.")

            if cantidad_digitos <= 0:
                raise ValidationError("La cantidad de dígitos debe ser mayor a cero.")
            
            data_in['id_persona_config_implementacion']=data_in['user']
            data_in['fecha_inicial_config_implementacion'] = timezone.now()
            data_in['consecutivo_actual'] = consecutivo_inicial-1
   
            if 'cantidad_digitos' in data_in and data_in['cantidad_digitos']:
                if data_in['cantidad_digitos'] > 20:
                    raise ValidationError('La cantidad de digitos no puede ser mayor a 20')

            
        print(data_in)
        serializer = ConfigTipoConsecAgnoCreateSerializer(data=data_in)
        serializer.is_valid(raise_exception=True)
        serializer.save()

            # id_modulo=0
            # if instance.agno_radicado==age:
            #     id_modulo=143
            # elif instance.agno_radicado==age+1:
            #     id_modulo=144

            # descripcion = {"AgnoRadicado":instance.agno_radicado,"CodTipoRadicado":instance.cod_tipo_radicado}
            # auditoria_data = {
            # "id_usuario" : data_in['user'],
            # "id_modulo" : id_modulo,
            # "cod_permiso": "CR",
            # "subsistema": 'GEST',
            # "dirip": data_in['direccion'],
            # "descripcion": descripcion, 
            # }
            # Util.save_auditoria(auditoria_data)
        print(serializer.data)
        #raise ValidationError("Se implementó correctamente")

        return Response({
                'success': True,
                'detail': 'Se creó la configuración de los consecutivos correctamente.',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)




    def post(self, request, *args, **kwargs):
        data_in = request.data
        usuario = request.user.persona.id_persona
        data_in['user'] = usuario #id_persona_config_implementacion
        data_in['direccion']=Util.get_client_ip(request)
        #data_in['fecha_inicial_config_implementacion'] = timezone.now()
        response = self.crear_config_tipos_consecutivo_agno(data_in)
        return response



class ConfigTiposConsecutivoAgnoUpdate(generics.UpdateAPIView):
    serializer_class = ConfigTipoConsecAgnoCreateSerializer
    queryset = ConfigTipoConsecAgno.objects.all()
    permission_classes = [IsAuthenticated]

    def actualizar_config_tipos_consecutivo_agno(self,data,pk):
        
        data_in=data
        hoy = date.today()
        age=hoy.year
        # Obtener la instancia existente para actualizar
        instance =ConfigTipoConsecAgno.objects.filter(id_config_tipo_consec_agno=pk).first()

        # Verificar si la instancia existe
        if not instance:
            return Response({'detail': 'La configuracion no existe.'}, status=status.HTTP_404_NOT_FOUND)
        
        previous=copy.copy(instance)
        if instance.implementar and instance.agno_consecutivo==age:
            raise ValidationError('No se puede modificar la configuracion de un consecutivo si se esta implementando actualmente.')
        if instance.agno_consecutivo < age:
            raise ValidationError('No se puede modificar la configuracion de un consecutivo si es de un año anterior.')
        if 'implementar' in data_in:

            if data_in['implementar']==False and instance.implementar:
                
                 data_in['consecutivo_inicial']=None
                 data_in['cantidad_digitos']=None
            elif data_in['implementar']==True:

              
                #raise ValidationError("No se puede implementar la configuracion si ya esta vigente una de tipo unica")
              
                consecutivo_inicial = data.get('consecutivo_inicial')
                cantidad_digitos = data.get('cantidad_digitos')
                
                # Validar campos almacenados en la instancia actual

                if consecutivo_inicial is None:
                    consecutivo_inicial = instance.consecutivo_inicial
                    
                if cantidad_digitos is None:
                    cantidad_digitos = instance.cantidad_digitos

                
                if consecutivo_inicial  is None:
                    raise ValidationError("Se debe asignar un consecutivo inicial.")
                
                if cantidad_digitos is None:
                    raise ValidationError("se deben asignar una cantidad de digitos.")
                
                if cantidad_digitos <= 0:
                    raise ValidationError("se debe ser mayor a cero.")
                data_in['fecha_inicial_config_implementacion']= timezone.now()
                data_in['id_persona_config_implementacion']=data_in['user']

     

        if 'consecutivo_inicial' in data_in:
            if data_in['consecutivo_inicial']:
                data_in['consecutivo_actual']=data_in['consecutivo_inicial']-1
        if 'cantidad_digitos' in data_in and data_in['cantidad_digitos']:
            if data_in['cantidad_digitos'] > 20:
                raise ValidationError('La cantidad de digitos no puede ser mayor a 20')

        
        serializer =ConfigTipoConsecAgnoCreateSerializer(instance, data=data_in, partial=True)
        serializer.is_valid(raise_exception=True)
        
        serializer.save()

            # direccion=data_in['direccion']
            # descripcion = {"AgnoRadicado":instance.agno_radicado,"CodTipoRadicado":instance.cod_tipo_radicado}
            
            # valores_actualizados = {'current': instance, 'previous': previous}
            # #print(valores_actualizados)
            # id_modulo=0
            # if instance.agno_radicado==age:
            #     id_modulo=143
            # elif instance.agno_radicado==age+1:
            #     id_modulo=144
            # auditoria_data = {
            #     "id_usuario" : data_in['user'],
            #     "id_modulo" : id_modulo,
            #     "cod_permiso": "AC",
            #     "subsistema": 'GEST',
            #     "dirip": direccion,
            #     "descripcion": descripcion, 
            #     "valores_actualizados": valores_actualizados
            # }
            # Util.save_auditoria(auditoria_data) 


        # Respuesta exitosa con los datos actualizados
        return Response({
            'success': True,
            'detail': 'Se actualizó la configuracion de los  consecutivos correctamente.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def put(self, request, pk):
        data_in = request.data
        usuario = request.user.persona.id_persona
        #direccion=#
        data_in['user']=usuario#id_persona_config_implementacion
        data_in['direccion']=Util.get_client_ip(request)
        response= self.actualizar_config_tipos_consecutivo_agno(data_in,pk)
        return response
    




class ConfigTiposRadicadoAgnoGenerarN(generics.UpdateAPIView):
    serializer_class = ConfigTipoConsecAgnoPutConSerializer
    queryset = ConfigTipoConsecAgno.objects.all()
    permission_classes = [IsAuthenticated]
    vista_creacion_configuracion = ConfigTipoConsecAgnoCreateView()
    def generar_n_radicado(self,data):
        
        data_in=data
        print(data_in)
        hoy = date.today()
        age=hoy.year
        # # Obtener la instancia existente para actualizar
        instance =ConfigTipoConsecAgno.objects.filter(agno_consecutivo=age,id_unidad=data_in['id_unidad'], id_catalogo_serie_unidad = data_in['id_cat_serie_und']).first()

        if not instance:
           

            
            auxiliar = ConfigTipoConsecAgno.objects.filter(id_unidad=data_in['id_unidad'],agno_consecutivo=age, id_catalogo_serie_unidad = data_in['id_cat_serie_und']).first()
            if not auxiliar:
                conf_agno_anterior = ConfigTipoConsecAgno.objects.filter(agno_consecutivo=age-1).first()
                if not conf_agno_anterior:
                    raise ValidationError("No se encontro la configuracion.")
              
                nueva_configuracion = {
                                    'user':None,
                                    'direccion' : data_in['direccion'],
                                    'agno_consecutivo':age,
                                    'consecutivo_inicial':1,
                                    'cantidad_digitos':conf_agno_anterior.cantidad_digitos,
                                    'implementar':conf_agno_anterior.implementar,
                                    'id_cat_serie_und': conf_agno_anterior.id_cat_serie_und,
                                    'id_unidad':conf_agno_anterior.id_unidad
                                    }
                respuesta = self.vista_creacion_configuracion.crear_config_tipos_consecutivo_agno(nueva_configuracion)
                if respuesta.status_code != status.HTTP_201_CREATED:
                    return respuesta

            instance =ConfigTipoConsecAgno.objects.filter(agno_consecutivo=age,id_unidad=data_in['id_unidad'], id_catalogo_serie_unidad = data_in['id_cat_serie_und']).first()

        if not instance.implementar:
            raise ValidationError("La configuracion se encuentra pendiente")


        new_data={}
        new_data['consecutivo_actual'] = instance.consecutivo_actual+1
        new_data['id_persona_consecutivo_actual'] = data_in['id_persona']
        new_data['fecha_consecutivo_actual'] = data_in['fecha_actual']
       ##new_data['id_catalogo'] = data_in['id_cat_serie_und']
         
        serializer =ConfigTipoConsecAgnoPutConSerializer(instance, data=new_data, partial=True)
        serializer.is_valid(raise_exception=True)

        ##buscamos los catalogos de serie subserie de la unidad 
        cod_se_sub = ""
        if 'id_cat_serie_und' in data_in:
            catalogos_unidad=CatalogosSeriesUnidad.objects.filter(id_cat_serie_und=data_in['id_cat_serie_und']).first()
            cod_serie = catalogos_unidad.id_catalogo_serie.id_serie_doc.codigo
            cod_se_sub = cod_serie
            if catalogos_unidad.id_catalogo_serie.id_subserie_doc:
                cod_subserie =catalogos_unidad.id_catalogo_serie.id_subserie_doc.codigo
                cod_se_sub = cod_serie+'.'+cod_subserie
 
            
            
        instance = serializer.save()
        print('Holaaaa'+str(instance.id_catalogo_serie_unidad))
        numero_con_ceros = str(instance.consecutivo_actual).zfill(instance.cantidad_digitos)
        if cod_se_sub != "":

            conseg_nuevo = instance.id_unidad.codigo+'.'+cod_se_sub+'.'+str(instance.agno_consecutivo)[-2:]+'.'+numero_con_ceros
        else:
            conseg_nuevo = instance.id_unidad.codigo+'.'+str(instance.agno_consecutivo)[-2:]+'.'+numero_con_ceros
        
        #raise ValidationError("siu generando radicado")
        
        return Response({
            'success': True,
            'detail': 'Se actualizó la configuracion de los  consecutivos correctamente.',
            'data': {**serializer.data,'conseg_nuevo':conseg_nuevo}
        }, status=status.HTTP_200_OK)

    def put(self, request):
        data_in = request.data
        usuario = request.user.persona.id_persona
        #direccion=#
        data_in['user']=usuario#id_persona_config_implementacion
        data_in['direccion']=Util.get_client_ip(request)
        response= self.generar_n_radicado(data_in,)
        return response
    



class SerieSubserioUnidadGet(generics.ListAPIView):

    serializer_class = CatalogosSeriesUnidadGetSerializer
    permission_classes = [IsAuthenticated]
    
    def get (self, request,uni):

        instance=CatalogosSeriesUnidad.objects.filter(id_unidad_organizacional=uni)

        if not instance:
            raise NotFound("No existen registros asociados.")
        
    
        serializador=self.serializer_class(instance,many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializador.data}, status=status.HTTP_200_OK)


class ConsecutivoGetView(generics.ListAPIView):
    serializer_class = ConsecutivoGetSerializer
    permission_classes = [IsAuthenticated]
    queryset = Consecutivo.objects.all()
    
    def get (self, request):


        filter={}
        
        
        for key, value in request.query_params.items():

            # if key == 'radicado':
            #     if value !='':
            #         filter['mezcla__icontains'] = value
            if key =='unidad':
                if value != '':
                    filter['id_unidad__nombre__icontains'] = value    
            if key == 'agno':
                if value != '':
                     filter['agno_consecutivo__icontains'] = value   

            if key == 'fecha_inicio':
                if value != '':
                    
                    filter['fecha_consecutivo__gte'] = datetime.strptime(value, '%Y-%m-%d').date()
            if key == 'fecha_fin':
                if value != '':
                    filter['fecha_consecutivo__lte'] = datetime.strptime(value, '%Y-%m-%d').date()
            # if key == 'modulo':
            #     if value != '':
            #         filter['id_modulo_que_radica__nombre__icontains'] = value


            if key == 'id_persona':
                if value != '':
                    filter['id_id_persona_solicita'] = value
        instance = self.get_queryset().filter(**filter).order_by('fecha_consecutivo')
        
        consecutivo_value = request.query_params.get('consecutivo')
        print(consecutivo_value)
        if not instance:
            raise NotFound("No existen registros")

        serializador = self.serializer_class(instance,many=True)
        data_respuesta = serializador.data
        data_validada =[]
        if consecutivo_value and consecutivo_value != '':
            data_validada = [item for item in serializador.data if consecutivo_value in item.get('consecutivo', '')]
        else :
            data_validada = data_respuesta


        if not instance:
            raise NotFound("No existen registros asociados.")
        
    
        serializador=self.serializer_class(instance,many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':data_validada}, status=status.HTTP_200_OK)

class ConsecutivoCreateView(generics.CreateAPIView):
    serializer_class = ConsecutivoCreateSerializer
    permission_classes = [IsAuthenticated]
    vista_generadora_numero = ConfigTiposRadicadoAgnoGenerarN()

    def post(self, request):
        data_in = request.data
        usuario = request.user.persona.id_persona
        if not 'id_unidad' in data_in:
            raise ValidationError("Debe ingresar la unidad a la cual se le asignara el consecutivo.")
        if not 'id_cat_serie_und' in data_in:
            raise ValidationError("Debe ingresar el catalogo al cual se le va a crear el consecutivo.")
        
        respuesta = self.vista_generadora_numero.generar_n_radicado(data_in)

        if respuesta.status_code != status.HTTP_200_OK:
            return respuesta
        
        print(respuesta.data['data'])
        #raise ValidationError("AQUI VAMOS")
        data_respuesta = respuesta.data['data']

        data_consecutivo = {}
        data_consecutivo['id_unidad'] = data_respuesta['id_unidad']

        if 'id_cat_serie_und' in data_in:
            data_consecutivo['id_catalogo'] = data_in['id_cat_serie_und']
        data_consecutivo['agno_consecutivo'] = data_respuesta['agno_consecutivo']
        data_consecutivo['nro_consecutivo'] = data_respuesta['consecutivo_actual']
        data_consecutivo['fecha_consecutivo'] = data_respuesta['fecha_consecutivo_actual']
        data_consecutivo['id_persona_solicita'] = data_respuesta['id_persona_consecutivo_actual']

        serializer = self.serializer_class(data=data_consecutivo)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'succes': True, 'detail':'Se creo el consecutivo correctamente', 'data':{**serializer.data,'consecutivo':data_respuesta['conseg_nuevo']}}, status=status.HTTP_201_CREATED)
