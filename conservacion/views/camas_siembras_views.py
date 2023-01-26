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
    CamasGerminacionVivero,
    Siembras,
)
from conservacion.models.viveros_models import (
    Vivero,
)
from conservacion.serializers.viveros_serializers import (
    ViveroSerializer,
)
from conservacion.serializers.camas_siembras_serializers import (
    CamasGerminacionPost,
    CreateSiembrasSerializer,
    GetNumeroLoteSerializer
)
from conservacion.utils import UtilConservacion

class CamasGerminacion(generics.UpdateAPIView):
    serializer_class = CamasGerminacionPost
    queryset = CamasGerminacionVivero.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self, request, id_vivero_procesar):
        datos_ingresados = request.data
        # SE VALIDA QUE EL VIVERO INGRESADO EXISTA
        instancia_vivero_ingresado = Vivero.objects.filter(id_vivero=id_vivero_procesar).first()
        if not instancia_vivero_ingresado:
            return Response({'success':False,'detail':'El vivero ingresado no existe'},status=status.HTTP_400_BAD_REQUEST)
        # SE VALIDA QUE EL DATO COMÚN SEA CORRECTO EN TODOS LOS ELEMENTOS (SE HAYA PUESTO EL MISMO VIVERO QUE CADA CAMA)
        if datos_ingresados == []:
            camas_existentes = CamasGerminacionVivero.objects.filter(id_vivero=id_vivero_procesar)
            for i in camas_existentes:
                if ((i.item_activo != False) or (i.item_activo != False)):
                    return Response({'success':False,'detail':'No es posible eliminar una cama si está activa o si ya ha sido usada'},status=status.HTTP_400_BAD_REQUEST)
            # SE ELIMINAN LOS ELEMENTOS
            camas_existentes.delete()
            return Response({'success':True,'detail':'Camas de germinación elimanadas con éxito'},status=status.HTTP_200_OK)
        else:
            i['id_vivero'] = id_vivero_procesar
            # SE OBTIENEN LAS CAMAS QUE SE QUIEREN ELIMINAR
            camas_existentes = CamasGerminacionVivero.objects.filter(id_vivero=instancia_vivero_ingresado.id_vivero)
            id_camas_existentes = [i.id_cama_germinacion_vivero for i in camas_existentes]
            id_camas_entrantes = [i['id_cama_germinacion_vivero'] for i in datos_ingresados if i['id_cama_germinacion_vivero'] != None]
            lista_elementos_eliminar = [i for i in id_camas_existentes if i not in id_camas_entrantes]
            # VALIDACIONES COMPLEMENTARIAS DE LOS ELEMENTOS A ELIMINAR
            for i in lista_elementos_eliminar:
                instancia_validacion_camas_germinacion = CamasGerminacionVivero.objects.filter(id_cama_germinacion_vivero=i).first()
                if ((instancia_validacion_camas_germinacion.item_activo != False) or (instancia_validacion_camas_germinacion.item_activo != False)):
                    return Response({'success':False,'detail':'No es posible eliminar una cama si está activa o si ya ha sido usada'},status=status.HTTP_400_BAD_REQUEST)
            # SE VALIDAN LOS ELEMENTOS QUE SE QUIEREN ACTUALIZAR Y LOS QUE SE QUIEREN CREAR
            lista_elementos_crear = []
            lista_elementos_actualizar = []
            for i in datos_ingresados:
                # Se valida cual se quiere actualizar y cual se quiere crear
                if i['id_cama_germinacion_vivero'] == None:
                    lista_elementos_crear.append(i)
                else:
                    instancia_validacion_camas_germinacion = CamasGerminacionVivero.objects.filter(id_cama_germinacion_vivero=i['id_cama_germinacion_vivero']).first()
                    if instancia_validacion_camas_germinacion.nombre != i['nombre']:
                        if instancia_validacion_camas_germinacion.item_ya_usado != False:
                            return Response({'success':False,'detail':'No es posible modificar el nombre a una cama que tenga el campo (item_ya_usado) en (true)'},status=status.HTTP_200_OK)
                    lista_elementos_actualizar.append(i)
            # SE CREAN LOS ELEMENTOS
            serializer_crear = self.serializer_class(data=lista_elementos_crear, many=True)
            serializer_crear.is_valid(raise_exception=True)
            serializer_crear.save()
            # SE ACTUALIZAN LOS ELEMENTOS
            for i in lista_elementos_actualizar:
                instancia_elemento_actualizar = CamasGerminacionVivero.objects.filter(id_cama_germinacion_vivero=i['id_cama_germinacion_vivero']).first()
                serializer_actualizar = self.serializer_class(instancia_elemento_actualizar, data=i)
                serializer_actualizar.is_valid(raise_exception=True)
                serializer_actualizar.save()
            # SE ELIMINAN LOS ELEMENTOS
            instancia_elementos_eliminar = CamasGerminacionVivero.objects.filter(id_cama_germinacion_vivero__in = lista_elementos_eliminar)
            instancia_elementos_eliminar.delete()
            return Response({'success':True,'detail':'Camas de germinación creadas o actualizadas con éxito'},status=status.HTTP_200_OK)
        id_vivero = [i['id_vivero'] for i in datos_ingresados]
        if len(set(id_vivero)) > 1:
            return Response({'success':False,'detail':'Verifique que todas las camas ingresadas pertenezcan al mismo vivero'},status=status.HTTP_200_OK)
        instancia_vivero_ingresado = Vivero.objects.filter(id_vivero=id_vivero[0]).first()
        # SE OBTIENEN LAS CAMAS QUE SE QUIEREN ELIMINAR
        camas_existentes = CamasGerminacionVivero.objects.filter(id_vivero=instancia_vivero_ingresado.id_vivero)
        id_camas_existentes = [i.id_cama_germinacion_vivero for i in camas_existentes]
        id_camas_entrantes = [i['id_cama_germinacion_vivero'] for i in datos_ingresados if i['id_cama_germinacion_vivero'] != None]
        lista_elementos_eliminar = [i for i in id_camas_existentes if i not in id_camas_entrantes]
        print(lista_elementos_eliminar)
        # SE VALIDAN LOS ELEMENTOS QUE SE QUIEREN ACTUALIZAR Y LOS QUE SE QUIEREN CREAR
        lista_elementos_crear = []
        lista_elementos_actualizar = []
        for i in datos_ingresados:
            # Se valida cual se quiere actualizar y cual se quiere crear
            if i.get['id_cama_germinacion_vivero'] == None:
                lista_elementos_crear.append(i)
            else:
                lista_elementos_actualizar.append(i)
        # SE CREAN LOS ELEMENTOS
        serializer_crear = self.serializer_class(data=lista_elementos_crear, many=True)
        serializer_crear.is_valid(raise_exception=True)
        serializer_crear.save()
        # SE ACTUALIZAN LOS ELEMENTOS
        for i in lista_elementos_actualizar:
            instancia_elemento_actualizar = CamasGerminacionVivero.objects.filter(id_cama_germinacion_vivero=i['id_cama_germinacion_vivero']).first()
            serializer_actualizar = self.serializer_class(instancia_elemento_actualizar, data=lista_elementos_crear)
            serializer_actualizar.is_valid(raise_exception=True)
            serializer_actualizar.save()
        # SE ELIMINAN LOS ELEMENTOS
        instancia_elementos_eliminar = CamasGerminacionVivero.objects.filter(id_cama_germinacion_vivero__in = lista_elementos_eliminar)
        instancia_elementos_eliminar.delete()
        return Response({'success':True,'detail':'Camas de germinación creadas con éxito'},status=status.HTTP_200_OK)


class FilterViverosByNombreAndMunicipio(generics.ListAPIView):
    serializer_class = ViveroSerializer
    queryset = Vivero.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self,request):
        filter = {}
        for key, value in request.query_params.items():
            if key in ['nombre','cod_municipio']:
                if key != 'cod_municipio':
                    filter[key + '__icontains'] = value
                else:
                    filter[key] = value
        vivero = Vivero.objects.filter(~Q(fecha_ultima_apertura=None) & (Q(vivero_en_cuarentena=False) | Q(vivero_en_cuarentena=None)) & Q(fecha_cierre_actual=None)).filter(**filter)
        if vivero:
            serializer = self.serializer_class(vivero, many=True)
            return Response({'success': True, 'detail': 'Se encontraron viveros', 'data': serializer.data}, status=status.HTTP_200_OK)
        else: 
            return Response({'success': False, 'detail': 'No se encontraron viveros'}, status=status.HTTP_404_NOT_FOUND)
        
class CreateSiembraView(generics.CreateAPIView):
    serializer_class = CreateSiembrasSerializer
    queryset = Siembras.objects.all()

    def post(self, request):
        siembra_data = request.data
        

        return Response({'success': True, 'detail': 'Siembra creada exitosamente'}, status=status.HTTP_201_CREATED)
