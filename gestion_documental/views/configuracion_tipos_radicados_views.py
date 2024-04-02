
import copy
from rest_framework.response import Response
from rest_framework.views import APIView
from gestion_documental.choices.tipo_radicado_choices import cod_tipos_radicados_LIST
from gestion_documental.choices.tipo_radicado_choices import TIPOS_RADICADO_CHOICES
from rest_framework import status
from gestion_documental.models.radicados_models import ConfigTiposRadicadoAgno, modulos_radican
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from gestion_documental.serializers.radicados_consecutivos_serializers import ConfigTiposRadicadoAgnoCreateSerializer, ConfigTiposRadicadoAgnoGetSerializer, ConfigTiposRadicadoAgnoUpDateSerializer,RadicadoPostSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from datetime import date
from django.utils import timezone
from seguridad.models import Personas

from seguridad.utils import Util
from transversal.views.bandeja_alertas_views import BandejaAlertaPersonaCreate
from datetime import datetime, date, timedelta, timezone
class GetLisPerfilesSistema(APIView):
    def get(self, request):
        return Response({'success':True, 'detail':'Los perfiles del sistema son los siguientes', 'data': cod_tipos_radicados_LIST}, status=status.HTTP_200_OK) 


class ConfigTiposRadicadoAgnoUpdate(generics.UpdateAPIView):
    serializer_class = ConfigTiposRadicadoAgnoUpDateSerializer
    queryset = ConfigTiposRadicadoAgno.objects.all()
    permission_classes = [IsAuthenticated]

    def actualizar_config_tipos_radicado_agno(self,data,pk):
        
        data_in=data
        hoy = date.today()
        age=hoy.year
        # Obtener la instancia existente para actualizar
        instance =ConfigTiposRadicadoAgno.objects.filter(id_config_tipo_radicado_agno=pk).first()

        # Verificar si la instancia existe
        if not instance:
            return Response({'detail': 'La configuracion no existe.'}, status=status.HTTP_404_NOT_FOUND)
        
        previous=copy.copy(instance)
        if instance.implementar and instance.agno_radicado==age:
            raise ValidationError('No se puede modificar la configuracion de un consecutivo si se esta implementando actualmente.')
        if instance.agno_radicado < age:
            raise ValidationError('No se puede modificar la configuracion de un consecutivo si es de un año anterior.')
        if 'implementar' in data_in:

            if data_in['implementar']==False and instance.implementar:
                 data_in['prefijo_consecutivo']=None
                 data_in['consecutivo_inicial']=None
                 data_in['cantidad_digitos']=None
            elif data_in['implementar']==True:

                if instance.cod_tipo_radicado=="U":
                    entrada=ConfigTiposRadicadoAgno.objects.filter(implementar=True,cod_tipo_radicado='E',agno_radicado=instance.agno_radicado)
                    if entrada:
                        raise ValidationError("No se puede implementar la configuracion si se encuentra vigente una de tipo entrada")
                    salida=ConfigTiposRadicadoAgno.objects.filter(implementar=True,cod_tipo_radicado='S',agno_radicado=instance.agno_radicado)
                    if salida:
                        raise ValidationError("No se puede implementar la configuracion si se encuentra vigente una de tipo salida")
                
                elif instance.cod_tipo_radicado=="E" or instance.cod_tipo_radicado=="S":
                    unico=ConfigTiposRadicadoAgno.objects.filter(cod_tipo_radicado="U",agno_radicado=instance.agno_radicado,implementar=True)
                    if unico:
                        raise ValidationError("No se puede implementar la configuracion si ya esta vigente una de tipo unica")
                prefijo_consecutivo = data.get('prefijo_consecutivo')
                consecutivo_inicial = data.get('consecutivo_inicial')
                cantidad_digitos = data.get('cantidad_digitos')
                
                # Validar campos almacenados en la instancia actual
                if prefijo_consecutivo is None:
                    prefijo_consecutivo = instance.prefijo_consecutivo

                if consecutivo_inicial is None:
                    consecutivo_inicial = instance.consecutivo_inicial
                    
                if cantidad_digitos is None:
                    cantidad_digitos = instance.cantidad_digitos
                
                if  prefijo_consecutivo is None:
                     raise ValidationError("Se debe asignar un prefijo.")
                
                if consecutivo_inicial  is None:
                    raise ValidationError("Se debe asignar un consecutivo inicial.")
                
                if cantidad_digitos is None:
                    raise ValidationError("se deben asignar una cantidad de digitos.")
                
                #if consecutivo_inicial < 0:
                #    raise ValidationError(" El consecutivo inicial debe ser mayor o igual a 0.")
                if cantidad_digitos <= 0:
                    raise ValidationError("se debe ser mayor a cero.")
                data_in['fecha_inicial_config_implementacion']= timezone.now()
                data_in['id_persona_config_implementacion']=data_in['user']

        try:

            if 'consecutivo_inicial' in data_in:
                if data_in['consecutivo_inicial']:
                    data_in['consecutivo_actual']=data_in['consecutivo_inicial']-1
            if 'cantidad_digitos' in data_in and data_in['cantidad_digitos']:
                if data_in['cantidad_digitos'] > 20:
                    raise ValidationError('La cantidad de digitos no puede ser mayor a 20')

         
            serializer =ConfigTiposRadicadoAgnoUpDateSerializer(instance, data=data_in, partial=True)
            serializer.is_valid(raise_exception=True)
            
            serializer.save()

            direccion=data_in['direccion']
            descripcion = {"AgnoRadicado":instance.agno_radicado,"CodTipoRadicado":instance.cod_tipo_radicado}
            
            valores_actualizados = {'current': instance, 'previous': previous}
            #print(valores_actualizados)
            id_modulo=0
            if instance.agno_radicado==age:
                id_modulo=143
            elif instance.agno_radicado==age+1:
                id_modulo=144
            auditoria_data = {
                "id_usuario" : data_in['user'],
                "id_modulo" : id_modulo,
                "cod_permiso": "AC",
                "subsistema": 'GEST',
                "dirip": direccion,
                "descripcion": descripcion, 
                "valores_actualizados": valores_actualizados
            }
            Util.save_auditoria(auditoria_data) 
        except ValidationError as e:
            raise ValidationError(e.detail)

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
        response= self.actualizar_config_tipos_radicado_agno(data_in,pk)
        return response
    

class ConfigTiposRadicadoAgnoCreate(generics.CreateAPIView):
    serializer_class = ConfigTiposRadicadoAgnoCreateSerializer
    permission_classes = [IsAuthenticated]

    def crear_config_tipos_radicado_agno(self, data):
        data_in = data
        hoy = date.today()
        age = hoy.year
        print(age)
        print(age+1)
        #print(data_in['agno_radicado'])
        if 'agno_radicado' in data_in:
            if data_in['agno_radicado']!= age and  data_in['agno_radicado']!= (age+1):
                raise ValidationError("El año debe ser el actual o el siguiente")
        else:
            raise ValidationError("El año del radicado es requerido")
        
        if 'implementar' in data_in and data_in['implementar']:

            if data_in['cod_tipo_radicado'] == "U":
                entrada = ConfigTiposRadicadoAgno.objects.filter(implementar=True, cod_tipo_radicado='E', agno_radicado=data_in['agno_radicado'])
                if entrada:
                    raise ValidationError("No se puede implementar la configuración si se encuentra vigente una de tipo entrada")
                salida = ConfigTiposRadicadoAgno.objects.filter(implementar=True, cod_tipo_radicado='S', agno_radicado=data_in['agno_radicado'])
                if salida:
                    raise ValidationError("No se puede implementar la configuración si se encuentra vigente una de tipo salida")

            elif data_in['cod_tipo_radicado'] == "E" or data_in['cod_tipo_radicado'] == "S":
                unico = ConfigTiposRadicadoAgno.objects.filter(cod_tipo_radicado="U", agno_radicado=data_in['agno_radicado'],implementar=True)
                if unico:
                    raise ValidationError("No se puede implementar la configuración si ya está vigente una de tipo unica")

            prefijo_consecutivo = data.get('prefijo_consecutivo')
            consecutivo_inicial = data.get('consecutivo_inicial')
            cantidad_digitos = data.get('cantidad_digitos')

            if prefijo_consecutivo is None:
                raise ValidationError("Se debe asignar un prefijo.")

            if consecutivo_inicial is None:
                raise ValidationError("Se debe asignar un consecutivo inicial.")

            if cantidad_digitos is None:
                raise ValidationError("Se deben asignar una cantidad de dígitos.")

            if cantidad_digitos <= 0:
                raise ValidationError("La cantidad de dígitos debe ser mayor a cero.")
            
            data_in['id_persona_config_implementacion']=data_in['user']
            data_in['fecha_inicial_config_implementacion'] = timezone.now()
            data_in['consecutivo_actual'] = consecutivo_inicial-1
        try:
            if 'cantidad_digitos' in data_in and data_in['cantidad_digitos']:
                if data_in['cantidad_digitos'] > 20:
                    raise ValidationError('La cantidad de digitos no puede ser mayor a 20')

            
            print(data_in)
            serializer = ConfigTiposRadicadoAgnoCreateSerializer(data=data_in)
            serializer.is_valid(raise_exception=True)
            instance=serializer.save()

            id_modulo=0
            if instance.agno_radicado==age:
                id_modulo=143
            elif instance.agno_radicado==age+1:
                id_modulo=144

            descripcion = {"AgnoRadicado":instance.agno_radicado,"CodTipoRadicado":instance.cod_tipo_radicado}
            auditoria_data = {
            "id_usuario" : data_in['user'],
            "id_modulo" : id_modulo,
            "cod_permiso": "CR",
            "subsistema": 'GEST',
            "dirip": data_in['direccion'],
            "descripcion": descripcion, 
            }
            Util.save_auditoria(auditoria_data)

            return Response({
                'success': True,
                'detail': 'Se creó la configuración de los consecutivos correctamente.',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            raise ValidationError(e.detail)

        return serializer.data

    def post(self, request, *args, **kwargs):
        data_in = request.data
        usuario = request.user.id_usuario
        data_in['user'] = usuario #id_persona_config_implementacion
        data_in['direccion']=Util.get_client_ip(request)
        #data_in['fecha_inicial_config_implementacion'] = timezone.now()
        response = self.crear_config_tipos_radicado_agno(data_in)
        return response


class ConfigTiposRadicadoAgnoGet(generics.ListAPIView):
    serializer_class = ConfigTiposRadicadoAgnoGetSerializer
    queryset = ConfigTiposRadicadoAgno.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,agno,tipo):
        
        hoy = date.today()
        

        
        valido=False

        for data,name in TIPOS_RADICADO_CHOICES:
            if data==tipo:
                valido=True
                break
        
        if not valido:
            raise ValidationError("Tipo de radicado no valido")
        
        queryset=ConfigTiposRadicadoAgno.objects.filter(agno_radicado=agno,cod_tipo_radicado=tipo)
        serializador = self.serializer_class(queryset, many=True)
                         
        return Response({'succes':True, 'detail':'Se encontró el siguiente histórico','data':serializador.data}, status=status.HTTP_200_OK)



class ConfigTiposRadicadoAgnoGenerarN(generics.UpdateAPIView):
    serializer_class = ConfigTiposRadicadoAgnoUpDateSerializer
    queryset = ConfigTiposRadicadoAgno.objects.all()
    permission_classes = [IsAuthenticated]
    vista_creacion_configuracion =ConfigTiposRadicadoAgnoCreate()
    def generar_n_radicado(self,data):
        
        data_in=data
        print(data_in)
        hoy = date.today()
        age=hoy.year
        # # Obtener la instancia existente para actualizar
        instance =ConfigTiposRadicadoAgno.objects.filter(agno_radicado=age,cod_tipo_radicado=data_in['cod_tipo_radicado']).first()

        if not instance:
            tipos_radicado =TIPOS_RADICADO_CHOICES

            for data,name in tipos_radicado:
                auxiliar = ConfigTiposRadicadoAgno.objects.filter(cod_tipo_radicado=data,agno_radicado=age).first()
                if not auxiliar:
                    conf_agno_anterior = ConfigTiposRadicadoAgno.objects.filter(agno_radicado=age-1,cod_tipo_radicado=data).first()
                    print(conf_agno_anterior.prefijo_consecutivo)
                    nueva_configuracion = {
                                        'user':None,
                                        'direccion' : data_in['direccion'],
                                        'agno_radicado':age,
                                        'cod_tipo_radicado':conf_agno_anterior.cod_tipo_radicado,
                                        'prefijo_consecutivo':conf_agno_anterior.prefijo_consecutivo,
                                        'consecutivo_inicial':1,
                                        'cantidad_digitos':conf_agno_anterior.cantidad_digitos,
                                        'implementar':conf_agno_anterior.implementar,
                                        }
                    respuesta = self.vista_creacion_configuracion.crear_config_tipos_radicado_agno(nueva_configuracion)
                    if respuesta.status_code != status.HTTP_201_CREATED:
                        return respuesta

            instance =ConfigTiposRadicadoAgno.objects.filter(agno_radicado=age,cod_tipo_radicado=data_in['cod_tipo_radicado']).first()
            #raise NotFound("No se existe este tipo de configuracion de radicado.")
        
        ##Verificamos si es de tipo ENTRADA O SALIDA
        ##ENTRADA

        if not instance.implementar:
            if instance.cod_tipo_radicado in ['E','S']:

                if not instance.implementar:
                    instance =ConfigTiposRadicadoAgno.objects.filter(agno_radicado=age,cod_tipo_radicado='U').first()


        if not instance.implementar:
            return Response({
            'success': True,
            'detail': 'Este tipo de radicado no se encuentra configurado para este año',
                }, status=status.HTTP_200_OK)
           

            
                    
       
        #instance =ConfigTiposRadicadoAgno.objects.filter(agno_radicado=age,cod_tipo_radicado='U').first()


        new_data={}
        new_data['consecutivo_actual'] = instance.consecutivo_actual+1
        new_data['id_persona_consecutivo_actual'] = data_in['id_persona']
        new_data['fecha_consecutivo_actual'] = data_in['fecha_actual']
         
        serializer =ConfigTiposRadicadoAgnoUpDateSerializer(instance, data=new_data, partial=True)
        serializer.is_valid(raise_exception=True)
            
        instance = serializer.save()
        numero_con_ceros = str(instance.consecutivo_actual).zfill(instance.cantidad_digitos)
        radicado_nuevo= instance.prefijo_consecutivo+'-'+str(instance.agno_radicado)+'-'+numero_con_ceros
        
        
        #raise ValidationError("siu generando radicado")
        
        return Response({
            'success': True,
            'detail': 'Se actualizó la configuracion de los  consecutivos correctamente.',
            'data': {**serializer.data,'radicado_nuevo':radicado_nuevo}
        }, status=status.HTTP_200_OK)

    def put(self, request):
        data_in = request.data
        usuario = request.user.persona.id_persona
        #direccion=#
        data_in['user']=usuario#id_persona_config_implementacion
        data_in['direccion']=Util.get_client_ip(request)
        response= self.generar_n_radicado(data_in,)
        return response



class RadicadoCreate(generics.CreateAPIView):
    serializer_class = RadicadoPostSerializer
    config_radicados = ConfigTiposRadicadoAgnoGenerarN
    
    
    def post(self, request):
        data = request.data
        fecha_actual = datetime.now()
        print(fecha_actual)
        try:
            config_tipos_radicado = self.get_config_tipos_radicado(data)
            radicado_data = self.set_data_radicado(config_tipos_radicado, data['fecha_actual'], data['id_persona'], data['modulo_radica'])
            serializer = self.serializer_class(data=radicado_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer_data = serializer.data
            serializer_data['radicado_nuevo'] = config_tipos_radicado['radicado_nuevo']

            return Response({"success":True,"detail":"Se creo el radicado correctamente",'data':serializer_data}, status=status.HTTP_201_CREATED)
            

        except Exception as e:
            raise ValidationError(str(e))


    def get_config_tipos_radicado(self, request):
        data_request = {
            'id_persona': request['id_persona'],
            'cod_tipo_radicado': request['tipo_radicado'],
            'fecha_actual': request['fecha_actual']
        }
        config_tipos_radicados = self.config_radicados.generar_n_radicado(self, data_request)
        config_tipos_radicado_data = config_tipos_radicados.data['data']
        if config_tipos_radicado_data['implementar'] == False:
            raise ValidationError("El sistema requiere que se maneje un radicado de entrada o unico, debe solicitar al administrador del sistema la configuración del radicado")
        else:
            return config_tipos_radicado_data
        
    def set_data_radicado(self, config_tipos_radicado, fecha_actual, id_persona, modulo_radica):
        radicado = {}
        radicado['cod_tipo_radicado'] = config_tipos_radicado['cod_tipo_radicado']
        radicado['prefijo_radicado'] = config_tipos_radicado['prefijo_consecutivo']
        radicado['agno_radicado'] = config_tipos_radicado['agno_radicado']
        radicado['nro_radicado'] = config_tipos_radicado['consecutivo_actual']
        radicado['fecha_radicado'] = fecha_actual
        radicado['id_persona_radica'] = id_persona

        modulo_radica = modulos_radican.objects.filter(nombre=modulo_radica).first()
        radicado['id_modulo_que_radica'] = modulo_radica.id_ModuloQueRadica

        return radicado



def actualizar_conf_agno_sig():
    #print("SI SOU ")
    hoy = date.today()
    age=hoy.year+1
    
   
    instance =ConfigTiposRadicadoAgno.objects.filter(agno_radicado=age)
    for data,name in TIPOS_RADICADO_CHOICES:
        conf=ConfigTiposRadicadoAgno.objects.filter(agno_radicado=age,cod_tipo_radicado=data).first()
        if conf:
            if conf.implementar:
                print(conf)
            print("existe")
            print(data)
        else:
           conf_agno_anterior=ConfigTiposRadicadoAgno.objects.filter(agno_radicado=age-1,cod_tipo_radicado=data).first()
           data_conf={}
           data_conf['agno_radicado']=age
           data_conf['cod_tipo_radicado']=data
           data_conf['prefijo_consecutivo']=conf_agno_anterior.prefijo_consecutivo
           data_conf['consecutivo_inicial']=1
           data_conf['cantidad_digitos']=conf_agno_anterior.cantidad_digitos
           data_conf['implementar']=conf_agno_anterior.implementar
           print(conf_agno_anterior)
           print("No Existe "+data) 
        print("#############")
    
