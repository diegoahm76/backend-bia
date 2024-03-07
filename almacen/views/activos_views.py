import hashlib
import os
import json
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, date, timedelta, timezone
from rest_framework.response import Response
from django.http import Http404, JsonResponse
from django.db import transaction
from rest_framework import status
from django.db.models import Q, Max
from django.db.models.functions import Lower
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound
from almacen.models.bienes_models import CatalogoBienes, ItemEntradaAlmacen
from almacen.serializers.activos_serializer import InventarioSerializer, RegistrarBajaAnexosCreateSerializer, RegistrarBajaBienesCreateSerializer, RegistrarBajaCreateSerializer
from almacen.models.inventario_models import Inventario
from almacen.models.activos_models import AnexosDocsAlma, BajaActivos, ItemsBajaActivos
from gestion_documental.models.trd_models import FormatosTiposMedio
from gestion_documental.views.archivos_digitales_views import ArchivosDgitalesCreate



class BuscarBien(generics.ListAPIView):
    serializer_class = InventarioSerializer

    def get_queryset(self):
        # Filtrar los registros de inventario según las validaciones requeridas
        queryset = Inventario.objects.filter(
            id_bien__isnull=False,
            id_bodega__isnull=False,
            realizo_baja=False,
            realizo_salida=False
        ).select_related('id_bodega')  # Realizar una sola consulta a la tabla de bodegas

        # Filtrar las bodegas activas
        queryset = queryset.filter(id_bodega__activo=True)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        # Aplicar filtros adicionales según los parámetros de consulta recibidos en la URL
        codigo_bien = self.request.query_params.get('codigo_bien')
        nombre_bien = self.request.query_params.get('nombre_bien')
        nombre_marca = self.request.query_params.get('nombre_marca')
        identificador_bien = self.request.query_params.get('identificador_bien')
        valor_unitario = self.request.query_params.get('valor_unitario')

        if codigo_bien:
            queryset = queryset.filter(id_bien__codigo_bien__icontains=codigo_bien)

        if nombre_bien:
            queryset = queryset.filter(id_bien__nombre__icontains=nombre_bien)

        if nombre_marca:
            queryset = queryset.filter(id_bien__id_marca__nombre__icontains=nombre_marca)

        if identificador_bien:
            queryset = queryset.filter(id_bien__doc_identificador_nro__icontains=identificador_bien)

        if valor_unitario:
            # Filtrar por valor unitario
            items_entrada_ids = ItemEntradaAlmacen.objects.filter(id_bien_id__in=queryset.values_list('id_bien', flat=True), valor_unitario=valor_unitario).values_list('id_bien', flat=True)
            queryset = queryset.filter(id_bien__in=items_entrada_ids)

        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'detail': 'Bienes obtenidos exitosamente', 'data': serializer.data})
    


#Registrar_Baja_Activos
class RegistrarBajaCreateView(generics.CreateAPIView):
    serializer_class = RegistrarBajaCreateSerializer
    serializer_bienes_class = RegistrarBajaBienesCreateSerializer
    serializer_anexos_class = RegistrarBajaAnexosCreateSerializer

    def create(self, request):
        data = request.data
        anexo = request.FILES.get('anexo')
        current_date = datetime.now()
        persona_logueada = request.user.persona

        bienes = json.loads(data.get('bienes'))

        if not bienes:
            raise ValidationError('Debe seleccionar mínimo un activo al cual desea darle de baja')
        
        ultimo_consecutivo = BajaActivos.objects.aggregate(Max('consecutivo_por_baja'))
        ultimo_consecutivo = ultimo_consecutivo['consecutivo_por_baja__max'] if ultimo_consecutivo['consecutivo_por_baja__max'] else 0

        # Insertar baja en T086
        data_baja = {}
        data_baja['consecutivo_por_baja'] = ultimo_consecutivo + 1
        data_baja['concepto'] = data.get('concepto')
        data_baja['fecha_baja'] = current_date
        data_baja['cantidad_activos_baja'] = len(bienes)
        data_baja['id_persona_registro_baja'] = persona_logueada.id_persona
        data_baja['id_uni_org_registro_baja'] = persona_logueada.id_unidad_organizacional_actual.id_unidad_organizacional
        
        serializer_baja = self.serializer_class(data=data_baja)
        serializer_baja.is_valid(raise_exception=True)
        baja_creada = serializer_baja.save()

        # Insertar bienes
        # Obtener las instancias de CatalogoBienes para los campos excepto valor_unitario
        bienes_id_list = [bien['id_bien'] for bien in bienes]
        bienes_instances = CatalogoBienes.objects.filter(id_bien__in=bienes_id_list)

        # Obtener las instancias de ItemEntradaAlmacen para el campo valor_unitario
        item_entrada_instances = ItemEntradaAlmacen.objects.filter(id_bien__in=bienes_id_list)

        for bien in bienes:
            bien_instance = bienes_instances.filter(id_bien=bien['id_bien']).first()

            # Obtener el valor unitario correcto de ItemEntradaAlmacen si existe
            item_entrada_instance = item_entrada_instances.filter(id_bien=bien['id_bien']).first()
            valor_unitario_correcto = item_entrada_instance.valor_unitario if item_entrada_instance else None
            
            # Asignar los valores correspondientes
            bien['id_baja_Activo'] = baja_creada.id_baja_activo
            bien['codigo_bien'] = bien_instance.codigo_bien
            bien['nombre'] = bien_instance.nombre
            bien['nombre_marca'] = bien_instance.id_marca.nombre
            bien['doc_identificador_nro'] = bien_instance.doc_identificador_nro
            bien['valor_unitario'] = valor_unitario_correcto

        # Guardar los datos
        serializer_bienes = self.serializer_bienes_class(data=bienes, many=True)
        serializer_bienes.is_valid(raise_exception=True)
        serializer_bienes.save()

        # Insertar archivo digital

        # VALIDAR FORMATO ARCHIVO 
        nombre_anexo = "Resolución aprobada por el comité"
        archivo_nombre = anexo.name 
        nombre_sin_extension, extension = os.path.splitext(archivo_nombre)
        extension_sin_punto = extension[1:] if extension.startswith('.') else extension
        
        formatos_tipos_medio_list = FormatosTiposMedio.objects.filter(cod_tipo_medio_doc='E').values_list(Lower('nombre'), flat=True)
        
        if extension_sin_punto.lower() not in list(formatos_tipos_medio_list):
            raise ValidationError(f'El formato del documento {archivo_nombre} no se encuentra definido en el sistema')
        
        # CREAR ARCHIVO EN T238
        # Obtiene el año actual para determinar la carpeta de destino
        current_year = current_date.year
        ruta = os.path.join("home", "BIA", "Otros", "GDEA", str(current_year)) # VALIDAR RUTA

        # Calcula el hash MD5 del archivo
        md5_hash = hashlib.md5()
        for chunk in anexo.chunks():
            md5_hash.update(chunk)

        # Obtiene el valor hash MD5
        md5_value = md5_hash.hexdigest()

        # Crea el archivo digital y obtiene su ID
        data_archivo = {
            'es_Doc_elec_archivo': True,
            'ruta': ruta,
            'md5_hash': md5_value  # Agregamos el hash MD5 al diccionario de datos
        }
        
        archivo_class = ArchivosDgitalesCreate()
        anexo.name = nombre_anexo + extension
        respuesta = archivo_class.crear_archivo(data_archivo, anexo)

        # Insertar anexo en T094
        data_anexo = {}
        data_anexo['id_baja_activo'] = baja_creada.id_baja_activo
        data_anexo['nombre_anexo'] = nombre_anexo # PONER NOMBRE FIJO ANEXO
        data_anexo['nro_folios'] = data.get('nro_folios')
        data_anexo['descripcion_anexo'] = data.get('descripcion_anexo')
        data_anexo['fecha_creacion_anexo'] = current_date
        data_anexo['id_archivo_digital'] = respuesta.data.get('data').get('id_archivo_digital')
        
        serializer_anexo = self.serializer_anexos_class(data=data_anexo)
        serializer_anexo.is_valid(raise_exception=True)
        serializer_anexo.save()

        return Response({'success': True, 'message': 'Se realizó el registro de la baja correctamente', 'data': serializer_baja.data}, status=status.HTTP_201_CREATED)