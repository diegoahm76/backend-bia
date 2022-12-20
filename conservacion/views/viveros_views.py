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

from conservacion.models.viveros_models import (
    Vivero,
    HistorialAperturaViveros,
    HistorialCuarentenaViveros
)
from conservacion.serializers.viveros_serializers import (
    ViveroSerializer,
    ActivarDesactivarSerializer,
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
