
from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from gestion_documental.models.plantillas_models import PlantillasDoc
from gestion_documental.models.trd_models import TipologiasDoc
from gestion_documental.serializers.plantillas_serializers import PlantillasDocCreateSerializer, TipologiasDocSerializerGetSerializer
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied

class PlantillasDocCreate(generics.CreateAPIView):
    queryset = PlantillasDoc.objects.all()
    serializer_class = PlantillasDocCreateSerializer
    def post(self,request):
        
        usuario = request.user.persona.id_persona
        
        data_in = request.data.copy()
        data_in['id_persona_crea_plantilla']=usuario
        #raise ValidationError(data_in['nombre'])
        print(data_in)
        #archivos =request.FILES.getlist('evidencia')
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