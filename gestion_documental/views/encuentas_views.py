
import copy
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from gestion_documental.models.encuencas_models import EncabezadoEncuesta, OpcionesRta, PreguntasEncuesta
from gestion_documental.serializers.encuentas_serializers import EncabezadoEncuestaCreateSerializer, EncabezadoEncuestaDeleteSerializer, EncabezadoEncuestaGetSerializer, OpcionesRtaCreateSerializer, PreguntasEncuestaCreateSerializer
from django.db.models import Max
class EncabezadoEncuestaCreate(generics.CreateAPIView):
    serializer_class = EncabezadoEncuestaCreateSerializer
    permission_classes = [IsAuthenticated]
    queryset = EncabezadoEncuesta.objects.all()
    
    def post(self,request):
        data_in = request.data
        usuario = request.user.id_usuario
        try:
            data_in['id_persona_ult_config_implement']=usuario
            serializer = self.serializer_class(data=data_in)
            serializer.is_valid(raise_exception=True)
            instance=serializer.save()
           
            return Response({'success':True,'detail':'Se crearon los registros correctamente','data':serializer.data},status=status.HTTP_201_CREATED)
        except ValidationError as e:       
            raise ValidationError(e.detail)
         
class EncabezadoEncuestaCreate(generics.CreateAPIView):
    serializer_class = EncabezadoEncuestaCreateSerializer
    permission_classes = [IsAuthenticated]
    queryset = EncabezadoEncuesta.objects.all()
    
    def post(self,request):
        data_in = request.data
        usuario = request.user.id_usuario
        try:
            data_in['id_persona_ult_config_implement']=usuario
            serializer = self.serializer_class(data=data_in)
            serializer.is_valid(raise_exception=True)
            instance=serializer.save()
            crear_pregunta=PreguntasEncuestaCreate()
            crear_opcion=OpcionesRtaCreate()
            if 'preguntas' in data_in:
            
                data_pregunta={}
                response_preguntas=[]

                for pre in data_in['preguntas']:
                    data_pregunta.clear()
                    
                    data_pregunta={**pre}
                    data_pregunta['id_encabezado_encuesta']=instance.id_encabezado_encuesta
                    #print(data_pregunta)
                    response_pregunta=crear_pregunta.crear_pregunta(data_pregunta)
                    if response_pregunta.status_code!=status.HTTP_201_CREATED:
                        return response_pregunta
                    
                    pregunta=response_pregunta.data['data']
                    #raise ValidationError(str(pregunta))

                    data_preguntas={}
                    if 'opciones_rta' in pre:
                        data_ops=[]
                        data_respuesta={}
                        for op in pre['opciones_rta']:
                            data_respuesta.clear()
                            data_respuesta={**op}
                            data_respuesta['id_pregunta']=pregunta['id_pregunta_encuesta']
                            #print(data_respuesta)
                            response_opcion=crear_opcion.crear_opciones_rta(data_respuesta)
                            if response_opcion.status_code!=status.HTTP_201_CREATED:
                                    return response_opcion
                            data_ops.append(response_opcion.data['data'])
                    
                    data_pregunta=response_pregunta.data['data']
                    data_pregunta['opciones_rta']=data_ops
                    data_copy=copy.copy(data_pregunta)
                    print(data_pregunta)
                    response_preguntas.append(data_copy)
                #raise ValidationError()
                response_encabezado=serializer.data
                response_encabezado['preguntas_encuesta']=response_preguntas
            return Response({'success':True,'detail':'Se crearon los registros correctamente','data':response_encabezado},status=status.HTTP_201_CREATED)
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
            return Response({'success':True,'detail':'Se crearon los registros correctamente','data':serializer.data},status=status.HTTP_201_CREATED)
        except ValidationError as e:       
            raise ValidationError(e.detail)

    def post(self,request):
        data_in = request.data
        response=self.crear_pregunta(data_in)
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
    

class EncabezadoEncuestaDelete(generics.DestroyAPIView):
    queryset = EncabezadoEncuesta.objects.all()
    serializer_class = EncabezadoEncuestaDeleteSerializer

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        self.perform_destroy(instance)
        return Response({
            "success": True,
            "detail": "Se eliminó el encabezado de encuesta correctamente",
            "data": serializer.data
        }, status=status.HTTP_204_NO_CONTENT)