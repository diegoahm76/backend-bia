from rest_framework import generics, status
from rest_framework.views import APIView
from seguridad.utils import Util  
from django.db.models import Q, F, Sum
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
from datetime import timezone
import copy

from seguridad.models import Personas
from conservacion.choices.cod_etapa_lote import cod_etapa_lote_CHOICES
from conservacion.models.siembras_models import (
    CamasGerminacionVivero
)
from conservacion.models.viveros_models import (
    Vivero
)
from conservacion.models.despachos_models import (
    DespachoEntrantes,
    ItemsDespachoEntrante,
    DistribucionesItemDespachoEntrante
)
from conservacion.serializers.despachos_serializers import (
    DespachosEntrantesSerializer,
    ItemsDespachosEntrantesSerializer,
    DistribucionesItemDespachoEntranteSerializer
)
from conservacion.utils import UtilConservacion

class CrearCamasGerminacion(generics.UpdateAPIView):
    serializer_class = DespachosEntrantesSerializer
    queryset = CamasGerminacionVivero.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self, request):
        datos_ingresados = request.data
        id_vivero = [i['id_vivero'] for i in datos_ingresados]
        if len(set(id_vivero)) > 1:
            return Response({'success':False,'detail':'Verifique que todas las camas ingresadas pertenezcan al mismo vivero'},status=status.HTTP_200_OK)
        instancia_vivero_ingresado = Vivero.objects.filter(id_vivero=id_vivero[0]).first()
        camas_existentes = CamasGerminacionVivero.objects.filter()
        lista_elementos_crear = []
        lista_elementos_actualizar = []
        for i in datos_ingresados:
            vivero_ingresado = i.get['id_vivero']
            if not instancia_vivero_ingresado:
                return Response({'success':False,'detail':'En el numero de posición (' + str(i.get['nombre']) + '), el vivero no existe'},status=status.HTTP_200_OK)
            # Se valida cual se quiere actualizar y cual se quiere crear
            if i.get['id_cama_germinacion_vivero'] == None:
                lista_elementos_crear.append(i)
            else:
                lista_elementos_actualizar.append(i)
            # Se valida cual se quiere eliminar
            
        return Response({'success':True,'detail':'Camas de germinación creadas con éxito'},status=status.HTTP_200_OK)
