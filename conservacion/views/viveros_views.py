from rest_framework import generics, status
from rest_framework.views import APIView
from seguridad.utils import Util  
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
from datetime import timezone
import copy

from seguridad.models import Personas
from conservacion.models.viveros_models import (
    Vivero,
    HistorialAperturaViveros,
    HistorialCuarentenaViveros
)
from conservacion.serializers.viveros_serializers import (
    ViveroSerializer,
    ActivarDesactivarSerializer,
    ViveroPostSerializer
)

class DeleteVivero(generics.RetrieveDestroyAPIView):
    serializer_class = ViveroSerializer
    queryset = Vivero.objects.all()

    def delete(self, request, id_vivero):
        vivero = Vivero.objects.filter(id_vivero=id_vivero).first()
        if not vivero:
            return Response({'success': False, 'detail': 'No se encontró ningún vivero con el id_vivero enviado'}, status=status.HTTP_404_NOT_FOUND)
        if vivero.en_funcionamiento != None:
            return Response({'success': False, 'detail': 'No se puede eliminar un vivero que ha tenido una apertura'}, status=status.HTTP_403_FORBIDDEN)
        vivero.delete()
        return Response({'success': True, 'detail': 'Se ha eliminado correctamente este vivero'}, status=status.HTTP_204_NO_CONTENT)

class AbrirCerrarVivero(generics.RetrieveUpdateAPIView):
    serializer_class = ActivarDesactivarSerializer
    queryset = Vivero.objects.all()

    def put(self, request, id_vivero):
        data = request.data
        persona = request.user.persona.id_persona
        print(persona)
        vivero = Vivero.objects.filter(id_vivero=id_vivero).first()
        if not vivero:
            return Response({'success': False, 'detail': 'No se encontró ningún vivero con el parámetro ingresado'}, status=status.HTTP_404_NOT_FOUND)
       
        match data['accion']:
            case 'Abrir':
                if vivero.en_funcionamiento == None:
                    if vivero.id_viverista_actual == None:
                        return Response({'success': False, 'detail': 'No se puede abrir un vivero sin un viverista'}, status=status.HTTP_403_FORBIDDEN)
                    data['fecha_ultima_apertura'] = datetime.now()
                    data['en_funcionamiento'] = True
                    data['item_ya_usado'] = True
                    data['id_persona_abre'] = persona
                    serializer = self.serializer_class(vivero, data=data, many=False)
                    serializer.is_valid(raise_exception=True)
                    print('data validada: ',serializer.validated_data.get('justificacion'))
                    serializer.save()
                    return Response({'success': True, 'detail': 'Acción realizada correctamente'}, status=status.HTTP_201_CREATED)
                else:
                    if not vivero.fecha_cierre_actual:
                        return Response({'success': False, 'detail': 'No se puede abrir un vivero si no se encuentra actualmente cerrado'}, status=status.HTTP_400_BAD_REQUEST)
                    data['fecha_ultima_apertura'] = datetime.now()
                    data['en_funcionamiento'] = True
                    data['item_ya_usado'] = True
                    serializer = self.serializer_class(vivero, data=data, many=False)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    return Response({'success': True, 'detail': 'Acción realizada correctamente'}, status=status.HTTP_201_CREATED)
            
            case 'Cerrar':
                if not vivero.fecha_cierre_actual:
                    return Response({'success': False, 'detail': 'No se puede abrir un vivero si no se encuentra actualmente cerrado'}, status=status.HTTP_400_BAD_REQUEST)
                data['fecha_ultima_apertura'] = datetime.now()
                data['en_funcionamiento'] = True
                data['item_ya_usado'] = True
                serializer = self.serializer_class(vivero, data=data, many=False)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response({'success': True, 'detail': 'Acción realizada correctamente'}, status=status.HTTP_201_CREATED)
            case _:
                return Response({'success': False, 'detail': 'Debe enviar una acción válida'}, status=status.HTTP_400_BAD_REQUEST)

class CreateViveros(generics.CreateAPIView):
    serializer_class = ViveroPostSerializer
    queryset = Vivero.objects.all()
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        data = request.data
        persona = request.user.persona.id_persona
        data['id_persona_crea'] = persona
        
        # VALIDAR ASIGNACIÓN VIVERISTA
        viverista = data.get('id_viverista_actual')
        if viverista:
            viverista_existe = Personas.objects.filter(id_persona=viverista)
            if not viverista_existe:
                return Response({'status':False, 'detail':'Debe elegir un viverista que exista'}, status=status.HTTP_400_BAD_REQUEST)
            data['fecha_inicio_viverista_actual'] = datetime.now()
        
        serializador = self.serializer_class(data=data)
        serializador.is_valid(raise_exception=True)
        serializador.save()
        
        return Response({'success':True, 'detail':'Se ha creado el vivero', 'data':serializador.data}, status=status.HTTP_201_CREATED)
class GetViveroByPk(generics.RetrieveAPIView):
    serializer_class=ViveroSerializer
    queryset=Vivero.objects.all()

class FilterViverosByNombreAndMunicipioForCuarentena(generics.ListAPIView):
    serializer_class=ViveroSerializer
    queryset=Vivero.objects.all()
    def get(self,request):
        filter={}
        for key,value in request.query_params.items():
            if key in ['nombre','cod_municipio']:
                if key != 'cod_municipio':
                    filter[key+'__icontains']=value
                else:
                    filter[key]=value
        vivero=Vivero.objects.filter(**filter).filter(Q(en_funcionamiento=True) | Q(vivero_en_cuarentena=True))
        if vivero:
            serializer=self.serializer_class(vivero,many=True)
            return Response({'success':True,'detail':'Se encontraron viveros','data':serializer.data},status=status.HTTP_200_OK)
        else: 
            return Response({'success':False,'detail':'No se encontraron viveros'},status=status.HTTP_404_NOT_FOUND)
        
        
class FilterViverosByNombreAndMunicipioForAperturaCierres(generics.ListAPIView):
    serializer_class=ViveroSerializer
    queryset=Vivero.objects.all()
    def get(self,request):
        filter={}
        for key,value in request.query_params.items():
            if key in ['nombre','cod_municipio']:
                if key != 'cod_municipio':
                    filter[key+'__icontains']=value
                else:
                    filter[key]=value
        vivero=Vivero.objects.filter(**filter).filter( Q(activo=True) & (Q(vivero_en_cuarentena=False) | Q(vivero_en_cuarentena= None)))
        if vivero:
            serializer=self.serializer_class(vivero,many=True)
            return Response({'success':True,'detail':'Se encontraron viveros','data':serializer.data},status=status.HTTP_200_OK)
        else: 
            return Response({'success':False,'detail':'No se encontraron viveros'},status=status.HTTP_404_NOT_FOUND)

        
