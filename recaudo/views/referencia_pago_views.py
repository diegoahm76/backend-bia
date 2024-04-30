import copy

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, date, timedelta
import copy
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from django.utils import timezone
from gestion_documental.models.ccd_models import CatalogosSeriesUnidad

from recaudo.models.referencia_pago_models import ConfigReferenciaPagoAgno
from recaudo.serializers.referencia_pago_serializers import ConfigTipoRefgnoCreateSerializer, ConfigTipoRefgnoGetSerializer
from transversal.models.organigrama_models import UnidadesOrganizacionales
from seguridad.models import Personas
from seguridad.utils import Util

class ConfigTipoConsecAgnoCreateView(generics.CreateAPIView):
    serializer_class = ConfigTipoRefgnoCreateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request,):
        data_in = request.data
        usuario = request.user.persona.id_persona
        data_in['user'] = usuario #id_persona_config_implementacion
        data_in['direccion']=Util.get_client_ip(request)
        #data_in['fecha_inicial_config_implementacion'] = timezone.now()
       
        respuesta = self.crear_config_tipos_consecutivo_agno(data_in)
        return respuesta

    def crear_config_tipos_consecutivo_agno(self, data):
        data_in = data
        hoy = date.today()
        age = hoy.year

        # unidad_encargada = UnidadesOrganizacionales.objects.filter(nombre ='Oficina Asesora Jurídica' ,id_organigrama__actual=True).first()

        # catalogo = CatalogosSeriesUnidad.objects.filter(id_unidad_organizacional=unidad_encargada)

        # print(catalogo)

        # print(unidad_encargada.id_unidad_organizacional)
        print(age)
        print(age+1)
        #print(data_in['agno_radicado'])
        if 'agno_ref' in data_in:
            if data_in['agno_ref']!= age and  data_in['agno_ref']!= (age+1):
                raise ValidationError("El año debe ser el actual o el siguiente")
        else:
            raise ValidationError("El año de referencia es requerido")
        

        if not data_in['id_catalogo_serie_unidad']:
             cof = ConfigReferenciaPagoAgno.objects.filter(agno_ref=data_in['agno_ref'],id_unidad= data_in['id_unidad'])
             if cof:
                 raise ValidationError("Ya existe una configuracion")
        
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
        serializer = ConfigTipoRefgnoCreateSerializer(data=data_in)
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
        #print(serializer.data)
        #raise ValidationError("Se implementó correctamente")

        return Response({
                'success': True,
                'detail': 'Se creó la configuración de los consecutivos correctamente.',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)



class ConfigTiposConsecutivoAgnoUpdate(generics.UpdateAPIView):
    serializer_class = ConfigTipoRefgnoCreateSerializer
    queryset = ConfigReferenciaPagoAgno.objects.all()
    permission_classes = [IsAuthenticated]

    def actualizar_config_tipos_consecutivo_agno(self,data,pk):
        
        data_in=data
        hoy = date.today()
        age=hoy.year
        # Obtener la instancia existente para actualizar
        instance =ConfigReferenciaPagoAgno.objects.filter(id_config_ref_agno=pk).first()

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

        
        serializer = ConfigTipoRefgnoCreateSerializer(instance, data=data_in, partial=True)
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
    



class ConfigTipoConsecAgnoGetView(generics.ListAPIView):
    serializer_class = ConfigTipoRefgnoGetSerializer
    permission_classes = [IsAuthenticated]
    queryset = ConfigReferenciaPagoAgno.objects.all()
    
    def get(self, request,agno,uni):
        instance = self.get_queryset().filter(agno_ref=agno,id_unidad=uni)



        if not instance:
            raise NotFound('No existe registro')
        
        serializer = self.serializer_class(instance, many=True)
        
        return Response({'success':True, 'detail':'se encontraron los siguientes registros', 'data': serializer.data}, status=status.HTTP_200_OK)


