from rest_framework import generics,status
from rest_framework.response import Response
from conservacion.serializers.mezclas_serializers import (
    MezclasSerializador,
    MezclasPutSerializador,
    MezclasGetListSerializador,
    GetItemsSerializador
)
from conservacion.models.mezclas_models import Mezclas, ItemsPreparacionMezcla, PreparacionMezclas
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied

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
            raise NotFound('No existe la mezcla')

class EliminarMezcla(generics.DestroyAPIView):
    serializer_class = MezclasSerializador
    queryset = Mezclas.objects.all()
    permission_classes = [IsAuthenticated]

    def delete(self, request, id_mezcla):
        mezcla = self.queryset.all().filter(id_mezcla=id_mezcla).first()
        if mezcla:
            if mezcla.item_ya_usado:
                raise PermissionDenied('Esta mezcla ya está siendo usada, no se puede eliminar')

            mezcla.delete()
            return Response({'success': True, 'detail': 'Esta mezcla ha sido eliminada exitosamente'}, status=status.HTTP_200_OK)
        else:
            raise NotFound('No existe la mezcla')

class GetListMezclas(generics.ListAPIView):
    serializer_class = MezclasGetListSerializador
    queryset = Mezclas.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        mezclas = self.queryset.all()
        serializador = self.serializer_class(mezclas,many=True)
        
        return Response ({'success':True, 'detail':'Las mezclas registradas actualmente son las siguientes', 'data':serializador.data}, status=status.HTTP_200_OK)

class ItemsMezclaView(generics.ListAPIView):
    serializer_class = GetItemsSerializador

    def get(self, request):
        id_preparacion_mezcla = request.query_params.get('id_preparacion_mezcla')

        if not id_preparacion_mezcla:
            return Response({'success': False, 'detail': 'Debe proporcionar el ID de la preparación de la mezcla.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            preparacion_mezcla = PreparacionMezclas.objects.get(id_preparacion_mezcla=id_preparacion_mezcla)
        except PreparacionMezclas.DoesNotExist:
            return Response({'success': False, 'detail': 'La preparación de la mezcla no existe.'}, status=status.HTTP_404_NOT_FOUND)

        queryset = ItemsPreparacionMezcla.objects.filter(id_preparacion_mezcla=preparacion_mezcla)
        serializer = self.serializer_class(queryset, many=True)
        
        return Response({'success': True, 'detail': 'Se encontraron los siguientes items para la preparación de la mezcla', 'data': serializer.data}, status=status.HTTP_200_OK)