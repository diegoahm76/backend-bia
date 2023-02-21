from rest_framework import generics,status
from rest_framework.response import Response
from conservacion.serializers.mezclas_serializers import (
    MezclasSerializador,
    MezclasPutSerializador,
    MezclasGetListSerializador
)
from conservacion.models.mezclas_models import Mezclas
from rest_framework.permissions import IsAuthenticated

class CrearMezcla(generics.CreateAPIView):
    serializer_class = MezclasSerializador
    queryset = Mezclas.objects.all()
    permission_classes = [IsAuthenticated]
    
    def post(self,request):
        data = request.data
        serializador = self.serializer_class(data=data)
        serializador.is_valid(raise_exception=True)
        serializador.save()
        return Response ({'success':True,'detail':'Se ha creado la mezcla correctamente'}, status=status.HTTP_201_CREATED)

class ActualizarMezcla(generics.RetrieveUpdateAPIView):
    serializer_class = MezclasPutSerializador
    queryset = Mezclas.objects.all()
    permission_classes = [IsAuthenticated]

    def put(self, request, id_mezcla):
        mezcla = self.queryset.all().filter(id_mezcla=id_mezcla).first()

        if mezcla:
            if mezcla.item_ya_usado:
                return Response({'success':False, 'detail':'Esta mezcla ya está siendo usada, por lo cual no es actualizable'}, status=status.HTTP_403_FORBIDDEN)

            serializer = self.serializer_class(mezcla, data=request.data, many=False)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'success':True, 'detail':'Registro actualizado exitosamente'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'success': False, 'detail': 'No existe la mezcla'}, status=status.HTTP_404_NOT_FOUND)

class EliminarMezcla(generics.DestroyAPIView):
    serializer_class = MezclasSerializador
    queryset = Mezclas.objects.all()
    permission_classes = [IsAuthenticated]

    def delete(self, request, id_mezcla):
        mezcla = self.queryset.all().filter(id_mezcla=id_mezcla).first()
        if mezcla:
            if mezcla.item_ya_usado:
                return Response({'success':False, 'detail':'Esta mezcla ya está siendo usada, no se puede eliminar'}, status=status.HTTP_403_FORBIDDEN)

            mezcla.delete()
            return Response({'success': True, 'detail': 'Esta mezcla ha sido eliminada exitosamente'}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'detail':'No existe la mezcla'}, status=status.HTTP_404_NOT_FOUND)

class GetListMezclas(generics.ListAPIView):
    serializer_class = MezclasGetListSerializador
    queryset = Mezclas.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        mezclas = self.queryset.all()
        serializador = self.serializer_class(mezclas,many=True)
        
        return Response ({'success':True, 'detail':'Las mezclas registradas actualmente son las siguientes', 'data':serializador.data}, status=status.HTTP_200_OK)