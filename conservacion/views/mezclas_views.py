from rest_framework import generics,status
from rest_framework.response import Response
from conservacion.serializers.mezclas_serializers import MezclasSerializador
from conservacion.models.mezclas_models import Mezclas

class CrearMezcla(generics.CreateAPIView):
    serializer_class = MezclasSerializador
    queryset = Mezclas.objects.all()
    
    def post(self,request):
        data = request.data
        serialializador= self.serializer_class(data=data,many=False)
        serialializador.is_valid(raise_exception=True)
        serialializador.save()
        return Response ({'success':True,'detail':'Se ha creado la mezcla correctamente'},status=status.HTTP_201_CREATED)
        

