import hashlib
import os
import json
from django.db.models import F
from django.db.models import Max
from pyexpat import model
from rest_framework import generics
from django.core.exceptions import ObjectDoesNotExist
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
from almacen.serializers.activos_serializer import AnexosDocsAlmaSerializer, BajaActivosSerializer, InventarioSerializer, ItemsBajaActivosSerializer, RegistrarBajaAnexosCreateSerializer, RegistrarBajaBienesCreateSerializer, RegistrarBajaCreateSerializer
from almacen.models.inventario_models import Inventario
from almacen.models.activos_models import AnexosDocsAlma, BajaActivos, ItemsBajaActivos
from gestion_documental.models.trd_models import FormatosTiposMedio
from gestion_documental.views.archivos_digitales_views import ArchivosDgitalesCreate, ArchivosDigitales
from copy import copy


class BuscarBien(generics.ListAPIView):
    serializer_class = InventarioSerializer

    def get_queryset(self):
        # Filtrar los registros de inventario según las validaciones requeridas
        queryset = Inventario.objects.filter(
            id_bien__isnull=False,
            id_bodega__isnull=False,
            realizo_baja=False,
            realizo_salida=False,
            
        ).select_related('id_bodega')  # Realizar una sola consulta a la tabla de bodegas

        # Filtrar las bodegas activas
        queryset = queryset.filter(id_bodega__activo=True)

        # Excluir los bienes incluidos en salidas o bajas previas
        queryset = queryset.exclude(realizo_baja=True).exclude(realizo_salida=True)

        # Validar que el campo id_bien tenga un nivel jerárquico de 5
        queryset = queryset.annotate(
            nivel_jerarquico=F('id_bien__nivel_jerarquico')
        ).filter(nivel_jerarquico=5)

        # Validar que el campo cod_tipo_bien sea igual a "A"
        queryset = queryset.filter(id_bien__cod_tipo_bien='A')

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
    
class RegistrarBajaCreateView(generics.CreateAPIView):
    serializer_class = RegistrarBajaCreateSerializer
    serializer_bienes_class = RegistrarBajaBienesCreateSerializer
    serializer_anexos_class = RegistrarBajaAnexosCreateSerializer

    @transaction.atomic
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
        bienes_id_list = [bien['id_bien'] for bien in bienes]
        bienes_instances = CatalogoBienes.objects.filter(id_bien__in=bienes_id_list)

        item_entrada_instances = ItemEntradaAlmacen.objects.filter(id_bien__in=bienes_id_list)

        for bien in bienes:
            bien_instance = bienes_instances.filter(id_bien=bien['id_bien']).first()

            item_entrada_instance = item_entrada_instances.filter(id_bien=bien['id_bien']).first()
            valor_unitario_correcto = item_entrada_instance.valor_unitario if item_entrada_instance else None
            
            bien['id_baja_activo'] = baja_creada.id_baja_activo
            bien['codigo_bien'] = bien_instance.codigo_bien
            bien['nombre'] = bien_instance.nombre
            bien['nombre_marca'] = bien_instance.id_marca.nombre
            bien['doc_identificador_nro'] = bien_instance.doc_identificador_nro
            bien['valor_unitario'] = valor_unitario_correcto

            # Agregar registro al inventario
            inventario = Inventario.objects.filter(id_bien=bien['id_bien']).first()
            if inventario:
                inventario.realizo_baja = True
                inventario.ubicacion_en_bodega = False
                inventario.fecha_ultimo_movimiento = current_date
                inventario.tipo_doc_ultimo_movimiento = 'BAJA'
                inventario.id_registro_doc_ultimo_movimiento = baja_creada.id_baja_activo
                inventario.save()

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

        return Response({'success': True, 'detail': 'Se realizó el registro de la baja correctamente', 'data': serializer_baja.data}, status=status.HTTP_201_CREATED)

class ActualizarBajaActivosView(generics.UpdateAPIView):
    serializer_class = RegistrarBajaCreateSerializer
    serializer_bienes_class = RegistrarBajaBienesCreateSerializer
    serializer_anexos_class = RegistrarBajaAnexosCreateSerializer

    @transaction.atomic
    def update(self, request, pk):
        data = request.data
        anexo = request.FILES.get('anexo')
        # anexos_opcionales = request.FILES.getlist('anexos_opcionales')
        current_date = datetime.now()
        persona_logueada = request.user.persona

        bienes = json.loads(data.get('bienes'))
        # anexos_opcionales_data = json.loads(data.get('anexos_opcionales_data'))

        baja_activo = BajaActivos.objects.filter(id_baja_activo=pk).first()
        if not baja_activo:
            raise NotFound('No se encontró la baja ingresada')

        if not bienes:
            raise ValidationError('Debe seleccionar mínimo un activo al cual desea darle de baja')

        # Actualizar baja en T086
        data_baja = {}
        data_baja['concepto'] = data.get('concepto')
        data_baja['fecha_baja'] = current_date # VALIDAR SI SE PUEDE ACTUALIZAR
        data_baja['cantidad_activos_baja'] = len(bienes)
        data_baja['id_persona_registro_baja'] = persona_logueada.id_persona # VALIDAR SI SE PUEDE ACTUALIZAR
        data_baja['id_uni_org_registro_baja'] = persona_logueada.id_unidad_organizacional_actual.id_unidad_organizacional # VALIDAR SI SE PUEDE ACTUALIZAR
        
        serializer_baja = self.serializer_class(baja_activo, data=data_baja, partial=True)
        serializer_baja.is_valid(raise_exception=True)
        serializer_baja.save()

        # Insertar bienes
        bienes_id_list = [bien['id_bien'] for bien in bienes]
        items_bienes_bajas = ItemsBajaActivos.objects.filter(id_baja_activo=pk)
        items_bienes_bajas_list = list(items_bienes_bajas.values_list('id_bien', flat=True))

        items_bienes_actualizar = items_bienes_bajas.filter(id_bien__in=bienes_id_list)
        items_bienes_crear = [bien for bien in bienes if bien['id_bien'] not in items_bienes_bajas_list]
        items_bienes_crear_list = [bien['id_bien'] for bien in items_bienes_crear]
        items_bienes_eliminar = items_bienes_bajas.exclude(id_bien__in=bienes_id_list)
        items_bienes_crear_instances = CatalogoBienes.objects.filter(id_bien__in=items_bienes_crear_list)

        item_entrada_instances = ItemEntradaAlmacen.objects.filter(id_bien__in=items_bienes_crear_list)

        # ELIMINAR BIENES BAJA
        if items_bienes_eliminar:
            items_bienes_eliminar.delete()

        # CREAR BIENES DE BAJAS NUEVOS
        if items_bienes_crear:
            for bien in items_bienes_crear:
                bien_instance = items_bienes_crear_instances.filter(id_bien=bien['id_bien']).first()

                item_entrada_instance = item_entrada_instances.filter(id_bien=bien['id_bien']).first()
                valor_unitario_correcto = item_entrada_instance.valor_unitario if item_entrada_instance else None
                
                bien['id_baja_activo'] = pk
                bien['codigo_bien'] = bien_instance.codigo_bien
                bien['nombre'] = bien_instance.nombre
                bien['nombre_marca'] = bien_instance.id_marca.nombre
                bien['doc_identificador_nro'] = bien_instance.doc_identificador_nro
                bien['valor_unitario'] = valor_unitario_correcto

                # Agregar registro al inventario
                inventario = Inventario.objects.filter(id_bien=bien['id_bien']).first()
                if inventario:
                    inventario.realizo_baja = True
                    inventario.ubicacion_en_bodega = False
                    inventario.fecha_ultimo_movimiento = current_date # VALIDAR FECHA QUE DEBERIA TOMAR (CREACION O ACTUALIZACION)
                    inventario.tipo_doc_ultimo_movimiento = 'BAJA'
                    inventario.id_registro_doc_ultimo_movimiento = pk
                    inventario.save()

            serializer_bienes = self.serializer_bienes_class(data=items_bienes_crear, many=True)
            serializer_bienes.is_valid(raise_exception=True)
            serializer_bienes.save()

        # ACTUALIZAR JUSTIFICACION BIENES BAJA
        if items_bienes_actualizar:
            for bien_actualizar in items_bienes_actualizar:
                bien_actualizar.justificacion_baja_activo = [bien['justificacion_baja_activo'] for bien in bienes if bien['id_bien'] == bien_actualizar.id_bien.id_bien][0]
                bien_actualizar.save()

        # Insertar archivo digital

        # VALIDAR FORMATO ARCHIVO
        anexo_instance = AnexosDocsAlma.objects.filter(id_anexo_doc_alma=data['id_anexo_doc_alma']).first()
        if anexo:
            nombre_anexo = "Resolución aprobada por el comité"
            old_archivo_digital = copy(anexo_instance.id_archivo_digital)

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

            # Actualizar anexo en T094
            data_anexo = {}
            data_anexo['nro_folios'] = data.get('nro_folios')
            data_anexo['descripcion_anexo'] = data.get('descripcion_anexo')
            data_anexo['fecha_creacion_anexo'] = current_date # SE VA GUADAR FECHA ACTUALZIACION????
            data_anexo['id_archivo_digital'] = respuesta.data.get('data').get('id_archivo_digital')
        
            serializer_anexo = self.serializer_anexos_class(anexo_instance, data=data_anexo, partial=True)
            serializer_anexo.is_valid(raise_exception=True)
            serializer_anexo.save()

            # ELIMINAR ARCHIVO DIGITAL
            old_archivo_digital.delete()

        return Response({'success': True, 'detail': 'Se actualizó el registro de la baja correctamente', 'data': serializer_baja.data}, status=status.HTTP_201_CREATED)

#Retorna_consecutivo_Siguiente
class UltimoConsecutivoView(generics.ListAPIView):
    def list(self, request, *args, **kwargs):
        # Obtener el último consecutivo más 1
        ultimo_consecutivo = BajaActivos.objects.aggregate(max_consecutivo=Max('consecutivo_por_baja'))
        proximo_consecutivo = ultimo_consecutivo['max_consecutivo'] + 1 if ultimo_consecutivo['max_consecutivo'] is not None else 1
        data = {'success': True, 'detail': 'El ultimo consecutivo actual es:', 'data': {'consecutivo_por_baja': proximo_consecutivo}}
        return Response(data)
    

#ELIMINAR_REGISTROS
class BorrarBajaActivosView(generics.DestroyAPIView):
    queryset = BajaActivos.objects.all()

    @transaction.atomic
    def destroy(self, request, pk):
        instance = self.get_object()
        
        # Validar si es posible eliminar el registro de baja de activos
        if not self.puede_eliminar_registro(instance):
            raise ValidationError('No es posible eliminar el registro de baja de activos debido a movimientos posteriores.')

        # Proceder con la eliminación del registro de baja de activos

        # Paso 1: Eliminar los registros correspondientes en la tabla T094ItemsBajaActivos
        items_baja_activos = ItemsBajaActivos.objects.filter(id_baja_activo=instance.id_baja_activo)
        for item in items_baja_activos:
            # Paso 2: Obtener el bien y actualizar el inventario
            inventario = Inventario.objects.get(id_bien=item.id_bien.id_bien)
            inventario.realizo_baja = False
            inventario.fecha_ultimo_movimiento = None
            inventario.tipo_doc_ultimo_movimiento = None
            inventario.id_registro_doc_ultimo_movimiento = None
            inventario.save()

            # Paso 3: Eliminar el item de baja de activos
            item.delete()

        # Paso 4: Eliminar los registros correspondientes en la tabla T087AnexosDocsAlma
        anexos_baja_activos = AnexosDocsAlma.objects.filter(id_baja_activo=instance.id_baja_activo)
        for anexo in anexos_baja_activos:
            # Paso 5: Obtener el archivo digital y eliminarlo
            archivo_digital = anexo.id_archivo_digital
            archivo_digital.delete()
            anexo.delete()

        # Paso 6: Finalmente, eliminar el registro correspondiente en la tabla T086BajaActivos
        instance.delete()

        return Response({'success': True, 'detail': 'Se eliminó el registro de baja de activos correctamente.'}, status=status.HTTP_200_OK)

    def puede_eliminar_registro(self, instance):
        # Recuperar todos los activos incluidos en el registro de baja
        activos_baja = ItemsBajaActivos.objects.filter(id_baja_activo=instance.id_baja_activo)

        # Verificar si los activos tienen movimientos posteriores a la fecha de la baja
        for activo in activos_baja:
            # Obtener el registro de inventario correspondiente al activo
            inventario_activo = Inventario.objects.get(id_bien=activo.id_bien.id_bien)

            # Verificar si el activo tiene un movimiento posterior a la fecha de la baja
            if inventario_activo.fecha_ultimo_movimiento and inventario_activo.fecha_ultimo_movimiento > instance.fecha_baja:
                return False  # Si hay algún movimiento posterior, no se puede eliminar el registro de baja

        return True  # Si no hay movimientos posteriores para ningún activo, se puede eliminar el registro de baja
    


class BajaActivosPorConsecutivo(generics.ListAPIView):
    queryset = BajaActivos.objects.all()
    serializer_class = BajaActivosSerializer

    def list(self, request, *args, **kwargs):
        consecutivo = self.kwargs.get('consecutivo')  # Obtener el consecutivo desde los argumentos de la URL
        baja_activos = self.get_queryset().filter(consecutivo_por_baja=consecutivo).first()  # Filtrar por consecutivo
        if not baja_activos:
            return Response({"success": False, "detail": "No se encontró la baja de activos asociada al consecutivo proporcionado"}, status=404)
        
        # Serializar la baja de activos
        serializer = self.get_serializer(baja_activos)
        data = serializer.data

        # Obtener los anexos relacionados con la baja de activos
        anexos = AnexosDocsAlma.objects.filter(id_baja_activo=baja_activos.id_baja_activo)
        anexos_serializer = AnexosDocsAlmaSerializer(anexos, many=True)
        
        # Agregar los anexos serializados al objeto de la respuesta
        data['anexos'] = anexos_serializer.data

        # Obtener los items de baja de activos asociados a la baja de activos
        items_baja_activos = ItemsBajaActivos.objects.filter(id_baja_activo=baja_activos.id_baja_activo)
        items_serializer = ItemsBajaActivosSerializer(items_baja_activos, many=True)
        
        # Agregar los items serializados al objeto de la respuesta
        data['items'] = items_serializer.data

        return Response({"success": True, "detail": "Baja de activos encontrada", "data": data})
    

class ListarBajasActivosView(generics.ListAPIView):
    queryset = BajaActivos.objects.all()
    serializer_class = BajaActivosSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"success": True, "detail": "Bajas de activos listadas correctamente", "data": serializer.data})
