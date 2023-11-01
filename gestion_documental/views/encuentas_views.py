
import copy
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from gestion_documental.models.encuencas_models import TIPO_USUARIO_CHOICES, AsignarEncuesta, DatosEncuestasResueltas, EncabezadoEncuesta, OpcionesRta, PreguntasEncuesta, RespuestaEncuesta
from gestion_documental.serializers.encuentas_serializers import AlertasGeneradasEncuestaPostSerializer, AsignarEncuestaGetSerializer, AsignarEncuestaPostSerializer, DatosEncuestasResueltasConteoSerializer, DatosEncuestasResueltasCreateSerializer, EncabezadoEncuestaCreateSerializer, EncabezadoEncuestaDeleteSerializer, EncabezadoEncuestaGetDetalleSerializer, EncabezadoEncuestaGetSerializer, EncabezadoEncuestaUpdateSerializer, EncuestaActivaGetSerializer, OpcionesRtaCreateSerializer, OpcionesRtaDeleteSerializer, OpcionesRtaGetSerializer, OpcionesRtaUpdateSerializer, PersonaRegistradaEncuentaGet, PersonasFilterEncuestaSerializer, PreguntasEncuestaCreateSerializer, PreguntasEncuestaDeleteSerializer, PreguntasEncuestaGetSerializer, PreguntasEncuestaUpdateSerializer,RespuestaEncuestaCreateSerializer
from django.db.models import Max
from datetime import datetime
from django.db import transaction
from seguridad.utils import Util
from django.db.models import Count
from transversal.admin import PersonasAdmin
from transversal.models.alertas_models import AlertasBandejaAlertaPersona, AlertasGeneradas, BandejaAlertaPersona, ConfiguracionClaseAlerta

from transversal.models.personas_models import Personas
from transversal.models.base_models import Departamento, Municipio, Paises, Sexo, TipoDocumento
from gestion_documental.choices.rango_edad_choices import RANGO_EDAD_CHOICES
from django.template.loader import render_to_string

from transversal.serializers.alertas_serializers import AlertasBandejaAlertaPersonaPostSerializer
from transversal.serializers.personas_serializers import PersonasFilterSerializer
class EncabezadoEncuestaCreate(generics.CreateAPIView):
    serializer_class = EncabezadoEncuestaCreateSerializer
    permission_classes = [IsAuthenticated]
    queryset = EncabezadoEncuesta.objects.all()
    
    def post(self,request):
        data_in = request.data
        usuario = request.user.persona.id_persona
        #print(usuario)
        try:
            with transaction.atomic():
                data_in['id_persona_ult_config_implement']=usuario
                serializer = self.serializer_class(data=data_in)
                serializer.is_valid(raise_exception=True)
                instance=serializer.save()
                crear_pregunta=PreguntasEncuestaCreate()
                crear_opcion=OpcionesRtaCreate()
                response_preguntas=[]
                if 'preguntas' in data_in:
                
                    data_pregunta={}
                    
                    
                    for pre in data_in['preguntas']:
                        #print(pre)
                        data_pregunta.clear()
                        
                        data_pregunta={**pre}
                        data_pregunta['id_encabezado_encuesta']=instance.id_encabezado_encuesta
                        #print(data_pregunta)
                        response_pregunta=crear_pregunta.crear_pregunta(data_pregunta,request)
                        if response_pregunta.status_code!=status.HTTP_201_CREATED:
                            return response_pregunta
                        response_preguntas.append(response_pregunta.data['data'])

                response_encabezado=serializer.data
                response_encabezado['preguntas']=response_preguntas

            #AUDITORIA DE CREAR ENCUESTA
            id_usuario = request.user.id_usuario
            direccion=Util.get_client_ip(request)
            descripcion = {"NombreEncuesta": str(instance.nombre_encuesta)}
            
            auditoria_data = {
                "id_usuario" : id_usuario,
                "id_modulo" : 167,
                "cod_permiso": "CR",
                "subsistema": 'GEST',
                "dirip": direccion,
                "descripcion": descripcion, 
            }
            #print(auditoria_data)
            Util.save_auditoria(auditoria_data)
            return Response({'success':True,'detail':'Se crearon los registros correctamente','data':response_encabezado},status=status.HTTP_201_CREATED)
        except ValidationError as e:       
            raise ValidationError(e.detail)


class EncabezadoEncuestaUpdate(generics.UpdateAPIView):
    queryset = EncabezadoEncuesta.objects.all()
    serializer_class = EncabezadoEncuestaUpdateSerializer
    permission_classes = [IsAuthenticated]
    def put(self, request, *args, **kwargs):


        fecha_actual = datetime.now()
        data_in=request.data
        instance = self.get_object()
        previus = copy.copy(instance)
        if not instance:
            raise NotFound("No existe encuentas asociada e esta id")
        if instance.item_ya_usado:
            raise NotFound("No se puede editar esta encuesta")
            
        try:
            data_in['fecha_ult_config_implement']=fecha_actual
            data_in['id_persona_ult_config_implement']=request.user.persona.id_persona
            serializer = self.get_serializer(instance, data=data_in,partial=True)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            data_response_pregunta=[]
            if 'preguntas' in data_in :
                crear_pregunta=PreguntasEncuestaCreate()
                actualizar_pregunta=PreguntasEncuestaUpdate()
                eliminar_pregunta=PreguntasEncuestaDelete()

                id_preguntas= [opcion.get('id_pregunta_encuesta', None) for opcion in data_in['preguntas']]
                #BUSCA EN BASE DE DATOS LAS RESPUESTAS
                respuestas_persistentes=list(PreguntasEncuesta.objects.filter(id_encabezado_encuesta=instance.id_encabezado_encuesta).values_list('id_pregunta_encuesta', flat=True))
                print("EN BASE DE DATOS :"+str(respuestas_persistentes))
                print("EN JSON:"+ str(id_preguntas))
                id_opciones_json_set = set(id_preguntas)
                id_opciones_bd_set = set(respuestas_persistentes)

                id_opciones_no_en_json = list(id_opciones_bd_set.difference(id_opciones_json_set))
                print(id_opciones_no_en_json)
                for ids in  id_opciones_no_en_json:
                    print (ids)
                    respuesta_pregunta=eliminar_pregunta.eliminar(ids,request)
                    if respuesta_pregunta.status_code != status.HTTP_200_OK:
                        return respuesta_pregunta
           
                for pre in data_in['preguntas']:

                    if 'id_pregunta_encuesta' in pre:
                        if pre:
                           
                            #print(pre)
                            response_pregunta=actualizar_pregunta.actualizar_pregunta(pre,pre['id_pregunta_encuesta'],request)
                            if response_pregunta.status_code!=status.HTTP_200_OK:
                                return response_pregunta  
                            data_response_pregunta.append(response_pregunta.data['data'])

                    else:
                        id_encabezado=instance.id_encabezado_encuesta
                        response_pregunta=crear_pregunta.crear_pregunta({**pre,"id_encabezado_encuesta":id_encabezado},request)
                        if response_pregunta.status_code!=status.HTTP_201_CREATED:
                            return response_pregunta    
                        data_response_pregunta.append(response_pregunta.data['data'])
                    #print(pre)
               

            response_data=serializer.data
            response_data['preguntas_encuesta']=data_response_pregunta

            # AUDITORÍA ENCUESTA
            usuario = request.user.id_usuario
            descripcion = {"NombreEncuesta": str(previus.nombre_encuesta)}
            direccion=Util.get_client_ip(request)
            valores_actualizados = {'previous':previus, 'current':instance}
            auditoria_data = {
                "id_usuario" : usuario,
                "id_modulo" : 167,
                "cod_permiso": "AC",
                "subsistema": 'GEST',
                "dirip": direccion,
                "descripcion": descripcion,
                "valores_actualizados": valores_actualizados,
            }
            Util.save_auditoria(auditoria_data)
            return Response({
                "success": True,
                "detail": "Se actualizó el encabezado de encuesta correctamente",
                "data": response_data
            }, status=status.HTTP_200_OK)
        except ValidationError as e:       
            raise ValidationError(e.detail)

class PreguntasEncuestaCreate(generics.CreateAPIView):
    serializer_class = PreguntasEncuestaCreateSerializer
    permission_classes = [IsAuthenticated]
    queryset = PreguntasEncuesta.objects.all()
    
    def crear_pregunta(self,data,request):
        try:
           
            valor_maximo = PreguntasEncuesta.objects.filter(id_encabezado_encuesta=data['id_encabezado_encuesta']).aggregate(Max('ordenamiento'))['ordenamiento__max']
            valor_orden=1
            if valor_maximo is not None:
         
                valor_orden=int(valor_maximo)+1
            
            data_in=data
            data_in['ordenamiento']=valor_orden
            serializer = PreguntasEncuestaCreateSerializer(data=data_in)
            serializer.is_valid(raise_exception=True)
            instance=serializer.save()
            id_pregunta=instance.id_pregunta_encuesta
            #print(id_pregunta)

            crear_opcion=OpcionesRtaCreate()
            data_ops=[]
            if 'opciones_rta' in data_in:
                if data_in['opciones_rta']:
                    for opc_rta in  data_in['opciones_rta']:
                        
                        response_pregunta=crear_opcion.crear_opciones_rta({**opc_rta,"id_pregunta":id_pregunta},request)
                        if response_pregunta.status_code!=status.HTTP_201_CREATED:
                            return response_pregunta   
                        #print (opc_rta)
                        data_ops.append(response_pregunta.data['data'])
            data_response=serializer.data
            data_response['opciones_rta']=data_ops

            #AUDITORIA DE CREAR PREGUNTA
            id_usuario = request.user.id_usuario
            direccion=Util.get_client_ip(request)
            descripcion = {"IdEncuesta": str(instance.id_encabezado_encuesta),"RedaccionPregunta": str(instance.redaccion_pregunta)}
            
            auditoria_data = {
                "id_usuario" : id_usuario,
                "id_modulo" : 167,
                "cod_permiso": "CR",
                "subsistema": 'GEST',
                "dirip": direccion,
                "descripcion": descripcion, 
            }
            #print(auditoria_data)
            Util.save_auditoria(auditoria_data)


            return Response({'success':True,'detail':'Se crearon los registros correctamente','data':data_response},status=status.HTTP_201_CREATED)
        except ValidationError as e:       
            raise ValidationError(e.detail)

    def post(self,request):
        data_in = request.data
        usuario = request.user.id_usuario
        direccion=Util.get_client_ip(request)
        response=self.crear_pregunta({**data_in},request)
        return response


class PreguntasEncuestaUpdate(generics.UpdateAPIView):
    queryset = PreguntasEncuesta.objects.all()
    serializer_class = PreguntasEncuestaUpdateSerializer
    permission_classes = [IsAuthenticated]
    def actualizar_pregunta(self,data,pk,request):
        data_in=data
        instance = PreguntasEncuesta.objects.filter(id_pregunta_encuesta=pk).first()

        if not instance:
            raise NotFound("No existe encuentas asociada e esta id")
        
        previus = copy.copy(instance)
        
        
        try:

            
            serializer = PreguntasEncuestaUpdateSerializer(instance, data=data_in,partial=True)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            id_pregunta=instance.id_pregunta_encuesta
            crear_opcion=OpcionesRtaCreate()
            actualizar_opcion=OpcionesRtaUpdate()
            eliminar_opcion=OpcionesRtaDelete()
            data_ops=[]
            
            if 'opciones_rta' in data_in:
                if data_in['opciones_rta']:
                    id_opciones_rta = [opcion.get('id_opcion_rta', None) for opcion in data_in['opciones_rta']]
                    #BUSCA EN BASE DE DATOS LAS RESPUESTAS
                    respuestas_persistentes=list(OpcionesRta.objects.filter(id_pregunta=instance.id_pregunta_encuesta).values_list('id_opcion_rta', flat=True))
                    #print("EN BASE DE DATOS :"+str(respuestas_persistentes))
                    #print("EN JSON:"+ str(id_opciones_rta))
                    id_opciones_json_set = set(id_opciones_rta)
                    id_opciones_bd_set = set(respuestas_persistentes)

                    id_opciones_no_en_json = list(id_opciones_bd_set.difference(id_opciones_json_set))

           

                    for opc_rta in  data_in['opciones_rta']:
                        if 'id_opcion_rta' in opc_rta and opc_rta['id_opcion_rta'] :
                            
                            response_pregunta=actualizar_opcion.actualizar_opciones_rta({**opc_rta},opc_rta['id_opcion_rta'],request)
                            if response_pregunta.status_code!=status.HTTP_200_OK:
                                return response_pregunta   
                            
                            data_ops.append(response_pregunta.data['data'])

                        else:
                            response_pregunta=crear_opcion.crear_opciones_rta({**opc_rta,"id_pregunta":id_pregunta},request)
                            if response_pregunta.status_code!=status.HTTP_201_CREATED:
                                return response_pregunta   
                            
                            data_ops.append(response_pregunta.data['data'])
                            
                    for delete in id_opciones_no_en_json:
                        datos_eliminados_response = eliminar_opcion.eliminar(delete,request)
                        if datos_eliminados_response.status_code != status.HTTP_200_OK:
                            return datos_eliminados_response
                        #print (datos_eliminados_response)
            data_response=serializer.data
            data_response['opciones_rta']=data_ops
            # AUDITORÍA PREGUNTA
            usuario = request.user.id_usuario
            descripcion = {"IdEncuesta": str(previus.id_encabezado_encuesta),"RedaccionPregunta": str(previus.redaccion_pregunta)}
            direccion=Util.get_client_ip(request)
            valores_actualizados = {'previous':previus, 'current':instance}
            auditoria_data = {
                "id_usuario" : usuario,
                "id_modulo" : 167,
                "cod_permiso": "AC",
                "subsistema": 'GEST',
                "dirip": direccion,
                "descripcion": descripcion,
                "valores_actualizados": valores_actualizados,
            }
            Util.save_auditoria(auditoria_data)

            
            return Response({
                "success": True,
                "detail": "Se actualizó el encabezado de encuesta correctamente",
                "data":data_response
            }, status=status.HTTP_200_OK)
        except ValidationError as e:       
            raise ValidationError(e.detail)


    def put(self, request, pk):

        response =self.actualizar_pregunta(request.data,pk)
        return response

class PreguntasEncuestaDelete(generics.DestroyAPIView):
    queryset = PreguntasEncuesta.objects.all()
    serializer_class = PreguntasEncuestaDeleteSerializer
    permission_classes = [IsAuthenticated]
    def eliminar(self,pk,request):
        instance = PreguntasEncuesta.objects.filter(id_pregunta_encuesta=pk).first()
        previus = copy.copy(instance)
        if not instance:
            raise NotFound("No existe pregunta asociada a esta id.")
        serializer =PreguntasEncuestaDeleteSerializer(instance)
        instance.delete()
        #AUDITORIA 
        usuario = request.user.id_usuario
        descripcion =  {"IdEncuentas" : str(previus.id_encabezado_encuesta), "RedaccionPregunta" : str(previus.redaccion_pregunta)}
        dirip = Util.get_client_ip(request)
    
        auditoria_data = {
            'id_usuario': usuario,
            'id_modulo': 167,
            'cod_permiso': 'BO',
            'subsistema': 'GEST',
            'dirip': dirip,
            'descripcion': descripcion
        }
        
        Util.save_auditoria(auditoria_data)


        return Response({
            "success": True,
            "detail": "Se eliminó la pregunta correctamente",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    def delete(self, request,pk):
        response=self.eliminar(pk,request)
        return response
    
class OpcionesRtaCreate(generics.CreateAPIView):
    serializer_class = OpcionesRtaCreateSerializer
    permission_classes = [IsAuthenticated]
    queryset = OpcionesRta.objects.all()
    
    def crear_opciones_rta(self,data,request):
        try:

            valor_maximo = OpcionesRta.objects.filter(id_pregunta=data['id_pregunta']).aggregate(Max('ordenamiento'))['ordenamiento__max']
            valor_orden=1
            if valor_maximo is not None:
         
                valor_orden=int(valor_maximo)+1
            
            data_in=data
            data_in['ordenamiento']=valor_orden
            serializer = OpcionesRtaCreateSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            instance=serializer.save()
                        #AUDITORIA DE CREAR PREGUNTA
            id_usuario = request.user.id_usuario
            direccion=Util.get_client_ip(request)
            descripcion = {"IdPregunta": str(instance.id_pregunta.id_pregunta_encuesta),"OpcionRta": str(instance.opcion_rta)}
            
            auditoria_data = {
                "id_usuario" : id_usuario,
                "id_modulo" : 167,
                "cod_permiso": "CR",
                "subsistema": 'GEST',
                "dirip": direccion,
                "descripcion": descripcion, 
            }
            #print(auditoria_data)
            Util.save_auditoria(auditoria_data)
            return Response({'success':True,'detail':'Se crearon los registros correctamente','data':serializer.data},status=status.HTTP_201_CREATED)
        
        except ValidationError as e:       
            raise ValidationError(e.detail)

    def post(self,request):
        data_in = request.data
        response=self.crear_opciones_rta(data_in,request)
        return response

class OpcionesRtaUpdate(generics.UpdateAPIView):
    queryset = OpcionesRta.objects.all()
    serializer_class = OpcionesRtaUpdateSerializer
    permission_classes = [IsAuthenticated]
    def actualizar_opciones_rta(self,data,pk,request):
        data_in=data
        instance = OpcionesRta.objects.filter(id_opcion_rta=pk).first()

        if not instance:
            raise NotFound("No existe opcion asociada e esta id")
        previus = copy.copy(instance)
        try:
 
            serializer = OpcionesRtaUpdateSerializer(instance, data=data_in,partial=True)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()




          
            # AUDITORÍA RESPUESTA
            usuario = request.user.id_usuario
            descripcion = {"IdPregunta": str(previus.id_pregunta),"OpcionRta": str(previus.opcion_rta)}
            direccion=Util.get_client_ip(request)
            valores_actualizados = {'previous':previus, 'current':instance}
            auditoria_data = {
                "id_usuario" : usuario,
                "id_modulo" : 167,
                "cod_permiso": "AC",
                "subsistema": 'GEST',
                "dirip": direccion,
                "descripcion": descripcion,
                "valores_actualizados": valores_actualizados,
            }
            Util.save_auditoria(auditoria_data)
            return Response({
                "success": True,
                "detail": "Se actualizó el encabezado de encuesta correctamente",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except ValidationError as e:       
            raise ValidationError(e.detail)


    def put(self, request, pk):

        response =self.actualizar_opciones_rta(request.data,pk,request)
        return response

class OpcionesRtaDelete(generics.DestroyAPIView):
    queryset = OpcionesRta.objects.all()
    serializer_class = OpcionesRtaDeleteSerializer
    permission_classes = [IsAuthenticated]
    def eliminar(self,pk,request):
        instance = OpcionesRta.objects.filter(id_opcion_rta=pk).first()
        previus = copy.copy(instance)
        if not instance:
            raise NotFound("No existe pregunta asociada a esta id.")
        serializer =OpcionesRtaDeleteSerializer(instance)
        instance.delete()

        #Auditoria ENCUESTA

        usuario = request.user.id_usuario
        descripcion =  {"IdPregunta" : str(previus.id_pregunta),'OpcionRta':previus.opcion_rta}
        dirip = Util.get_client_ip(request)
    
        auditoria_data = {
            'id_usuario': usuario,
            'id_modulo': 167,
            'cod_permiso': 'BO',
            'subsistema': 'GEST',
            'dirip': dirip,
            'descripcion': descripcion
        }
        
        Util.save_auditoria(auditoria_data)
        return Response({
            "success": True,
            "detail": "Se eliminó la opcion correctamente",
            "data": serializer.data
        }, status = status.HTTP_200_OK)
    def delete(self, request,pk):
        response=self.eliminar(pk,request)
        return response




class EncabezadoEncuestaGet(generics.ListAPIView):
    queryset = EncabezadoEncuesta.objects.all()
    serializer_class = EncabezadoEncuestaGetSerializer
    def get(self, request, *args, **kwargs):
        instance = EncabezadoEncuesta.objects.all()
        serializer = self.serializer_class(instance,many=True)
        
        if not instance:
            raise NotFound("No existen encuentas registrados en el sistema.")

        return Response({'success':True,
                         'detail':'Se encontraron los siguientes registros.',
                         'data':serializer.data},status=status.HTTP_200_OK)
    
class EncabezadoEncuestaDetalleGet(generics.ListAPIView):
    queryset = EncabezadoEncuesta.objects.all()
    serializer_class = EncabezadoEncuestaGetDetalleSerializer
    def get(self, request,pk):
        instance = EncabezadoEncuesta.objects.filter(id_encabezado_encuesta=pk).first()
        serializer = self.serializer_class(instance)
        
        if not instance:
            raise NotFound("No existen encuentas registrados en el sistema.")
        
        preguntas = PreguntasEncuesta.objects.filter(id_encabezado_encuesta=pk)
        lista_preguntas=[]
        for pre in preguntas:
            data_pregunta=PreguntasEncuestaGetSerializer(pre).data
            opciones=OpcionesRta.objects.filter(id_pregunta=pre.id_pregunta_encuesta)
            #print(pre.id_pregunta_encuesta)
            data_opcion=[]
            for op in opciones:
                #print(op)
                data_opcion.append(OpcionesRtaGetSerializer(op).data)
            data_pregunta['opciones_rta']=data_opcion
            lista_preguntas.append(data_pregunta)
            
        
        data_response=serializer.data
        data_response['preguntas']=lista_preguntas
        return Response({'success':True,
                         'detail':'Se encontraron los siguientes registros.',
                         'data':data_response},status=status.HTTP_200_OK)
    
class EncabezadoEncuestaDelete(generics.DestroyAPIView):
    queryset = EncabezadoEncuesta.objects.all()
    serializer_class = EncabezadoEncuestaDeleteSerializer
    
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        previus = copy.copy(instance)
        if instance.item_ya_usado:
            raise ValidationError("No se puede eliminar una encuesta si ya fue usada")

        serializer = self.get_serializer(instance)

        preguntas_intance=PreguntasEncuesta.objects.filter(id_encabezado_encuesta=instance.id_encabezado_encuesta)

        if preguntas_intance:
            for pregunta in preguntas_intance:
                respuestas_instace=OpcionesRta.objects.filter(id_pregunta=pregunta.id_pregunta_encuesta)
                #print(respuestas_instace)
                respuestas_instace.delete()
            preguntas_intance.delete()
        instance.delete()

        #auditoria ENCUESTA

        usuario = request.user.id_usuario
        descripcion =  {"Nombre_encuesta" : str(previus.nombre_encuesta)}
        dirip = Util.get_client_ip(request)
    
        auditoria_data = {
            'id_usuario': usuario,
            'id_modulo': 167,
            'cod_permiso': 'BO',
            'subsistema': 'GEST',
            'dirip': dirip,
            'descripcion': descripcion
        }
        
        Util.save_auditoria(auditoria_data)
        

        return Response({
            "success": True,
            "detail": "Se eliminó el encabezado de encuesta correctamente",
            "data": serializer.data
        }, status= status.HTTP_200_OK)
    



##ENCUENTA CONTESTADA

class DatosEncuestasResueltasCreate(generics.CreateAPIView):
    serializer_class = DatosEncuestasResueltasCreateSerializer
    permission_classes = [IsAuthenticated]
    queryset = DatosEncuestasResueltas.objects.all()
    
    def post(self,request):
        data_in = request.data
        usuario = request.user.persona.id_persona
        datos_encuestas_resueltas=[]
        #print(usuario)
        try:
            with transaction.atomic():

                encuenta=EncabezadoEncuesta.objects.filter(id_encabezado_encuesta=data_in['id_encuesta']).first()
                if not encuenta:
                    raise ValidationError("NO existe la encuesta que trata de responder")
                if not encuenta.item_ya_usado:
                    encuenta.item_ya_usado=True
                    encuenta.save()
                fecha_actual = datetime.now()
                data_in['fecha_creacion'] = fecha_actual

                if 'tipo_usuario' in data_in:
                    if data_in['tipo_usuario'] == 'I':
                            if not  ('nro_documento_id' in data_in and data_in['nro_documento_id']):
                                raise ValidationError('El campo '+'numero de documento id'+" es requerido.")
                            if not  ('nombre_completo' in data_in and data_in['nombre_completo']):
                                raise ValidationError('El campo '+'nombre completo'+" es requerido.")
                            if not  ('cod_sexo' in data_in and data_in['cod_sexo']):
                                raise ValidationError('El campo '+'sexo'+" es requerido.")
                            if not  ('rango_edad' in data_in and data_in['rango_edad']):
                                raise ValidationError('El campo '+'rango de edad'+" es requerido.")
                            if not  ('email' in data_in and data_in['email']):
                                raise ValidationError('El campo '+'email'+" es requerido.")
                            if not  ('telefono' in data_in and data_in['telefono']):
                                raise ValidationError('El campo '+'telefono'+" es requerido.")
                if 'tipo_usuario' in data_in:
                    if  data_in['tipo_usuario'] == 'A':
                        data_in ['nro_documento_id'] = None
                        data_in ['nombre_completo'] = None
                        data_in ['cod_sexo'] = None
                        data_in ['rango_edad'] = None
                        data_in ['email'] = None
                        data_in ['telefono'] = None

                        
                #data_in['id_persona_ult_config_implement']=usuario
                if not ('ids_opciones_preguntas_encuesta' in data_in):
                    raise ValidationError('re requieren respuestas')
                if len(data_in['ids_opciones_preguntas_encuesta']) ==0:
                    raise ValidationError('se deben enviar respuestas')


                serializer = self.serializer_class(data=data_in)
                serializer.is_valid(raise_exception=True)
                instance=serializer.save()
                
                for respuesta in data_in['ids_opciones_preguntas_encuesta']:
                    if 'id_opcion_pregunta_encuesta' in respuesta:
                        print(respuesta['id_opcion_pregunta_encuesta'])
                        serializer_respuesta=RespuestaEncuestaCreateSerializer(data={**respuesta,'id_encuesta_resuelta':instance.id_datos_encuesta_resuelta})
                        serializer_respuesta.is_valid(raise_exception=True)
                        serializer_respuesta.save()         
                        datos_encuestas_resueltas.append(serializer_respuesta.data)     
                return Response({'success':True,'detail':'Se crearon los registros correctamente','data':{**serializer.data,'datos_encuestas_resueltas':datos_encuestas_resueltas}},status=status.HTTP_201_CREATED)
        except ValidationError as e:       
            raise ValidationError(e.detail)
        
class UsuarioRegistradoGet(generics.ListAPIView):
    queryset = Personas.objects.all()
    serializer_class = PersonaRegistradaEncuentaGet
    def get(self,request):
        data_in = request.data
        usuario = request.user.persona
        serializer = self.serializer_class(usuario)
        
        if not usuario:
            raise NotFound("No existen encuentas registrados en el sistema.")

        return Response({'success':True,
                         'detail':'Se encontraron los siguientes registros.',
                         'data':serializer.data},status=status.HTTP_200_OK)

##INFORME ENCUESTAS RESUELTAS ENTREGA 68
class EncuestasRealizadasGet(generics.ListAPIView):
    queryset = EncabezadoEncuesta.objects.all()
    serializer_class = EncuestaActivaGetSerializer
    def get(self, request, *args, **kwargs):
        instance = EncabezadoEncuesta.objects.filter(item_ya_usado=True)
        serializer = self.serializer_class(instance,many=True)
        
        if not instance:
            raise NotFound("No existen encuentas registrados en el sistema.")

        return Response({'success':True,
                         'detail':'Se encontraron los siguientes registros.',
                         'data':serializer.data},status=status.HTTP_200_OK)
    

class ConteoEncuestasGet(generics.ListAPIView):
    queryset = DatosEncuestasResueltas.objects.all()
    serializer_class = DatosEncuestasResueltasConteoSerializer
    def get(self, request,pk):
        instance = DatosEncuestasResueltas.objects.filter(id_encuesta=pk)
        encuesta= EncabezadoEncuesta.objects.filter(id_encabezado_encuesta=pk).first()
        serializer = self.serializer_class(instance)
        data=[]
        cantidad_encuestas_resueltas = DatosEncuestasResueltas.objects.filter(id_encuesta=pk).count()
        #print(cantidad_encuestas_resueltas)
        #print("CANTIDAD: "+str(cantidad_encuestas_resueltas))
        pregustas_encuesta = PreguntasEncuesta.objects.filter(id_encabezado_encuesta=pk)
        
        for pregunta in pregustas_encuesta:
            data_pregunta={}
            data_pregunta['id_pregunta_encuesta'] = pregunta.id_pregunta_encuesta
            data_pregunta['redaccion_pregunta'] = pregunta.redaccion_pregunta
            data_pregunta['ordenamiento'] = pregunta.ordenamiento
            #print(pregunta)
            opciones = OpcionesRta.objects.filter(id_pregunta=pregunta.id_pregunta_encuesta)
            data_respuestas=[]
            for opcion in opciones:
                data_opciones={}
                #print(" "+str(opcion))
                cantidad_de_respuestas = RespuestaEncuesta.objects.filter(id_opcion_pregunta_encuesta = opcion.id_opcion_rta).count()
                data_opciones['id_opcion_rta'] = opcion.id_opcion_rta
                data_opciones['opcion_rta'] =  opcion.opcion_rta
                data_opciones['ordenamiento'] = opcion.ordenamiento
                data_opciones['total'] = cantidad_de_respuestas
                data_respuestas.append(data_opciones)
                #print("CANTIDAD DE RESPUESTAS: "+str(cantidad_de_respuestas))
                data_pregunta['opciones'] = data_respuestas
            data.append(data_pregunta)
            
     
        return Response({'success':True,
                         'detail':'Se encontraron los siguientes registros.',
                         'data':{'total':cantidad_encuestas_resueltas,'preguntas':data}},status=status.HTTP_200_OK)
    



#DatosEncuestasResueltas
class ConteoEncuestasRegionesGet(generics.ListAPIView):
    queryset = DatosEncuestasResueltas.objects.all()

    def get(self, request,pk):
        instance = DatosEncuestasResueltas.objects.filter(id_encuesta=pk).values('id_municipio_para_nacional').annotate(cuenta=Count('id_municipio_para_nacional'))
        datos_nulos = DatosEncuestasResueltas.objects.filter(id_encuesta=pk, id_municipio_para_nacional__isnull=True).count()
        total = DatosEncuestasResueltas.objects.filter(id_encuesta=pk).count()
        print(datos_nulos)
        data=[]
        for i in instance:

            if i['id_municipio_para_nacional']:
                municipio = Municipio.objects.filter(cod_municipio=i['id_municipio_para_nacional']).first()
                print(municipio.nombre)
                data.append({'nombre':municipio.nombre,'total':i['cuenta']})
        data.append({'nombre':'NULOS','total':datos_nulos})

        return Response({'success':True,
                         'detail':'Se encontraron los siguientes registros.',
                         'data':{'registros':data,'total':total}},status=status.HTTP_200_OK)
    
class ConteoEncuestasTiposUsuarioGet(generics.ListAPIView):
    queryset = DatosEncuestasResueltas.objects.all()

    def get(self, request,pk):
        instance = DatosEncuestasResueltas.objects.filter(id_encuesta=pk).values('tipo_usuario').annotate(cuenta=Count('tipo_usuario'))
        tipos=TIPO_USUARIO_CHOICES
        total = DatosEncuestasResueltas.objects.filter(id_encuesta=pk).count()
        data=[]
        for i in instance:
            for tipo in tipos:
                if i['tipo_usuario'] == tipo[0]:
                    data.append({'nombre':tipo[1],'total':i['cuenta']})
                    print(data)
                    break


        
                #print(tipo)
        return Response({'success':True,
                         'detail':'Se encontraron los siguientes registros.',
                         'data':{'registros':data,'total':total}},status=status.HTTP_200_OK)
    

class ConteoEncuestasPorGenero(generics.ListAPIView):
    queryset = DatosEncuestasResueltas.objects.all()

    def get(self, request,pk):
        instance = DatosEncuestasResueltas.objects.filter(id_encuesta=pk).values('cod_sexo').annotate(cuenta=Count('cod_sexo'))
        datos_nulos = DatosEncuestasResueltas.objects.filter(id_encuesta=pk, cod_sexo__isnull=True).count()
        total = DatosEncuestasResueltas.objects.filter(id_encuesta=pk).count()
        #print(datos_nulos)
        data=[]
        for i in instance:
            print(i)
            if i['cod_sexo']:
                sexo = Sexo.objects.filter(cod_sexo=i['cod_sexo']).first()
                print(sexo.nombre)
                data.append({'nombre':sexo.nombre,'total':i['cuenta']})
        data.append({'nombre':'NULOS','total':datos_nulos})
        return Response({'success':True,
                         'detail':'Se encontraron los siguientes registros.',
                         'data':{'registros':data,'total':total}},status=status.HTTP_200_OK)
    

class ConteoEncuestasPorRangoEdad(generics.ListAPIView):
    queryset = DatosEncuestasResueltas.objects.all()

    def get(self, request,pk):
        instance = DatosEncuestasResueltas.objects.filter(id_encuesta=pk).values('rango_edad').annotate(cuenta=Count('rango_edad'))
        datos_nulos = DatosEncuestasResueltas.objects.filter(id_encuesta=pk, rango_edad__isnull=True).count()
        #print(datos_nulos)
        total = DatosEncuestasResueltas.objects.filter(id_encuesta=pk).count()
        data=[]
        
        for i in instance:
            print(i)
            for rango in RANGO_EDAD_CHOICES:
                if i['rango_edad'] == rango[0]:
                    data.append({'nombre':rango[1],'total':i['cuenta']})
                    print(data)
                    break
        data.append({'nombre':'NULOS','total':datos_nulos})
        return Response({'success':True,
                         'detail':'Se encontraron los siguientes registros.',
                         'data':{'registros':data,'total':total}},status=status.HTTP_200_OK)
    


#ASIGNACION DE ENCUESTAS


class EncuestasDisponbles(generics.ListAPIView):
    queryset = EncabezadoEncuesta.objects.all()
    serializer_class = EncuestaActivaGetSerializer
    def get(self, request, *args, **kwargs):
        instance = EncabezadoEncuesta.objects.filter(activo=True)
        serializer = self.serializer_class(instance,many=True)
        
        if not instance:
            raise NotFound("No existen encuentas registrados en el sistema.")

        return Response({'success':True,
                         'detail':'Se encontraron los siguientes registros.',
                         'data':serializer.data},status=status.HTTP_200_OK)

class AsignacionEncuestaCreate(generics.CreateAPIView):
    queryset = AlertasGeneradas.objects.all()
    serializer_class = AlertasGeneradasEncuestaPostSerializer
    serialier_asignacion = AsignarEncuestaPostSerializer
    def post(self,request):
        data_in = request.data
        data_alerga_generada={}
        programada = ConfiguracionClaseAlerta.objects.filter(cod_clase_alerta='Gst_AsigE').first()

        if not programada:
            raise NotFound("No existe la alerta") 
        data_alerga_generada['nombre_clase_alerta']=programada.nombre_clase_alerta
   
  
        data_alerga_generada['mensaje'] = programada.mensaje_base_dia#VALIDAR CAMPO <1000


        # if programada.complemento_mensaje:
        #     data_alerga_generada['mensaje']+=" "+programada.complemento_mensaje
        
    
        #FIN
        data_alerga_generada['cod_categoria_alerta']=programada.cod_categoria_clase_alerta
        data_alerga_generada['nivel_prioridad']=programada.nivel_prioridad
    
        data_alerga_generada['id_modulo_generador'] = 167

        data_alerga_generada['envio_email']=programada.envios_email
        data_alerga_generada['id_elemento_implicado']=data_in['id_encuesta']
        
        serializer = self.serializer_class(data=data_alerga_generada)
        serializer.is_valid(raise_exception=True)
        instance=serializer.save()


        bandejas_notificaciones=BandejaAlertaPersona.objects.filter(id_persona=data_in['id_persona']).first()
        if bandejas_notificaciones:
            #print(bandejas_notificaciones.id_persona.id_persona)
                alerta_bandeja={}
                alerta_bandeja['leido']=False
                alerta_bandeja['archivado']=False
                email_persona=bandejas_notificaciones.id_persona
                #print("HOLAAAAAAAAAAAAAAAAAAA SI ENTRO ACA")
                print( programada.envios_email)
                if programada.envios_email:
                    if  email_persona and email_persona.email:
                        alerta_bandeja['email_usado'] = email_persona.email
                        subject = programada.nombre_clase_alerta
                        
                        template = "alerta.html"

                        context = {'Nombre_alerta':programada.nombre_clase_alerta,'primer_nombre': email_persona.primer_nombre,"mensaje":data_alerga_generada['mensaje']}
                        template = render_to_string((template), context)
                        email_data = {'template': template, 'email_subject': subject, 'to_email':email_persona.email}
                        Util.send_email(email_data)
                        alerta_bandeja['fecha_envio_email']=datetime.now()

                    else:
                        alerta_bandeja['email_usado'] = None
                else:
                    alerta_bandeja['email_usado'] = None

                alerta_bandeja['id_alerta_generada']=instance.id_alerta_generada
                alerta_bandeja['id_bandeja_alerta_persona']=bandejas_notificaciones.id_bandeja_alerta
                
                #print(alerta_bandeja)
                
                serializer_alerta_bandeja=AlertasBandejaAlertaPersonaPostSerializer(data=alerta_bandeja)
                bandejas_notificaciones.pendientes_leer=True
                bandejas_notificaciones.save()
                serializer_alerta_bandeja.is_valid(raise_exception=True)
                instance_alerta_bandeja=serializer_alerta_bandeja.save()
                print(serializer_alerta_bandeja.data)

                data_asignacion={}
                data_asignacion['id_encuesta']=data_in['id_encuesta']
                data_asignacion['id_persona']=data_in['id_persona']
                data_asignacion['id_alerta_generada']=instance.id_alerta_generada
                #raise ValidationError(instance.id_alerta_generada)
                serializer2 = self.serialier_asignacion(data=data_asignacion)
                serializer2.is_valid(raise_exception=True)
                instance2=serializer2.save()
        else:
             raise NotFound("Este usuario no cuenta con bandeja,comuniquese con soporte.")
        return Response({'success':True,
                         'detail':'Se encontraron los siguientes registros.',
                         'data':serializer2.data},status=status.HTTP_200_OK)


class EncuestasAsignadasGet(generics.ListAPIView):
    queryset = AsignarEncuesta.objects.all()
    serializer_class = AsignarEncuestaGetSerializer
    def get(self, request,enc):
        instance = AsignarEncuesta.objects.filter(id_encuesta=enc)
        serializer = self.serializer_class(instance,many=True)
        
        if not instance:
            raise NotFound("No existen encuentas registrados en el sistema.")

        return Response({'success':True,
                         'detail':'Se encontraron los siguientes registros.',
                         'data':serializer.data},status=status.HTTP_200_OK)
    


class DeleteAsignacion(generics.DestroyAPIView):
    serializer_class=AsignarEncuestaGetSerializer
    queryset=AsignarEncuesta.objects.all()
    
    def delete(self, request, pk):
      
        instance = self.queryset.filter(id_asignar_encuesta=pk).first()

        if not instance:
            raise NotFound("Dato no encontrado.")
        
        previus = copy.copy(instance)  

        alerta_generada = AlertasGeneradas.objects.filter(id_alerta_generada=instance.id_alerta_generada.id_alerta_generada).first()


        bandeja = AlertasBandejaAlertaPersona.objects.filter(id_alerta_generada=instance.id_alerta_generada).first()

        #print(alerta_generada)
        #print(bandeja)
        if alerta_generada:
            alerta_generada.delete()

        if bandeja:
            bandeja.delete()

        instance.delete()
        serializer = self.serializer_class(previus)
       
        
        return Response({'success':True,
                         'detail':'Se elimino correctamente los siguientes registros.',
                         'data':serializer.data},status=status.HTTP_200_OK)
    

class EncuestasAsignadasUsuarioGet(generics.ListAPIView):
    queryset = AsignarEncuesta.objects.all()
    serializer_class = AsignarEncuestaGetSerializer
    def get(self, request,pk):
        instance = AsignarEncuesta.objects.filter(id_persona=pk)
        serializer = self.serializer_class(instance,many=True)
        
        if not instance:
            raise NotFound("No existen encuentas registrados en el sistema.")

        return Response({'success':True,
                         'detail':'Se encontraron los siguientes registros.',
                         'data':serializer.data},status=status.HTTP_200_OK)
    
class GetPersonasByFilters(generics.ListAPIView):
    serializer_class = PersonasFilterEncuestaSerializer
    queryset = Personas.objects.all()

    def get(self,request,tip):
        filter = {}
        print(tip)
        for key,value in request.query_params.items():
            if key in ['tipo_documento','numero_documento','primer_nombre','primer_apellido','razon_social','nombre_comercial']:
                if key in ['primer_nombre','primer_apellido','razon_social','nombre_comercial']:
                    if value != "":
                        filter[key+'__icontains']=  value
                elif key == "numero_documento":
                    if value != "":
                        filter[key+'__icontains'] = value
                else:
                    if value != "":
                        filter[key] = value
        #filter['tipo_persona'] = ti               
        personas = self.queryset.all().filter(**filter)
        
        serializer = self.serializer_class(personas, many=True)
        data =[]
        for ser in serializer.data:
            if ser['usuario'] == tip:
                data.append(ser)
           
        return Response({'success':True, 'detail':'Se encontraron las siguientes personas que coinciden con los criterios de búsqueda', 'data':data}, status=status.HTTP_200_OK)
