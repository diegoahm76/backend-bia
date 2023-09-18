
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from gestion_documental.models.plantillas_models import AccesoUndsOrg_PlantillaDoc, PlantillasDoc
from gestion_documental.models.trd_models import TipologiasDoc
from gestion_documental.serializers.plantillas_serializers import AccesoUndsOrg_PlantillaDocCreateSerializer, PlantillasDocCreateSerializer, TipologiasDocSerializerGetSerializer
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
import os
from rest_framework.permissions import IsAuthenticated
class PlantillasDocCreate(generics.CreateAPIView):
    queryset = PlantillasDoc.objects.all()
    serializer_class = PlantillasDocCreateSerializer
    permission_classes = [IsAuthenticated]
    def obtener_extension_archivo(self,archivo):
        _, extension = os.path.splitext(archivo.name)
        return extension

    def post(self,request):
        
        usuario = request.user.persona.id_persona
        
        data_in = request.data.copy()
        data_in['id_persona_crea_plantilla']=usuario
        #raise ValidationError(data_in['nombre'])
        print(data_in)
        #archivos =request.FILES.getlist('evidencia')
        archivo = request.FILES.get('archivo')
        nombre_archivo = request.data.get('nombre_archivo')
                
        if not archivo:
            raise ValidationError("No se ha proporcionado ningún archivo.")

        if not nombre_archivo:
            raise ValidationError("El archivo debe tener un nombre.")
        #FUNCION GENERADORA DE RUTAS DE ARCHIVOS
        

       
        try:
            serializer = self.serializer_class(data=data_in)
            serializer.is_valid(raise_exception=True)
            instance=serializer.save()
            return Response({'success':True,'detail':'Se crearon los registros correctamente','data':serializer.data},status=status.HTTP_201_CREATED)
        except ValidationError as e:       
            raise ValidationError(e.detail)
        
class TipologiasDocGetActivo(generics.ListAPIView):
    serializer_class = TipologiasDocSerializerGetSerializer
    queryset =TipologiasDoc.objects.all()

    def get (self, request):
        instance = TipologiasDoc.objects.filter(activo=True)

        if not instance:
            raise NotFound("No existen registros")

        serializador = self.serializer_class(instance,many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializador.data}, status=status.HTTP_200_OK)
    

class AccesoUndsOrg_PlantillaDocCreate(generics.CreateAPIView):
    serializer_class = AccesoUndsOrg_PlantillaDocCreateSerializer
    permission_classes = [IsAuthenticated]
    queryset = AccesoUndsOrg_PlantillaDoc.objects.all()
    
    def crear_acceso(self,data):
        try:
           

            data_in=data
            serializer = AccesoUndsOrg_PlantillaDocCreateSerializer(data=data_in)
            serializer.is_valid(raise_exception=True)
            instance=serializer.save()
            
            return Response({'success':True,'detail':'Se crearon los registros correctamente','data':serializer.data},status=status.HTTP_201_CREATED)
        except ValidationError as e:       
            raise ValidationError(e.detail)

    def post(self,request):
        data_in = request.data
        response=self.crear_acceso(data_in)
        return response