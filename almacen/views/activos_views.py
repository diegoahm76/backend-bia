import hashlib
import os
import json
from wsgiref.types import FileWrapper
from django.core.files.base import ContentFile
from django.db.models import F
import base64 
from django.db.models import Count
from django.db.models import Max
from pyexpat import model
from rest_framework import generics
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from seguridad.models import Personas
from rest_framework.permissions import IsAuthenticated
from transversal.models.organigrama_models import UnidadesOrganizacionales
from datetime import datetime, date, timedelta, timezone
from rest_framework.response import Response
from django.http import FileResponse, Http404, HttpResponse, JsonResponse
from almacen.models.generics_models import Marcas, UnidadesMedida
from django.db import transaction
from rest_framework import status
from django.db.models import Q, Max
from django.db.models.functions import Lower
from rest_framework.exceptions import ValidationError, PermissionDenied, NotFound
from almacen.models.bienes_models import CatalogoBienes, ItemEntradaAlmacen
from almacen.serializers.activos_serializer import AnexosDocsAlmaSerializer, AnexosOpcionalesDocsAlmaSerializer, BajaActivosSerializer, BusquedaSolicitudActivoSerializer, DetalleSolicitudActivosSerializer, InventarioSerializer, ItemSolicitudActivosSerializer, ItemsBajaActivosSerializer, ItemsSolicitudActivosSerializer, RegistrarBajaAnexosCreateSerializer, RegistrarBajaBienesCreateSerializer, RegistrarBajaCreateSerializer, SolicitudesActivosSerializer, UnidadesMedidaSerializer
from almacen.models.inventario_models import Inventario
from almacen.models.activos_models import AnexosDocsAlma, BajaActivos, DespachoActivos, ItemsBajaActivos, ItemsDespachoActivos, ItemsSolicitudActivos, SolicitudesActivos
from gestion_documental.models.trd_models import FormatosTiposMedio
from gestion_documental.views.archivos_digitales_views import ArchivosDgitalesCreate, ArchivosDigitales
from copy import copy


class BuscarBien(generics.ListAPIView):
    serializer_class = InventarioSerializer
    permission_classes = [IsAuthenticated]


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
    permission_classes = [IsAuthenticated]


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
    permission_classes = [IsAuthenticated] 

    @transaction.atomic
    def update(self, request, pk):
        data = request.data
        anexo = request.FILES.get('anexo')
        current_date = datetime.now()
        persona_logueada = request.user.persona

        bienes = json.loads(data.get('bienes'))

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
            data_anexo['id_archivo_digital'] = respuesta.data.get('data').get('id_archivo_digital')

            # ELIMINAR ARCHIVO DIGITAL
            old_archivo_digital.delete()
            

        # Actualizar anexo en T094
        data_anexo = {}
        data_anexo['nro_folios'] = data.get('nro_folios')
        data_anexo['descripcion_anexo'] = data.get('descripcion_anexo')
        data_anexo['fecha_creacion_anexo'] = current_date # SE VA GUADAR FECHA ACTUALZIACION????
        
        serializer_anexo = self.serializer_anexos_class(anexo_instance, data=data_anexo, partial=True)
        serializer_anexo.is_valid(raise_exception=True)
        serializer_anexo.save()

        

        return Response({'success': True, 'detail': 'Se actualizó el registro de la baja correctamente', 'data': serializer_baja.data}, status=status.HTTP_201_CREATED)

#Retorna_consecutivo_Siguiente
class UltimoConsecutivoView(generics.ListAPIView):
    permission_classes = [IsAuthenticated] 
    def list(self, request, *args, **kwargs):
        # Obtener el último consecutivo más 1
        ultimo_consecutivo = BajaActivos.objects.aggregate(max_consecutivo=Max('consecutivo_por_baja'))
        proximo_consecutivo = ultimo_consecutivo['max_consecutivo'] + 1 if ultimo_consecutivo['max_consecutivo'] is not None else 1
        data = {'success': True, 'detail': 'El ultimo consecutivo actual es:', 'data': {'consecutivo_por_baja': proximo_consecutivo}}
        return Response(data)
    

#ELIMINAR_REGISTROS
class BorrarBajaActivosView(generics.DestroyAPIView):
    queryset = BajaActivos.objects.all()
    permission_classes = [IsAuthenticated] 

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
    permission_classes = [IsAuthenticated] 

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
    permission_classes = [IsAuthenticated] 

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"success": True, "detail": "Bajas de activos listadas correctamente", "data": serializer.data})
    
class ListarUnidadesMedidaActivas(generics.ListAPIView):
    serializer_class = UnidadesMedidaSerializer
    permission_classes = [IsAuthenticated] 

    def get_queryset(self):
        return UnidadesMedida.objects.filter(activo=True)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'success': True, 'detail': 'Unidades de medida activas obtenidas correctamente', 'data': serializer.data})
    

class CrearSolicitudActivosView(generics.CreateAPIView):
    serializer_class = SolicitudesActivosSerializer
    items_serializer_class = ItemsSolicitudActivosSerializer
    permission_classes = [IsAuthenticated] 

    def create(self, request, *args, **kwargs):
        data = request.data
        current_date = datetime.now()
        persona_logueada = request.user.persona

        # Obtener ID de unidad organizacional del solicitante
        id_unidad_org_solicitante = persona_logueada.id_unidad_organizacional_actual.id_unidad_organizacional

        # Obtener ID de la persona operario y su unidad organizacional
        id_persona_operario = data.get('id_persona_operario')
        try:
            persona_operario = Personas.objects.get(id_persona=id_persona_operario)
            id_uni_org_operario = persona_operario.id_unidad_organizacional_actual.id_unidad_organizacional
        except Personas.DoesNotExist:
            return Response({"success": False, 'detail': 'El usuario operario especificado no existe'}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener ID de la persona responsable y su unidad organizacional
        id_funcionario_resp_unidad = data.get('id_funcionario_resp_unidad')
        try:
            persona_responsable = Personas.objects.get(id_persona=id_funcionario_resp_unidad)
            id_uni_org_responsable = persona_responsable.id_unidad_organizacional_actual.id_unidad_organizacional
        except Personas.DoesNotExist:
            return Response({"success": False, 'detail': 'El usuario responsable especificado no existe'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar si la solicitud es de préstamo y ajustar la fecha de devolución
        solicitud_prestamo = data.get('solicitud_prestamo', False)
        if solicitud_prestamo:
            fecha_devolucion = current_date
        else:
            fecha_devolucion = None

        # Guardar información de la solicitud
        solicitud_data = {
            'fecha_solicitud': current_date,
            'motivo': data.get('motivo'),
            'observacion': data.get('observacion'),
            'id_persona_solicita': persona_logueada.id_persona,
            'id_uni_org_solicitante': id_unidad_org_solicitante,
            'id_funcionario_resp_unidad': id_funcionario_resp_unidad,
            'id_uni_org_responsable': id_uni_org_responsable,
            'id_persona_operario': id_persona_operario,
            'id_uni_org_operario': id_uni_org_operario,
            'estado_solicitud': 'S',
            'solicitud_prestamo': solicitud_prestamo,
            'revisada_responble': False,
            'estado_aprobacion_resp': 'Ep',
            'gestionada_alma': False,
            'rechazada_almacen': False,
            'solicitud_anulada_solicitante': False,
            'fecha_devolucion': fecha_devolucion  
        }

        solicitud_serializer = self.serializer_class(data=solicitud_data)
        solicitud_serializer.is_valid(raise_exception=True)
        solicitud = solicitud_serializer.save()

        # Guardar información de los items de la solicitud
        items_data = data.get('items', [])
        for item_data in items_data:
            item_data['id_solicitud_activo'] = solicitud.id_solicitud_activo
            item_serializer = self.items_serializer_class(data=item_data)
            item_serializer.is_valid(raise_exception=True)
            item_serializer.save()

        return Response({'success': True, 'detail': 'Solicitud de activos creada correctamente', 'data': solicitud_serializer.data}, status=status.HTTP_201_CREATED)
    


class EditarSolicitudActivosView(generics.UpdateAPIView):
    serializer_class = SolicitudesActivosSerializer
    queryset = SolicitudesActivos.objects.filter(estado_solicitud__in=["SR","S"])
    items_serializer_class = ItemsSolicitudActivosSerializer
    permission_classes = [IsAuthenticated] 

    def update(self, request, pk):
        instance = self.queryset.filter(id_solicitud_activo=pk).first()
        if not instance:
            raise NotFound ("No se encontro la solicitud activo.")
        data = request.data
        current_date = datetime.now()


        # try:
        with transaction.atomic():
                # Actualizar los campos de la solicitud
                instance.fecha_solicitud = current_date
                instance.motivo = data.get('motivo', instance.motivo)
                instance.observacion = data.get('observacion', instance.observacion)
                instance.solicitud_prestamo = data.get('solicitud_prestamo', instance.solicitud_prestamo)
                instance.save()

                # Actualizar la fecha de devolución si es un préstamo
                if instance.solicitud_prestamo:
                    instance.fecha_devolucion = current_date
                else:
                    instance.fecha_devolucion = None

                # Eliminar los items que no se envían en la solicitud
                items_data = data.get('items', [])
                item_ids_to_keep = [item['id_item_solicitud_activo'] for item in items_data if 'id_item_solicitud_activo' in item]
                instance.itemssolicitudactivos_set.exclude(id_item_solicitud_activo__in=item_ids_to_keep).delete()

                # Guardar o actualizar los items enviados en la solicitud
                for item_data in items_data:
                    item_id = item_data.get('id_item_solicitud_activo')
                    if item_id:
                        # Si el ID del item existe, actualizar el item
                        item_instance = instance.itemssolicitudactivos_set.get(id_item_solicitud_activo=item_id)
                        item_instance.descripcion = item_data.get('descripcion', item_instance.descripcion)
                        item_instance.cantidad = item_data.get('cantidad', item_instance.cantidad)
                        item_instance.save()
                    else:
                        # Si el ID del item no existe, crear un nuevo item asociado a la solicitud
                        item_data['id_solicitud_activo'] = instance.id_solicitud_activo
                        item_serializer = self.items_serializer_class(data=item_data)
                        item_serializer.is_valid(raise_exception=True)
                        item_serializer.save()

        return Response({'success': True, 'detail': 'Solicitud de activos editada correctamente'}, status=status.HTTP_200_OK)

        # except Exception as e:
        #     return Response({'success': False, 'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class DetalleSolicitudActivosView(generics.RetrieveAPIView):
    queryset = SolicitudesActivos.objects.all()
    serializer_class = SolicitudesActivosSerializer
    lookup_field = 'id_solicitud_activo'
    permission_classes = [IsAuthenticated] 

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        # Obtener los items asociados a la solicitud de activos
        items_queryset = ItemsSolicitudActivos.objects.filter(id_solicitud_activo=instance.id_solicitud_activo)
        items_serializer = ItemSolicitudActivosSerializer(items_queryset, many=True)

        # Agregar el nombre de la unidad de medida en los items
        for item_data in items_serializer.data:
            unidad_medida_id = item_data.get('id_unidad_medida')
            unidad_medida_nombre = None
            if unidad_medida_id:
                unidad_medida = UnidadesMedida.objects.filter(id_unidad_medida=unidad_medida_id).first()
                if unidad_medida:
                    unidad_medida_nombre = unidad_medida.nombre
            item_data['nombre_unidad_medida'] = unidad_medida_nombre

        # Agregar los items al resultado de la serialización
        serialized_data = serializer.data
        serialized_data['items'] = items_serializer.data

        return Response({'success': True, 'detail': 'Solicitud de activos recuperada correctamente', 'data': serialized_data}, status=status.HTTP_200_OK)
    
class ResumenSolicitudGeneralActivosView(generics.RetrieveAPIView):
    queryset = SolicitudesActivos.objects.all()
    serializer_class = None  # No necesitamos un serializador para esta vista
    lookup_field = 'id_solicitud_activo'  # Especifica el campo utilizado como PK en la URL
    permission_classes = [IsAuthenticated] 

    def get(self, request, *args, **kwargs):
        instance = self.get_object()
        solicitud_data = {
            'id_solicitud_activo': instance.id_solicitud_activo,
            'fecha_solicitud': instance.fecha_solicitud.strftime('%Y-%m-%d %H:%M:%S'),
            'motivo': instance.motivo,
            'observacion': instance.observacion,
            'id_persona_solicita': instance.id_persona_solicita.id_persona,
            'id_uni_org_solicitante': instance.id_uni_org_solicitante.id_unidad_organizacional,
            'id_funcionario_resp_unidad': instance.id_funcionario_resp_unidad.id_persona,
            'id_uni_org_responsable': instance.id_uni_org_responsable.id_unidad_organizacional,
            'id_persona_operario': instance.id_persona_operario.id_persona,
            'id_uni_org_operario': instance.id_uni_org_operario.id_unidad_organizacional,
            'estado_solicitud': instance.estado_solicitud,
            'solicitud_prestamo': instance.solicitud_prestamo,
            'fecha_devolucion': instance.fecha_devolucion.strftime('%Y-%m-%d %H:%M:%S') if instance.fecha_devolucion else None,
            'fecha_cierra_solicitud': instance.fecha_cierra_solicitud.strftime('%Y-%m-%d %H:%M:%S') if instance.fecha_cierra_solicitud else None,
            'revisada_responble': instance.revisada_responble,
            'estado_aprobacion_resp': instance.estado_aprobacion_resp,
            'justificacion_rechazo_resp': instance.justificacion_rechazo_resp,
            'fecha_aprobacion_resp': instance.fecha_aprobacion_resp.strftime('%Y-%m-%d %H:%M:%S') if instance.fecha_aprobacion_resp else None,
            'gestionada_alma': instance.gestionada_alma,
            'obser_cierre_no_dispo_alma': instance.obser_cierre_no_dispo_alma,
            'fecha_cierre_no_dispo_alma': instance.fecha_cierre_no_dispo_alma.strftime('%Y-%m-%d %H:%M:%S') if instance.fecha_cierre_no_dispo_alma else None,
            'id_persona_cierra_no_dispo_alma': instance.id_persona_cierra_no_dispo_alma.id_persona if instance.id_persona_cierra_no_dispo_alma else None,
            'rechazada_almacen': instance.rechazada_almacen,
            'fecha_rechazo_almacen': instance.fecha_rechazo_almacen.strftime('%Y-%m-%d %H:%M:%S') if instance.fecha_rechazo_almacen else None,
            'justificacion_rechazo_almacen': instance.justificacion_rechazo_almacen,
            'id_persona_alma_rechaza': instance.id_persona_alma_rechaza.id_persona if instance.id_persona_alma_rechaza else None,
            'solicitud_anulada_solicitante': instance.solicitud_anulada_solicitante,
            'fecha_anulacion_solicitante': instance.fecha_anulacion_solicitante.strftime('%Y-%m-%d %H:%M:%S') if instance.fecha_anulacion_solicitante else None,
        }
        
        # Recuperar los items de solicitud activos relacionados
        items_solicitud = ItemsSolicitudActivos.objects.filter(id_solicitud_activo=instance)
        items_data = []
        for item in items_solicitud:
            item_data = {
                'id_item_solicitud_activo': item.id_item_solicitud_activo,
                'id_solicitud_activo': item.id_solicitud_activo.id_solicitud_activo,
                'id_bien': item.id_bien.nombre,  
                'cantidad': item.cantidad,
                'id_unidad_medida': item.id_unidad_medida.id_unidad_medida,  
                'nombre_unidad_medida': item.id_unidad_medida.nombre,
                'observacion': item.observacion,
                'nro_posicion': item.nro_posicion
            }
            items_data.append(item_data)
        
        # Recuperar los items de despacho activos relacionados
        items_despacho = ItemsDespachoActivos.objects.filter(id_despacho_activo__id_solicitud_activo=instance)
        items_despacho_data = []
        for item_despacho in items_despacho:
            item_despacho_data = {
                'id_item_despacho_activo': item_despacho.id_item_despacho_activo,
                'id_despacho_activo': item_despacho.id_despacho_activo.id_despacho_activo,
                'id_bien_despachado': item_despacho.id_bien_despachado.nombre if item_despacho.id_bien_despachado else None,
                'id_bien_solicitado': item_despacho.id_bien_solicitado.nombre if item_despacho.id_bien_solicitado else None,
                'id_entrada_alma': item_despacho.id_entrada_alma if item_despacho.id_entrada_alma else None,
                'id_bodega': item_despacho.id_bodega if item_despacho.id_bodega else None,
                'cantidad_solicitada': item_despacho.cantidad_solicitada,
                'fecha_devolucion': item_despacho.fecha_devolucion.strftime('%Y-%m-%d %H:%M:%S') if item_despacho.fecha_devolucion else None,
                'se_devolvio': item_despacho.se_devolvio,
                'id_uni_medida_solicitada': item_despacho.id_uni_medida_solicitada.nombre if item_despacho.id_uni_medida_solicitada else None,
                'cantidad_despachada': item_despacho.cantidad_despachada,
                'observacion': item_despacho.observacion,
                'nro_posicion_despacho': item_despacho.nro_posicion_despacho
            }
            items_despacho_data.append(item_despacho_data)
        
        # Recuperar los despachos activos relacionados
        despachos = DespachoActivos.objects.filter(id_solicitud_activo=instance)
        despachos_data = []
        for despacho in despachos:
            despacho_data = {
                'id_despacho_activo': despacho.id_despacho_activo,
                'despacho_sin_solicitud': despacho.despacho_sin_solicitud,
                'estado_despacho': despacho.estado_despacho,
                'fecha_autorizacion_resp': despacho.fecha_autorizacion_resp.strftime('%Y-%m-%d %H:%M:%S') if despacho.fecha_autorizacion_resp else None,
                'justificacion_rechazo_resp': despacho.justificacion_rechazo_resp,
                'fecha_solicitud': despacho.fecha_solicitud.strftime('%Y-%m-%d %H:%M:%S') if despacho.fecha_solicitud else None,
                'fecha_despacho': despacho.fecha_despacho.strftime('%Y-%m-%d %H:%M:%S') if despacho.fecha_despacho else None,
                'id_persona_despacha': despacho.id_persona_despacha.id_persona,
                'observacion': despacho.observacion,
                'id_persona_solicita': despacho.id_persona_solicita.id_persona if despacho.id_persona_solicita else None,
                'id_uni_org_solicitante': despacho.id_uni_org_solicitante.id_unidad_organizacional if despacho.id_uni_org_solicitante else None,
                'id_bodega': despacho.id_bodega.id_bodega if despacho.id_bodega else None,
                'despacho_anulado': despacho.despacho_anulado,
                'justificacion_anulacion': despacho.justificacion_anulacion,
                'fecha_anulacion': despacho.fecha_anulacion.strftime('%Y-%m-%d %H:%M:%S') if despacho.fecha_anulacion else None,
                'id_persona_anula': despacho.id_persona_anula.id_persona if despacho.id_persona_anula else None,
                'id_archivo_doc_recibido': despacho.id_archivo_doc_recibido.id_archivo if despacho.id_archivo_doc_recibido else None
            }
            despachos_data.append(despacho_data)
        
        # Agregar los datos de los items de solicitud y despacho activos al resultado final
        solicitud_data['items_solicitud'] = items_data
        solicitud_data['despachos'] = despachos_data
        solicitud_data['items_despacho'] = items_despacho_data

        return Response({'success': True, 'detail': 'Solicitud de activos recuperada correctamente', 'data': solicitud_data}, status=status.HTTP_200_OK)
    

class CancelarSolicitudActivos(generics.UpdateAPIView):
    queryset = SolicitudesActivos.objects.all()
    serializer_class = SolicitudesActivosSerializer
    permission_classes = [IsAuthenticated]   
  
    lookup_field = 'id_solicitud_activo'  # Especifica el campo utilizado como PK en la URL

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        # Verificar si la solicitud puede ser cancelada
        if instance.gestionada_alma:
            return Response({'error': 'No se puede cancelar una solicitud gestionada por el almacén.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener los datos de la solicitud
        justificacion_anulacion = request.data.get('justificacion_anulacion')
        fecha_actual = datetime.now()
        
        # Actualizar los campos de la solicitud
        instance.solicitud_anulada_solicitante = True
        instance.justificacion_anulacion = justificacion_anulacion
        instance.fecha_anulacion_solicitante = fecha_actual
        instance.estado_solicitud = 'C'
        instance.fecha_cierra_solicitud = fecha_actual
        
        # Guardar los cambios en la base de datos
        instance.save()
        
        # Serializar la instancia actualizada
        serializer = self.get_serializer(instance)
        data = serializer.data
        
        return Response({'success': True, 'detail': 'Solicitud cancelada correctamente.', 'data': data}, status=status.HTTP_200_OK)
    

class BusquedaAvanzadaSolicitudesActivos(generics.ListAPIView):
    serializer_class = BusquedaSolicitudActivoSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        # Obtener parámetros de consulta
        estado_solicitud = self.request.query_params.get('estado_solicitud')
        fecha_desde = self.request.query_params.get('fecha_desde')
        fecha_hasta = self.request.query_params.get('fecha_hasta')

        # Filtrar las solicitudes por estado
        queryset = SolicitudesActivos.objects.all()
        if estado_solicitud:
            queryset = queryset.filter(estado_solicitud=estado_solicitud)

        # Filtrar las solicitudes por rango de fechas
        if fecha_desde:
            queryset = queryset.filter(fecha_solicitud__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha_solicitud__lte=fecha_hasta)

        # Anotar el número de activos relacionados a cada solicitud
        queryset = queryset.annotate(numero_activos=Count('itemssolicitudactivos'))

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        data = {
            'success': True,
            'detail': 'Solicitudes obtenidas correctamente.',
            'data': serializer.data
        }
        return Response(data)
    


class CrearArchivosOpcionales(generics.CreateAPIView):
    serializer_class = AnexosOpcionalesDocsAlmaSerializer
    permission_classes = [IsAuthenticated]

    def create(self,request, id_baja_activo):
        data = request.data
        anexo = request.FILES.get('anexo_opcional')
        current_date = datetime.now()
        baja = BajaActivos.objects.filter(id_baja_activo=id_baja_activo).first()

        if not baja:
            raise NotFound("La Baja Activo no ha sido encontrada.")
        
        # Insertar archivo digital

        # VALIDAR FORMATO ARCHIVO 
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
        respuesta = archivo_class.crear_archivo(data_archivo, anexo)

        # Insertar anexo en T094
        data['id_baja_activo'] = baja.id_baja_activo
        data['fecha_creacion_anexo'] = current_date
        data['id_archivo_digital'] = respuesta.data.get('data').get('id_archivo_digital')
        data.pop('anexo_opcional')
        serializer_anexo = self.serializer_class(data=data)
        serializer_anexo.is_valid(raise_exception=True)
        serializer_anexo.save()

        return Response({'success': True, 'detail': 'Archivo opcional creado exitosamente.', 'data': serializer_anexo.data}, status=status.HTTP_200_OK)



class ActualizarAnexoOpcional(generics.UpdateAPIView):
    serializer_class = AnexosOpcionalesDocsAlmaSerializer
    permission_classes = [IsAuthenticated]

    # Insertar archivo digital

    # VALIDAR FORMATO ARCHIVO

    def update(self, request,id_baja_activo):

        data = request.data
        data._mutable=True
        anexo = request.FILES.get('anexo_opcional')
        current_date = datetime.now()

        anexo_instance = AnexosDocsAlma.objects.filter(id_anexo_doc_alma=data['id_anexo_doc_alma'],id_baja_activo = id_baja_activo ).first()
        if not anexo_instance:
            raise NotFound("No se encontro el anexo opcional para la baja de activos requerida.")


        if anexo:
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
            respuesta = archivo_class.crear_archivo(data_archivo, anexo)

            # Actualizar anexo en T094
            data['id_archivo_digital'] = respuesta.data.get('data').get('id_archivo_digital')
            
            # ELIMINAR ARCHIVO DIGITAL
            old_archivo_digital.delete()
            data.pop('anexo_opcional')

        data['fecha_creacion_anexo'] = current_date
        serializer_anexo = self.serializer_class(anexo_instance, data=data, partial=True)
        serializer_anexo.is_valid(raise_exception=True)
        serializer_anexo.save()

        

        return Response({'success': True, 'detail': 'Se actualizó el registro de la baja correctamente', 'data': serializer_anexo.data}, status=status.HTTP_200_OK)


class EliminarAnexoOpcional(generics.DestroyAPIView):
    queryset = AnexosDocsAlma.objects.all()
    serializer_class = AnexosOpcionalesDocsAlmaSerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request, id_baja_activo):
        data = request.data 
        anexo_opcional = AnexosDocsAlma.objects.filter(id_anexo_doc_alma = data["id_anexo_doc_alma"], id_baja_activo= id_baja_activo).first()

        if not anexo_opcional:
            raise NotFound ("No se encontro el Id de la baja de activo que se desea eliminar.")
        
        anexo_opcional.id_archivo_digital.ruta_archivo.delete()

        anexo_opcional.id_archivo_digital.delete()

        anexo_opcional.delete()

        return Response({'success': True, 'detail': 'Anexo opcional eliminado exitosamente.'}, status=status.HTTP_200_OK)
    
class ListarAnexoOpcional(generics.ListAPIView):
    queryset = AnexosDocsAlma.objects.all()
    serializer_class = AnexosDocsAlmaSerializer

    def get_queryset(self):
        id_baja_activo = self.kwargs.get('id_baja_activo')
        return AnexosDocsAlma.objects.filter(id_baja_activo=id_baja_activo)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset, many=True)
        return Response({'success': True, 'detail': 'Anexos opcionales obtenidos exitosamente.', 'data': serializer.data}, status=status.HTTP_200_OK)
    

