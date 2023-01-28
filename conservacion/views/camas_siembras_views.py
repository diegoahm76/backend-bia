from rest_framework import generics, status
from rest_framework.views import APIView
from seguridad.utils import Util  
from django.db.models import Q, F, Sum
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, time, timedelta
from datetime import timezone
import copy
import json

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
    GetNumeroLoteSerializer,
    GetBienSembradoSerializer,
    GetCamasGerminacionSerializer
)
from almacen.models.bienes_models import (
    CatalogoBienes
)
from conservacion.models.inventario_models import (
    InventarioViveros
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
                i['id_vivero'] = id_vivero_procesar
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
        
class GetCamasGerminaciones(generics.ListAPIView):
    serializer_class = GetCamasGerminacionSerializer
    queryset = CamasGerminacionVivero.objects.all()

    def get(self, request):
        data = self.get_queryset()
        serializer = self.serializer_class(data, many=True)
        return Response({'success':True, 'detail':'Busqueda exitosa', 'data': serializer.data},status=status.HTTP_200_OK)

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
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data_siembra = json.loads(request.data['data_siembra'])
        data_siembra['ruta_archivo_soporte'] = request.FILES.get('ruta_archivo_soporte')
        
        #VALIDAR QUE NO SEA UNA FECHA SUPERIOR A HOY
        fecha_siembra = data_siembra.get('fecha_siembra')
        fecha_actual = datetime.now()
        fecha_siembra_strptime = datetime.strptime(fecha_siembra, '%Y-%m-%d %H:%M:%S')
        if fecha_siembra_strptime > fecha_actual:
            return Response({'success': False, 'detail': 'La fecha de siembra no puede ser superior a la actual'}, status=status.HTTP_400_BAD_REQUEST)
        
        print(fecha_siembra_strptime.year)
        
        #ASIGNACIÓN NÚMERO LOTE
        lote = Siembras.objects.filter(id_bien_sembrado=data_siembra['material_vegetal'], id_vivero=data_siembra['id_vivero'], agno_lote=fecha_siembra_strptime.year).order_by('-nro_lote').first()
        contador = 0
        if lote:
            contador = lote.nro_lote
        numero_lote = contador + 1
        data_siembra['nro_lote'] = numero_lote
        
        
        #VALIDACIÓN QUE NO SEA UNA FECHA SUPERIOR A 30 DÍAS
        if fecha_siembra_strptime < (fecha_actual - timedelta(days=30)):
            return Response({'success': False, 'detail': 'No se puede crear una siembra con antiguedad mayor a 30 días'}, status=status.HTTP_400_BAD_REQUEST)
        
        #VALIDAR FECHA DISPONIBLE PARA SIEMBRA
        lote_busqueda = InventarioViveros.objects.filter(id_bien=data_siembra['material_vegetal'], id_vivero=data_siembra['id_vivero'], agno_lote=data_siembra['agno_lote']).order_by('-nro_lote').first()
        if lote_busqueda:
            lote_instance = InventarioViveros.objects.filter(nro_lote=lote_busqueda.nro_lote, id_bien=lote_busqueda.id_bien.id_bien, id_vivero=lote_busqueda.id_vivero.id_vivero, agno_lote=lote_busqueda.agno_lote).filter(cod_etapa_lote='G').first()
            print(lote_instance)
            if fecha_siembra_strptime < lote_instance.fecha_ingreso_lote_etapa:
                return Response({'success': False, 'detail': 'No se puede crear una siembra con una fecha anterior a la última siembra registrada'})
        

        


        #VALIDAR QUE EL VIVERO ESTÉ DISPONIBLE PARA SELECCIONAR
        vivero = Vivero.objects.filter(id_vivero=data_siembra['id_vivero']).filter(~Q(fecha_ultima_apertura=None) & (Q(vivero_en_cuarentena=False) | Q(vivero_en_cuarentena=None)) & Q(fecha_cierre_actual=None)).first()
        if not vivero:
            return Response({'success': False, 'detail': 'El vivero seleccionado no cumple los requisitos para que la siembra pueda ser creada'}, status=status.HTTP_400_BAD_REQUEST)
        
        #VALIDAR QUE EL MATERIAL VEGETAL SEA UN BIEN CON LOS REQUISITOS
        bien = CatalogoBienes.objects.filter(id_bien=data_siembra['material_vegetal']).first()
        print('bien: ', bien)
        print('bien.cod_tipo_elemento_vivero: ', bien.cod_tipo_elemento_vivero)
        if not bien.cod_tipo_elemento_vivero =='MV' and not bien.solicitable_vivero == True and not  bien.es_semilla_vivero == False and not bien.nivel_jerarquico == '5':
            return Response({'success': False, 'detail': 'El bien seleccionado no cumple los requisitos para que la siembra pueda ser creada'}, status=status.HTTP_400_BAD_REQUEST)
        
        #VALIDAR QUE LA CAMA DE GERMINACIÓN EXISTA
        if not len(data_siembra['cama_germinacion']):
            return Response({'success': False, 'detail': 'No se puede crear una siembra sin una cama de germinación'}, status=status.HTTP_400_BAD_REQUEST)
        cama = CamasGerminacionVivero.objects.filter(id_cama_germinacion_vivero__in=data_siembra['cama_germinacion'])
        if len(set(data_siembra['cama_germinacion'])) != len(cama):
            return Response({'success': False, 'detail': 'No se encontró ninguna cama de germinación con el parámetro ingresado'}, status=status.HTTP_404_NOT_FOUND)
        
        
        
        

        


        
        


        return Response({'success': True, 'detail': 'Siembra creada exitosamente'}, status=status.HTTP_201_CREATED)


class GetBienSembradoView(generics.ListAPIView):
    serializer_class = GetBienSembradoSerializer
    queryset = CatalogoBienes.objects.all()

    def get(self, request):
        bien = CatalogoBienes.objects.filter(cod_tipo_elemento_vivero='MV', solicitable_vivero=True, es_semilla_vivero=False, nivel_jerarquico='5')
        serializer = self.serializer_class(bien, many=True)
        return Response({'success': True, 'detail': 'Búsqueda exitosa', 'data': serializer.data}, status=status.HTTP_200_OK)