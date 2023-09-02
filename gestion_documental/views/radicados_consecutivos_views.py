
from rest_framework.response import Response
from rest_framework.views import APIView
from gestion_documental.choices.tipo_radicado_choices import cod_tipos_radicados_LIST
from gestion_documental.choices.tipo_radicado_choices import TIPOS_RADICADO_CHOICES
from rest_framework import status
from gestion_documental.models.radicados_models import ConfigTiposRadicadoAgno
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from gestion_documental.serializers.radicados_consecutivos_serializers import ConfigTiposRadicadoAgnoCreateSerializer, ConfigTiposRadicadoAgnoGetSerializer, ConfigTiposRadicadoAgnoUpDateSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, status
from datetime import date
from django.utils import timezone

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
        if instance.implementar and instance.agno_radicado==age:
            raise ValidationError('No se puede modificar la configuracion de un consecutivo si se esta implementando actualmente.')
        if instance.agno_radicado < age:
            raise ValidationError('No se puede modificar la configuracion de un consecutivo si es de un año anterior.')
        if 'implementar' in data_in:
            if data_in['implementar']==True:

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
                    data_in['consecutivo_inicial']=data_in['consecutivo_inicial']-1
         
            serializer =ConfigTiposRadicadoAgnoUpDateSerializer(instance, data=data_in, partial=True)
            serializer.is_valid(raise_exception=True)
            
            serializer.save()
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
        usuario = request.user.id_usuario
        data_in['user']=usuario#id_persona_config_implementacion
        
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
        print(data_in['agno_radicado'])
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
        try:



            serializer = ConfigTiposRadicadoAgnoCreateSerializer(data=data_in)
            serializer.is_valid(raise_exception=True)
            serializer.save()

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
