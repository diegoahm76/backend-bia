
import copy
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from gestion_documental.models.encuencas_models import DatosEncuestasResueltas, EncabezadoEncuesta, OpcionesRta, PreguntasEncuesta, RespuestaEncuesta
from gestion_documental.serializers.encuentas_serializers import DatosEncuestasResueltasConteoSerializer, DatosEncuestasResueltasCreateSerializer, EncabezadoEncuestaCreateSerializer, EncabezadoEncuestaDeleteSerializer, EncabezadoEncuestaGetDetalleSerializer, EncabezadoEncuestaGetSerializer, EncabezadoEncuestaUpdateSerializer, EncuestaActivaGetSerializer, OpcionesRtaCreateSerializer, OpcionesRtaDeleteSerializer, OpcionesRtaGetSerializer, OpcionesRtaUpdateSerializer, PersonaRegistradaEncuentaGet, PreguntasEncuestaCreateSerializer, PreguntasEncuestaDeleteSerializer, PreguntasEncuestaGetSerializer, PreguntasEncuestaUpdateSerializer,RespuestaEncuestaCreateSerializer
from django.db.models import Max
from datetime import datetime
from django.db import transaction

from transversal.admin import PersonasAdmin
from transversal.models.personas_models import Personas
   
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
                        response_pregunta=crear_pregunta.crear_pregunta(data_pregunta)
                        if response_pregunta.status_code!=status.HTTP_201_CREATED:
                            return response_pregunta
                        response_preguntas.append(response_pregunta.data['data'])

                response_encabezado=serializer.data
                response_encabezado['preguntas_encuesta']=response_preguntas
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
                    respuesta_pregunta=eliminar_pregunta.eliminar(ids)
                    if respuesta_pregunta.status_code != status.HTTP_200_OK:
                        return respuesta_pregunta
           
                for pre in data_in['preguntas']:

                    if 'id_pregunta_encuesta' in pre:
                        if pre:
                           
                            #print(pre)
                            response_pregunta=actualizar_pregunta.actualizar_pregunta(pre,pre['id_pregunta_encuesta'])
                            if response_pregunta.status_code!=status.HTTP_200_OK:
                                return response_pregunta  
                            data_response_pregunta.append(response_pregunta.data['data'])

                    else:
                        id_encabezado=instance.id_encabezado_encuesta
                        response_pregunta=crear_pregunta.crear_pregunta({**pre,"id_encabezado_encuesta":id_encabezado})
                        if response_pregunta.status_code!=status.HTTP_201_CREATED:
                            return response_pregunta    
                        data_response_pregunta.append(response_pregunta.data['data'])
                    #print(pre)
               

            response_data=serializer.data
            response_data['preguntas_encuesta']=data_response_pregunta
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
    
    def crear_pregunta(self,data):
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
                        
                        response_pregunta=crear_opcion.crear_opciones_rta({**opc_rta,"id_pregunta":id_pregunta})
                        if response_pregunta.status_code!=status.HTTP_201_CREATED:
                            return response_pregunta   
                        #print (opc_rta)
                        data_ops.append(response_pregunta.data['data'])
            data_response=serializer.data
            data_response['opciones_rta']=data_ops
            return Response({'success':True,'detail':'Se crearon los registros correctamente','data':data_response},status=status.HTTP_201_CREATED)
        except ValidationError as e:       
            raise ValidationError(e.detail)

    def post(self,request):
        data_in = request.data
        response=self.crear_pregunta(data_in)
        return response


class PreguntasEncuestaUpdate(generics.UpdateAPIView):
    queryset = PreguntasEncuesta.objects.all()
    serializer_class = PreguntasEncuestaUpdateSerializer
    permission_classes = [IsAuthenticated]
    def actualizar_pregunta(self,data,pk):
        data_in=data
        instance = PreguntasEncuesta.objects.filter(id_pregunta_encuesta=pk).first()

        if not instance:
            raise NotFound("No existe encuentas asociada e esta id")
        

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
                            
                            response_pregunta=actualizar_opcion.actualizar_opciones_rta({**opc_rta},opc_rta['id_opcion_rta'])
                            if response_pregunta.status_code!=status.HTTP_200_OK:
                                return response_pregunta   
                            
                            data_ops.append(response_pregunta.data['data'])

                        else:
                            response_pregunta=crear_opcion.crear_opciones_rta({**opc_rta,"id_pregunta":id_pregunta})
                            if response_pregunta.status_code!=status.HTTP_201_CREATED:
                                return response_pregunta   
                            
                            data_ops.append(response_pregunta.data['data'])
                            
                    for delete in id_opciones_no_en_json:
                        datos_eliminados_response = eliminar_opcion.eliminar(delete)
                        if datos_eliminados_response.status_code != status.HTTP_200_OK:
                            return datos_eliminados_response
                        #print (datos_eliminados_response)
            data_response=serializer.data
            data_response['opciones_rta']=data_ops
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
    def eliminar(self,pk):
        instance = PreguntasEncuesta.objects.filter(id_pregunta_encuesta=pk).first()
        if not instance:
            raise NotFound("No existe pregunta asociada a esta id.")
        serializer =PreguntasEncuestaDeleteSerializer(instance)
        instance.delete()
        return Response({
            "success": True,
            "detail": "Se eliminó la pregunta correctamente",
            "data": serializer.data
        }, status=status.HTTP_200_OK)
    def delete(self, request,pk):
        response=self.eliminar(pk)
        return response
    
class OpcionesRtaCreate(generics.CreateAPIView):
    serializer_class = OpcionesRtaCreateSerializer
    permission_classes = [IsAuthenticated]
    queryset = OpcionesRta.objects.all()
    
    def crear_opciones_rta(self,data):
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
            return Response({'success':True,'detail':'Se crearon los registros correctamente','data':serializer.data},status=status.HTTP_201_CREATED)
        except ValidationError as e:       
            raise ValidationError(e.detail)

    def post(self,request):
        data_in = request.data
        response=self.crear_opciones_rta(data_in)
        return response

class OpcionesRtaUpdate(generics.UpdateAPIView):
    queryset = OpcionesRta.objects.all()
    serializer_class = OpcionesRtaUpdateSerializer
    permission_classes = [IsAuthenticated]
    def actualizar_opciones_rta(self,data,pk):
        data_in=data
        instance = OpcionesRta.objects.filter(id_opcion_rta=pk).first()

        if not instance:
            raise NotFound("No existe opcion asociada e esta id")
        try:
 
            serializer = OpcionesRtaUpdateSerializer(instance, data=data_in,partial=True)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()
            return Response({
                "success": True,
                "detail": "Se actualizó el encabezado de encuesta correctamente",
                "data": serializer.data
            }, status=status.HTTP_200_OK)
        except ValidationError as e:       
            raise ValidationError(e.detail)


    def put(self, request, pk):

        response =self.actualizar_opciones_rta(request.data,pk)
        return response

class OpcionesRtaDelete(generics.DestroyAPIView):
    queryset = OpcionesRta.objects.all()
    serializer_class = OpcionesRtaDeleteSerializer
    permission_classes = [IsAuthenticated]
    def eliminar(self,pk):
        instance = OpcionesRta.objects.filter(id_opcion_rta=pk).first()
        if not instance:
            raise NotFound("No existe pregunta asociada a esta id.")
        serializer =OpcionesRtaDeleteSerializer(instance)
        instance.delete()
        return Response({
            "success": True,
            "detail": "Se eliminó la opcion correctamente",
            "data": serializer.data
        }, status = status.HTTP_200_OK)
    def delete(self, request,pk):
        response=self.eliminar(pk)
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
        serializer = self.serializer_class(instance)
        cantidad_encuestas_resueltas = DatosEncuestasResueltas.objects.filter(id_encuesta=pk).count()

        id_preguntas=[]
        for encuenta in instance:
            respuestas_contestadas = RespuestaEncuesta.objects.filter(id_encuesta_resuelta=encuenta.id_datos_encuesta_resuelta)
            for respuesta in respuestas_contestadas:
                print(respuesta)
                print(respuesta.id_opcion_pregunta_encuesta.opcion_rta)
                id_preguntas.append(respuesta.id_opcion_pregunta_encuesta.id_pregunta.id_pregunta_encuesta)
            print("################")
        print(cantidad_encuestas_resueltas)
        print(id_preguntas)
        if not instance:
            raise NotFound("No existen encuentas registrados en el sistema.")
        
        serializer=self.serializer_class(instance,many=True)
            
     
        return Response({'success':True,
                         'detail':'Se encontraron los siguientes registros.',
                         'data':serializer.data},status=status.HTTP_200_OK)