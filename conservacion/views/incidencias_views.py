import copy
from datetime import datetime,timedelta
import json

from conservacion.serializers.incidencias_serializers import ActualizacionIncidenciaSerializer

from seguridad.utils import Util

from conservacion.utils import UtilConservacion
from conservacion.models.incidencias_models import ConsumosIncidenciasMV
from conservacion.serializers.incidencias_serializers import ConsumosIncidenciasMVSerializer
from conservacion.serializers.incidencias_serializers import GetTipoBienSerializer
from almacen.models.bienes_models import CatalogoBienes
from conservacion.models.viveros_models import Vivero
from rest_framework import status, generics
from rest_framework.response import Response
from conservacion.models.inventario_models import InventarioViveros
from rest_framework.permissions import IsAuthenticated
from conservacion.serializers.incidencias_serializers import MaterialVegetalSerializer
from conservacion.models.incidencias_models import IncidenciasMatVegetal
from conservacion.serializers.incidencias_serializers import IncidenciaSerializer
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied

class GetMaterialVegetalByCodigo(generics.ListAPIView):
    serializer_class = MaterialVegetalSerializer
    queryset = InventarioViveros.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,id_vivero):
        
        vivero=Vivero.objects.filter(id_vivero=id_vivero).first()
        if not vivero:
            raise PermissionDenied('No existe vivero')
        
        codigo_bien = request.query_params.get('codigo_bien')
        
        catalogo_bienes_mt=CatalogoBienes.objects.filter(codigo_bien=codigo_bien).first()
        
        if not catalogo_bienes_mt:
            raise ValidationError('El codigo de bien no existe')

        if catalogo_bienes_mt.cod_tipo_elemento_vivero:
            if catalogo_bienes_mt.cod_tipo_elemento_vivero != 'MV' or (catalogo_bienes_mt.cod_tipo_elemento_vivero == 'MV' and catalogo_bienes_mt.es_semilla_vivero):
                raise ValidationError('El código ingresado no es el código de una planta o una plántula')
        else:
            raise ValidationError('El código ingresado no es de consumo o no se encuentra tipificado')
        
        material_vegetal = self.queryset.all().filter(id_vivero=vivero.id_vivero,id_bien__codigo_bien=catalogo_bienes_mt.codigo_bien)
        
        list_siembra_cerrada = [] 
        for material in material_vegetal:
            if material.cod_etapa_lote == 'G' and material.siembra_lote_cerrada == True:
                list_siembra_cerrada.append(material.id_inventario_vivero)
    
        material_vegetal = material_vegetal.exclude(id_inventario_vivero__in=list_siembra_cerrada)
        
        serializador = self.serializer_class(material_vegetal,many = True)
        
        data_serializada = serializador.data
        saldo_total = [data['saldo_total'] for data in data_serializada if data['saldo_total'] != None]
        
        if data_serializada:
            if len(set(saldo_total)) == 1 and list(set(saldo_total))[0] == 0:
                raise PermissionDenied('El código ingresado es de una planta que no tiene saldo disponible en ningún lote-etapa')
        
        data_serializada = [data for data in data_serializada if data['saldo_total'] != 0]
        
        return Response({'success':True,'detail':'se encontraron elementos','data':data_serializada},status=status.HTTP_200_OK)
    
class GetMaterialVegetalByLupa(generics.ListAPIView):
    serializer_class = MaterialVegetalSerializer
    queryset = InventarioViveros.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,id_vivero):
        
        vivero=Vivero.objects.filter(id_vivero=id_vivero).first()
        if not vivero:
            raise PermissionDenied('No existe vivero')
        
        filter={}
        for key,value in request.query_params.items():
            if key in ['codigo_bien','nombre','cod_etapa_lote']:
                if key == 'codigo_bien':
                    filter['id_bien__'+key+'__startswith'] = value
                elif key =='nombre':
                    filter['id_bien__'+key+'__icontains'] = value
                else:
                    filter[key]=value
        
        material_vegetal = self.queryset.all().filter(id_vivero=vivero.id_vivero, id_bien__cod_tipo_elemento_vivero='MV', id_bien__es_semilla_vivero=False).filter(**filter)
        
        list_siembra_cerrada = [] 
        for material in material_vegetal:
            if material.cod_etapa_lote == 'G' and material.siembra_lote_cerrada == True:
                list_siembra_cerrada.append(material.id_inventario_vivero)
    
        material_vegetal = material_vegetal.exclude(id_inventario_vivero__in=list_siembra_cerrada)
        
        serializador = self.serializer_class(material_vegetal,many = True)
        
        data_serializada = serializador.data
    
        data_serializada = [data for data in data_serializada if data['saldo_total'] != 0]
        
        return Response({'success':True,'detail':'se encontraron elementos','data':data_serializada},status=status.HTTP_200_OK)

class GuardarIncidencia(generics.CreateAPIView):
    serializer_class = IncidenciaSerializer
    serializer_class_items = ConsumosIncidenciasMVSerializer
    queryset = IncidenciasMatVegetal.objects.all()
    permission_classes = [IsAuthenticated]
    
    def post(self,request,id_vivero):
        data = request.data
        data_incidencia =  json.loads(data['data_incidencia'])
        items_detalles = json.loads(data['items_detalle'])
        
        file = request.FILES.get('ruta_archivos_soporte')

        data_incidencia['ruta_archivos_soporte'] = file
        
        data_incidencia['id_vivero'] = id_vivero
        
        vivero = Vivero.objects.filter(id_vivero = id_vivero).first()
        
        if not vivero:
            raise ValidationError('El vivero enviado no existe')
        
        inventario_vivero = InventarioViveros.objects.filter(id_bien=data_incidencia['id_bien'],id_vivero=vivero.id_vivero,nro_lote=data_incidencia['nro_lote'],agno_lote=data_incidencia['agno_lote'],cod_etapa_lote=data_incidencia['cod_etapa_lote']).first()

        if not inventario_vivero:
            raise ValidationError('El bien no tiene existencia en el vivero que se está trabajando')
        
        incidencia = self.queryset.all().filter(id_bien=inventario_vivero.id_bien,id_vivero=inventario_vivero.id_vivero,nro_lote=inventario_vivero.nro_lote,agno_lote=inventario_vivero.agno_lote,cod_etapa_lote=inventario_vivero.cod_etapa_lote)
        incidencia_ultimo = incidencia.last()
        incidencia_no_anulada = incidencia.filter(incidencia_anulacion = False).last()

        #FORMATEO DE HORA
        fecha_incidencia = datetime.strptime(data_incidencia['fecha_incidencia'] , '%Y-%m-%d %H:%M:%S')
        
        #CONSECUTIVO
        data_incidencia['consec_por_lote_etapa'] = incidencia_ultimo.consec_por_lote_etapa + 1 if incidencia_ultimo else 1
    
        #VALIDACIONES FECHAS
        fecha_hace_un_dia = datetime.now() - timedelta(days=1)
        
        if fecha_incidencia != datetime.now() and fecha_incidencia < fecha_hace_un_dia:
            raise ValidationError('No se puede realizar el registro de incidencia con más de 24 horas de anterioridad')

        if incidencia_no_anulada:
            if fecha_incidencia <= incidencia_no_anulada.fecha_incidencia:
                raise ValidationError('La fecha de incidencia no puede ser menor o igual a la fecha del ultimo registro de incidencia('+str(incidencia_no_anulada.fecha_incidencia)+')')
                
        #VALIDAR ALTURA
        data_incidencia['altura_lote_en_cms'] = None if data_incidencia['consec_cuaren_lote_etapa'] != None else data_incidencia['altura_lote_en_cms']
        
        #VALIDACION FECHAS DE ALTURA
        if data_incidencia['consec_cuaren_lote_etapa'] == None and data_incidencia['altura_lote_en_cms'] != None:

            if not inventario_vivero.fecha_ult_altura_lote or (inventario_vivero.fecha_ult_altura_lote and fecha_incidencia > inventario_vivero.fecha_ult_altura_lote):

                inventario_vivero.fecha_ult_altura_lote = fecha_incidencia
                inventario_vivero.ult_altura_lote = data_incidencia['altura_lote_en_cms']
                
        elif data_incidencia['consec_cuaren_lote_etapa'] != None and data_incidencia['altura_lote_en_cms'] != None:
            data_incidencia['altura_lote_en_cms'] = None
        
        #ASIGNACION DE ID PERSONA REGISTRA
        data_incidencia['id_persona_registra'] = request.user.persona.id_persona
        
        valores_creados_detalles = []
        registro_viveros_actualizados = []
        # VALIDACIONES ITEMS
        if items_detalles:
            for bien in items_detalles:
                if bien['id_bien']:
                    registro_vivero = InventarioViveros.objects.filter(id_bien=bien['id_bien'],id_vivero=bien['id_vivero']).first()
                    saldo_disponible = UtilConservacion.get_cantidad_disponible_consumir(registro_vivero)
                    nombre = registro_vivero.id_bien.nombre
                    vivero = registro_vivero.id_vivero.nombre
                
                else:
                    registro_vivero = InventarioViveros.objects.filter(id_mezcla=bien['id_mezcla'],id_vivero=bien['id_vivero']).first()
                    saldo_disponible = UtilConservacion.get_cantidad_disponible_mezclas(registro_vivero)
                    nombre = registro_vivero.id_mezcla.nombre
                    vivero = registro_vivero.id_vivero.nombre
                    
                if bien['cantidad_a_consumir'] > saldo_disponible:

                    if bien['saldo_disponible'] != saldo_disponible:
                        raise ValidationError('El saldo disponible del item '+str(nombre)+' en el vivero '+str(vivero)+' se actualizó, por favor verifique que la cantidad a consumir no supere el nuevo saldo ('+str(saldo_disponible)+')')
            
                    raise ValidationError('La cantidad a consumir del item '+str(nombre)+' en el vivero '+str(vivero)+' no puede ser mayor al saldo disponible ('+str(saldo_disponible)+')')
                
                elif bien['cantidad_a_consumir'] <= 0:
                    raise ValidationError('La cantidad a consumir del item '+str(nombre)+' en el vivero '+str(vivero)+' tiene que ser mayor a 0')
            
                #VALIDACION DE REPETIDOS
                
                items_repetidos = [item_data for item_data in items_detalles if
                                    item_data['id_bien']==bien['id_bien'] and
                                    item_data['id_vivero']==bien['id_vivero'] and 
                                    item_data['id_mezcla']==bien['id_mezcla'] 
                                ]
                if len(items_repetidos) > 1:
                    raise ValidationError('El item '+str(nombre)+' en el vivero '+str(vivero)+' ha sido agregado más de una vez en los registros. Si desea actualizar la cantidad consumida u observación de dicho item, borre el registro y agreguelo nuevamente o edite el ya existente')
                
                bien['cantidad_consumida'] = bien['cantidad_a_consumir']
                
                bien['id_vivero'] = id_vivero
                
                #SUMA A CANTIDAD CONSUMOS INTERNOS
                registro_vivero.cantidad_consumos_internos = registro_vivero.cantidad_consumos_internos + int(bien['cantidad_consumida']) if registro_vivero.cantidad_consumos_internos else int(bien['cantidad_consumida'])
                registro_viveros_actualizados.append(registro_vivero)
                valores_creados_detalles.append({'nombre': nombre})
                
                
        # OBTENGO El NOMBRE DE LA ETAPA
        if inventario_vivero.cod_etapa_lote == 'G':
            nombre = 'Germinación'
        elif inventario_vivero.cod_etapa_lote == 'P':
            nombre = 'Producción'
        else:
            nombre = 'Distribución'
        
        #GUARDADO DE INCIDENCIA
        serializador = self.serializer_class(data=data_incidencia,many = False)
        serializador.is_valid(raise_exception=True)
        response_incidencia = serializador.save()
        
        inventario_vivero.save()
        
        #AUDITORIA MAESTRO (INCIDENCIA)
        
        descripcion = {"nombre_vivero": inventario_vivero.id_vivero.nombre,
                    'nombre_bien': inventario_vivero.id_bien.nombre,
                    'numero_lote': str(inventario_vivero.nro_lote),
                    'agno_lote': str(inventario_vivero.agno_lote),
                    'nombre_etapa': nombre,
                    'consecutivo_por_lote_etapa':str(data_incidencia['consec_por_lote_etapa'])}
        direccion=Util.get_client_ip(request)
        
        if items_detalles:
            #ASIGANACION DE PK DEL REGISTRO DE INCIDENCIA
            for item in items_detalles:
                item['id_incidencia_mat_vegetal'] = response_incidencia.pk
                
            #GUARDADO DE ITEMS DE INSUMOS Y MEZCLAS
            serializador = self.serializer_class_items(data=items_detalles,many = True)
            serializador.is_valid(raise_exception=True)
            serializador.save()
            
            InventarioViveros.objects.bulk_update(registro_viveros_actualizados, ['cantidad_consumos_internos'])
            
            #AUDITORIA DEL SERVICIO DE GUARDADO
        
            auditoria_data = {
                "id_usuario" : request.user.id_usuario,
                "id_modulo" : 59,
                "cod_permiso": "CR",
                "subsistema": 'CONS',
                "dirip": direccion,
                "descripcion": descripcion,
                "valores_creados_detalles":valores_creados_detalles
            }
            Util.save_auditoria_maestro_detalle(auditoria_data)
            
        return Response ({'success':True,'detail':'Incidencia creada correctamente'},status=status.HTTP_201_CREATED)
        
class GetElementosInsumoByCodigo(generics.ListAPIView):
    serializer_class = GetTipoBienSerializer
    queryset = InventarioViveros.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,id_vivero):
        
        codigo_bien = request.query_params.get('codigo_bien')
        
        vivero = Vivero.objects.filter(id_vivero = id_vivero).first()
        
        if not vivero:
            raise ValidationError('No existe el vivero seleccionado')
        
        #BUSCO EL BIEN DE TIPO INSUMO
        catalogo_bienes_in = CatalogoBienes.objects.filter(codigo_bien=codigo_bien).first()
        
        if not catalogo_bienes_in:
            raise ValidationError('El codigo de bien no existe')

        if catalogo_bienes_in.cod_tipo_elemento_vivero:
            
            if catalogo_bienes_in.cod_tipo_elemento_vivero != 'IN':
                raise ValidationError('El código ingresado no es de un insumo')
        else:
            raise ValidationError('El código ingresado no es de consumo o no se encuentra tipificado')

        #VALIDACION EN LA TABLA DE INVENTARIO VIVEROS
        
        inventario_vivero = self.queryset.all().filter(id_bien = catalogo_bienes_in.id_bien,id_vivero = id_vivero).first()
        
        if not inventario_vivero:
            raise ValidationError('El item no tiene existencia en el vivero que se está trabajando')
        
        serializador = self.serializer_class(inventario_vivero,many=False)
        
        serializador_data = serializador.data
        
        serializer = serializador_data if serializador_data['saldo_disponible'] > 0 else None
        
        if not serializer:
            raise ValidationError('El bien de tipo insumo no tiene saldo disponible')
        
        return Response({'success':True,'detail':'Se encontró el elemento de insumo','data':serializer},status=status.HTTP_200_OK)
    
class GetElementoYMezclaByLupa(generics.ListAPIView):
    
    serializer_class = GetTipoBienSerializer
    queryset = InventarioViveros.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get (self,request,id_vivero):
        
        filter = {}
        
        tipo_bien = request.query_params.get('tipo_bien')
        
        vivero = Vivero.objects.filter(id_vivero = id_vivero).first()
        
        if not vivero:
            raise ValidationError('No existe el vivero seleccionado')
        
        if not tipo_bien:
            raise ValidationError('Debe seleccionar un tipo')
        
        tipo_bien = 'id_bien' if tipo_bien == 'IN' else 'id_mezcla'
        
        for key,value in request.query_params.items():
            if key in ['codigo_bien', 'nombre']:
                if tipo_bien == 'id_bien' and key == 'nombre':
                    filter['id_bien__' + key+ '__icontains'] = value
                elif tipo_bien == 'id_bien' and key == 'codigo_bien':
                    filter['id_bien__' + key+ '__startswith'] = value
                elif tipo_bien == 'id_mezcla' and key != 'codigo_bien':
                    filter['id_mezcla__'+key+'__icontains'] = value
            
        bienes = self.queryset.all().filter(id_vivero=vivero.id_vivero).filter(**filter)
        
        if tipo_bien == 'id_bien':
            bienes_tipos = bienes.filter(id_bien__cod_tipo_elemento_vivero = 'IN')
        
        else:
            bienes_tipos = bienes.exclude(id_mezcla = None)
        
        serializador = self.serializer_class(bienes_tipos,many = True)
        serializador_data = serializador.data
        
        serializer = [bien_tipo for bien_tipo in serializador_data if bien_tipo['saldo_disponible'] > 0]
        
        return Response({'success':True,'detail':'Se encontraron items','data':serializer},status=status.HTTP_200_OK)

class AnulacionIncidencia(generics.UpdateAPIView):
    serializer_class = IncidenciaSerializer
    queryset = IncidenciasMatVegetal.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self,request,id_incidencias_mat_vegetal):
        
        data = request.data
        
        if not data['justificacion_anulacion']:
            raise ValidationError('Debe de enviar la justifiación')
        
        incidencias = self.queryset.all()
        id_incidencia = incidencias.filter(id_incidencias_mat_vegetal=id_incidencias_mat_vegetal,incidencia_anulacion=False).first()
        
        if not id_incidencia:
            raise NotFound('El registro de incidencia no existe o se encuentra anulado')
        
        ultima_incidencia = incidencias.filter(nro_lote = id_incidencia.nro_lote, cod_etapa_lote =id_incidencia.cod_etapa_lote, id_vivero =id_incidencia.id_vivero,incidencia_anulacion=False).last()
        
        if id_incidencia.id_incidencias_mat_vegetal != ultima_incidencia.id_incidencias_mat_vegetal:
            raise NotFound('El registro no se puede anular debido a que no es la última incidencia que existe con el vivero '+str(id_incidencia.id_vivero)+', Lote '+str(id_incidencia.nro_lote)+', Etapa '+str(id_incidencia.cod_etapa_lote)+'.')
        
        inventario_vivero = InventarioViveros.objects.filter(id_bien = ultima_incidencia.id_bien,id_vivero=ultima_incidencia.id_vivero,agno_lote=ultima_incidencia.agno_lote,nro_lote=ultima_incidencia.nro_lote,cod_etapa_lote=ultima_incidencia.cod_etapa_lote).first()

        valores_eliminados_detalles = []
        
        if ultima_incidencia:
            previous_incidencia = copy.copy(ultima_incidencia)
            fecha_incidencia_48_despues = ultima_incidencia.fecha_incidencia + timedelta(days=2)
            
            if datetime.now() > fecha_incidencia_48_despues:
                raise NotFound('El registro de incidencia no se puede anular ya que supero las 48 horas permitidas para esta acción')

            if ultima_incidencia.fecha_incidencia == inventario_vivero.fecha_ult_altura_lote:
                raise NotFound('la última altura registrada para el lote es de '+str(inventario_vivero.ult_altura_lote)+' cm y fue dada por la incidencia a anular, por lo tanto se recomienda que haga un Registro de Incidencia nuevo para modificar nuevamente dicha altura en caso de que no esté de acuerdo con ella.')
            
            items_consumidos = ConsumosIncidenciasMV.objects.filter(id_incidencia_mat_vegetal=ultima_incidencia.id_incidencias_mat_vegetal)
            
            if items_consumidos:
                for item in items_consumidos:
                    
                    if  item.id_bien:
                        registro_vivero = InventarioViveros.objects.filter(id_bien=item.id_bien,id_vivero=item.id_incidencia_mat_vegetal.id_vivero).first()
                        nombre = registro_vivero.id_bien.nombre
                
                    else:
                        registro_vivero = InventarioViveros.objects.filter(id_mezcla=item.id_mezcla,id_vivero=item.id_incidencia_mat_vegetal.id_vivero).first()
                        nombre = registro_vivero.id_mezcla.nombre

                    valores_eliminados_detalles.append({'nombre':nombre})
                    registro_vivero.cantidad_consumos_internos -= item.cantidad_consumida
                    registro_vivero.save()
        
        #OBTENGO EL NOMBRE DEL COD ETAPA DE LA INCIDENCIA
        
        if ultima_incidencia.cod_etapa_lote == 'G':
            nombre = 'Germinación'
        elif ultima_incidencia.cod_etapa_lote == 'P':
            nombre = 'Producción'
        else:
            nombre = 'Distribución'

        ultima_incidencia.incidencia_anulacion = True
        ultima_incidencia.justificacion_anulacion = data['justificacion_anulacion']
        ultima_incidencia.fecha_anulacion = datetime.now()
        ultima_incidencia.id_persona_anula = request.user.persona
            
        inventario_vivero.save()
        items_consumidos.delete()
        ultima_incidencia.save()

        #AUDITORIA DEL SERVICIO DE ANULACION PARA MAESTRO
        descripcion = {"nombre_vivero": inventario_vivero.id_vivero.nombre,
                        'nombre_bien': inventario_vivero.id_bien.nombre,
                        'numero_lote': str(inventario_vivero.nro_lote),
                        'agno_lote': str(inventario_vivero.agno_lote),
                        'nombre_etapa': nombre ,
                        'consecutivo_por_lote_etapa':str(ultima_incidencia.consec_por_lote_etapa)}
        direccion=Util.get_client_ip(request)
        
        #AUDITORIA DEL SERVICIO DE ACTUALIZADO PARA DETALLES
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 59,
            "cod_permiso": "AN",
            "subsistema": 'CONS',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_eliminados_detalles":valores_eliminados_detalles
        }
        Util.save_auditoria_maestro_detalle(auditoria_data)   
        
        return Response({'success':True,'detail':'Incidencia anulada correctamente'},status=status.HTTP_200_OK)
            
            
class ActualizacionIncidencia(generics.ListAPIView):
    serializer_class_items = ConsumosIncidenciasMVSerializer
    serializer_class = ActualizacionIncidenciaSerializer
    queryset = IncidenciasMatVegetal.objects.all()
    
    def put(self,request,id_incidencias_mat_vegetal):
        
        data = request.data
        data_incidencia =  json.loads(data['data_incidencia'])
        items_detalles = json.loads(data['items_detalle'])
        
        file = request.FILES.get('ruta_archivos_soporte')

        data_incidencia['ruta_archivos_soporte'] = file
        
        incidencia = self.queryset.all().filter(id_incidencias_mat_vegetal=id_incidencias_mat_vegetal,incidencia_anulacion=False).first()
        
        #VALIDACION PARA COMPARAR SI LA PERSONA QUE ESTÁ ACTUALIZANDO ES LA MISMA QUE CREO EL REGISTRO
        
        if incidencia.id_persona_registra.id_persona != request.user.persona.id_persona:
            raise PermissionDenied('No se puede actualizar debido a que la pesona que está intentando hacer esta acción no es la misma que registró esta incidencia')
        
        if incidencia:
            
            inventario_vivero = InventarioViveros.objects.filter(id_bien=incidencia.id_bien,id_vivero=incidencia.id_vivero,agno_lote=incidencia.agno_lote,nro_lote=incidencia.nro_lote,cod_etapa_lote=incidencia.cod_etapa_lote).first()
            items_consumidos = ConsumosIncidenciasMV.objects.filter(id_incidencia_mat_vegetal=incidencia.id_incidencias_mat_vegetal)
            
            previous_incidencias = copy.copy(incidencia)
            
            fecha_en_30_dias= incidencia.fecha_incidencia + timedelta(days=30)
            fecha_hoy = datetime.now()
            cuarenta_ocho = incidencia.fecha_incidencia + timedelta(days=2)
            
            items_validado_cantidad_consumos_internos = []
            items_cantidad_consumida = []
            items_cantidad_consumida_crear = []
        
            if fecha_hoy > fecha_en_30_dias:
                raise PermissionDenied('La incidencia no se puede actualizar debido a que ya superó los 30 días establecido para hacer esta acción')

            if incidencia.fecha_incidencia == inventario_vivero.fecha_ult_altura_lote:
                inventario_vivero.ult_altura_lote = data_incidencia['altura_lote_en_cms']
                
            valores_creados_detalles = []
            previous_instances = []
                
            for item in items_detalles:
                item_consumido = items_consumidos.filter(id_consumo_insidenciaMV=item['id_consumo_insidenciaMV']).first()
                
                #VALIDACION DE REPETIDOS
                
                items_repetidos = [item_data for item_data in items_detalles if
                                    item_data['id_bien']==item['id_bien'] and
                                    item_data['id_vivero']==item['id_vivero'] and 
                                    item_data['id_mezcla']==item['id_mezcla'] 
                                ]
                if len(items_repetidos) > 1:
                    raise ValidationError('El item '+str(nombre)+' en el vivero '+str(vivero)+' ha sido agregado más de una vez en los registros. Si desea actualizar la cantidad consumida u observación de dicho item, borre el registro y agreguelo nuevamente o edite el ya existente')
                
                #ACTUALIZACION ITEMS
                if item_consumido:
                    # previous_items_consumidos.append(copy.copy(item_consumido))
                    
                    if item_consumido.id_bien:
                        registro_vivero = InventarioViveros.objects.filter(id_bien=item['id_bien'],id_vivero=item['id_vivero']).first()
                        saldo_disponible = UtilConservacion.get_cantidad_disponible_consumir(registro_vivero)
                        nombre = item_consumido.id_bien.nombre
                    else:
                        registro_vivero = InventarioViveros.objects.filter(id_mezcla=item['id_mezcla'],id_vivero=item['id_vivero']).first()
                        saldo_disponible = UtilConservacion.get_cantidad_disponible_mezclas(registro_vivero)
                        nombre = item_consumido.id_mezcla.nombre
                    
                    if item_consumido.cantidad_consumida != item['cantidad_a_consumir'] or item_consumido.observaciones != item['observaciones']:
                        previous_instances.append(copy.copy(item_consumido))
                        if item_consumido.cantidad_consumida != item['cantidad_a_consumir']:
                            
                            #VALIDACION DE TIEMPO DE ACTUALIZACION DISPONIBLE PARA ACTUALIZAR LA CANTIDAD CONSUMIDA
                            if fecha_hoy > cuarenta_ocho:
                                raise PermissionDenied('La cantidad consumida del item '+str(nombre)+' no se puede actualizar debido a que ya superó las 48 horas establecidas para hacer esta acción')
                            
                            #AUMENTAR CANTIDAD CONSUMIDA   
                            if int(item['cantidad_a_consumir']) > item_consumido.cantidad_consumida:
                                
                                cantidad_aumentada = int(item['cantidad_a_consumir']) - item_consumido.cantidad_consumida
                                
                                if cantidad_aumentada > saldo_disponible:
                                    raise PermissionDenied('La cantidad aumentada del item '+str(nombre)+' no se puede actualizar debido a que es mayor a la cantidad disponible ('+str(saldo_disponible)+').')
                                
                                registro_vivero.cantidad_consumos_internos += cantidad_aumentada
                                
                                item_consumido.cantidad_consumida += cantidad_aumentada
                                
                            #ACTUALIZACION DISMINUIR CANTIDAD CONSUMIDA    
                            else:
                                if int(item['cantidad_a_consumir']) <= 0:
                                    raise PermissionDenied('La cantidad a consumir tiene que ser mayor a cero')
                                
                                cantidad_disminuida = item_consumido.cantidad_consumida - int(item['cantidad_a_consumir']) 
                                
                                registro_vivero.cantidad_consumos_internos -= cantidad_disminuida
                                
                                item_consumido.cantidad_consumida -= cantidad_disminuida

                        if item_consumido.observaciones != item['observaciones']:
                            item_consumido.observaciones = item['observaciones']
                    
                        items_validado_cantidad_consumos_internos.append(registro_vivero)
                        items_cantidad_consumida.append(item_consumido)
                
                #CREAR ITEMS
                else:
                    if item['id_bien']:
                        registro_vivero_bien = InventarioViveros.objects.filter(id_bien=item['id_bien'],id_vivero=item['id_vivero']).first()
                        saldo_disponible = UtilConservacion.get_cantidad_disponible_consumir(registro_vivero_bien)
                        nombre = registro_vivero_bien.id_bien.nombre
                        vivero = registro_vivero_bien.id_vivero.nombre
                    
                    else:
                        registro_vivero_mezcla = InventarioViveros.objects.filter(id_mezcla=item['id_mezcla'],id_vivero=item['id_vivero']).first()
                        saldo_disponible = UtilConservacion.get_cantidad_disponible_mezclas(registro_vivero_mezcla)
                        nombre = registro_vivero_mezcla.id_mezcla.nombre
                        vivero = registro_vivero_mezcla.id_vivero.nombre
                        
                        #VALIDACION PARA CUANDO AUMENTA LA CANTIDAD A CONSUMIR
                    if item['cantidad_a_consumir'] > saldo_disponible:

                        if item['saldo_disponible'] != saldo_disponible:
                            return Response({'success':False,'detail':'El saldo disponible del item '+str(nombre)+' en el vivero '+str(vivero)+' se actualizó, por favor verifique que la cantidad a consumir no supere el nuevo saldo ('+str(saldo_disponible)+')'},status=status.HTTP_400_BAD_REQUEST)
                
                        raise ValidationError('La cantidad a consumir del item '+str(nombre)+' en el vivero '+str(vivero)+' no puede ser mayor al saldo disponible ('+str(saldo_disponible)+')')
                    
                        #VALIDACION PARA CUANDO DISMINUYE LA CANTIDAD A CONSUMIR
                    elif item['cantidad_a_consumir'] <= 0:
                        raise ValidationError('La cantidad a consumir del item '+str(nombre)+' en el vivero '+str(vivero)+' tiene que ser mayor a 0')
                
                    item['cantidad_consumida'] = item['cantidad_a_consumir']
                    
                    item['id_vivero'] = incidencia.id_vivero
                    
                    #SUMA A CANTIDAD CONSUMOS INTERNOS
                    inventario_vivero.cantidad_consumos_internos = inventario_vivero.cantidad_consumos_internos + int(item['cantidad_consumida']) if inventario_vivero.cantidad_consumos_internos else int(item['cantidad_consumida'])

                    item['id_incidencia_mat_vegetal'] = incidencia.id_incidencias_mat_vegetal
                    
                    items_validado_cantidad_consumos_internos.append(inventario_vivero)
                    items_cantidad_consumida_crear.append(item)
                    valores_creados_detalles.append({'nombre':nombre})
            
            #DETECTAR ITEMS A ELIMINAR
            list_actualizar = [item['id_consumo_insidenciaMV'] for item in items_detalles if item['id_consumo_insidenciaMV'] != None]
            list_eliminar = items_consumidos.exclude(id_consumo_insidenciaMV__in = list_actualizar)
            
            valores_eliminados_detalles = []
            
            #ELIMINACION DE ITEMS
            if list_eliminar:

                for item in list_eliminar:
                    if item.id_bien:
                        registro_vivero = InventarioViveros.objects.filter(id_bien=item.id_bien,id_vivero=incidencia.id_vivero).first()
                        nombre = registro_vivero.id_bien.nombre
                        
                    else:
                        registro_vivero = InventarioViveros.objects.filter(id_mezcla=item.id_mezcla,id_vivero=incidencia.id_vivero).first()
                        nombre = registro_vivero.id_mezcla.nombre
                        
                    registro_vivero.cantidad_consumos_internos = registro_vivero.cantidad_consumos_internos - item.cantidad_consumida
                    registro_vivero.save()
                    valores_eliminados_detalles.append({'nombre':nombre})
                        
                list_eliminar.delete()
                
            #ACTUALIZACION DE ITEMS DE INSUMOS Y MEZCLAS
            serializador = self.serializer_class_items(data=items_cantidad_consumida_crear,many = True)
            serializador.is_valid(raise_exception=True)
            serializador.save()
            
            #ACTUALIZACION  DE MAESTRO
            serializador = self.serializer_class(incidencia,data = data_incidencia)
            serializador.is_valid(raise_exception=True)
            serializador.save()
            
            InventarioViveros.objects.bulk_update(items_validado_cantidad_consumos_internos, ['cantidad_consumos_internos'])
            ConsumosIncidenciasMV.objects.bulk_update(items_cantidad_consumida,['cantidad_consumida','observaciones'])
            
            valores_actualizados_detalles = []
            
            for item_actualizado in items_cantidad_consumida:
                
                if item_actualizado.id_bien:
                    nombre = item_actualizado.id_bien.nombre
                else: 
                    nombre = item_actualizado.id_mezcla.nombre
                    
                previous_item = [item_previous for item_previous in previous_instances if item_previous.id_consumo_insidenciaMV == item_actualizado.id_consumo_insidenciaMV][0]
                descripcion = {'nombre': nombre}
                
        
                valores_actualizados_detalles.append({'previous': previous_item, 'current': item_actualizado, 'descripcion':descripcion})
        
            descripcion = {"nombre_vivero": inventario_vivero.id_vivero.nombre,
                        'nombre_bien': inventario_vivero.id_bien.nombre,
                        'numero_lote': str(inventario_vivero.nro_lote),
                        'agno_lote': str(inventario_vivero.agno_lote),
                        'nombre_etapa': nombre,
                        'consecutivo_por_lote_etapa':str(incidencia.consec_por_lote_etapa)}
            direccion=Util.get_client_ip(request)
            valores_actualizados = {'previous': previous_incidencias,'current': incidencia}
            
            #AUDITORIA DEL SERVICIO DE ACTUALIZADO PARA DETALLES
            auditoria_data = {
                "id_usuario" : request.user.id_usuario,
                "id_modulo" : 59,
                "cod_permiso": "AC",
                "subsistema": 'CONS',
                "dirip": direccion,
                "descripcion": descripcion,
                "valores_actualizados_maestro": valores_actualizados,
                "valores_creados_detalles":valores_creados_detalles,
                "valores_actualizados_detalles":valores_actualizados_detalles,
                "valores_eliminados_detalles":valores_eliminados_detalles
            }
            Util.save_auditoria_maestro_detalle(auditoria_data)    
        
            return Response({'Succes':True,'detail':'Actualizado correctamente'},status=status.HTTP_200_OK)
        else:
            raise ValidationError('No existe incidenia')

class GetIncidenciasByVivero (generics.ListAPIView):
    serializer_class = IncidenciaSerializer
    queryset = IncidenciasMatVegetal.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,id_vivero):
        
        vivero = Vivero.objects.filter(id_vivero = id_vivero).first()
        
        if not vivero:
            raise ValidationError('No existe el vivero seleccionado')
        
        incidencias = self.queryset.all().filter(incidencia_anulacion = False,id_viver=vivero.id_vivero)
        
        if incidencias:
            
            serialializador = self.serializer_class(incidencias,many = True)
            
            return Response ({'success':True,'detail':'Se encontraron incidencias','data':serialializador.data},status=status.HTTP_200_OK)
        
        return Response ({'success':True,'detail':'No se encontraron incidencias para el vivero seleccionado'},status=status.HTTP_200_OK)
    
class GetConsumoIncidenciaByidIncidencia (generics.ListAPIView):
    serializer_class = ConsumosIncidenciasMVSerializer
    queryset = ConsumosIncidenciasMV.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,id_incidencia):
        
        incidencia = IncidenciasMatVegetal.objects.filter(id_incidencias_mat_vegetal=id_incidencia).first()
           
        if incidencia:
            
            consumo_incidencia = self.queryset.all().filter(id_incidencia_mat_vegetal=incidencia.id_incidencias_mat_vegetal)
            
            if consumo_incidencia:
                serializador = self.serializer_class(consumo_incidencia,many= True)

                return Response({'success':True,'detail':'Se encontraron los siguientes consumos para esta incidencia','data':serializador.data},status=status.HTTP_200_OK) 
            
            return Response ({'success':True,'detail':'No se encontraron incidencia para esta incidencia'},status=status.HTTP_200_OK)       
        
        else:
            raise ValidationError('No existe la incidencia')