from almacen.models.bienes_models import CatalogoBienes
from rest_framework import generics, status
from rest_framework.views import APIView
from almacen.serializers.bienes_serializers import (
    CatalogoBienesSerializer,
    EntradaCreateSerializer,
    EntradaUpdateSerializer,
    CreateUpdateItemEntradaConsumoSerializer,
    SerializerItemEntradaActivosFijos,
    SerializerUpdateItemEntradaActivosFijos,
    ItemEntradaSerializer,
    EntradaSerializer
)
from almacen.models.hoja_de_vida_models import (
    HojaDeVidaComputadores,
    HojaDeVidaVehiculos,
    HojaDeVidaOtrosActivos
)
from almacen.models.generics_models import (
    Bodegas,
)
from almacen.models.inventario_models import (
    Inventario,
)
from seguridad.models import (
    Personas
) 
from almacen.models.generics_models import UnidadesMedida , PorcentajesIVA, Marcas
from almacen.models.bienes_models import EntradasAlmacen, ItemEntradaAlmacen
from seguridad.utils import Util  
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
from datetime import timezone

#Creación y actualización de Catalogo de Bienes

class CreateCatalogoDeBienes(generics.UpdateAPIView):
    serializer_class = CatalogoBienesSerializer

    def put(self, request):
        data = request.data

        #Update
        if data['id_bien']!=None:
            catalogo_bien = CatalogoBienes.objects.filter(id_bien= data['id_bien']).first()
            if catalogo_bien:
                try:
                    id_unidad_medida = UnidadesMedida.objects.get(id_unidad_medida=data['id_unidad_medida'])
                    pass
                except:
                    return Response({'success':False, 'detail':'El id de unidad de medida ingresado no existe'}, status=status.HTTP_400_BAD_REQUEST)
                try:
                    id_porcentaje_iva = PorcentajesIVA.objects.get(id_porcentaje_iva=data['id_porcentaje_iva'])
                    pass
                except:
                    return Response({'success':False, 'detail':'El id de porcentaje de iva ingresado no existe'}, status=status.HTTP_400_BAD_REQUEST)
                try:
                    id_unidad_medida_vida_util = UnidadesMedida.objects.get(id_unidad_medida=data['id_unidad_medida_vida_util'])
                    pass
                except:
                    return Response({'success':False, 'detail':'El id de unidad de medida vida util ingresado no existe'}, status=status.HTTP_400_BAD_REQUEST)
                try:
                    id_marca = Marcas.objects.get(id_marca=data['id_marca'])
                    pass
                except:
                    return Response({'success':False, 'detail':'El id de marca ingresado no existe'}, status=status.HTTP_400_BAD_REQUEST)
 
                match data['cod_tipo_bien']:
                    case 'A':                       
                        catalogo_bien.nombre = data['nombre']
                        catalogo_bien.cod_tipo_activo = data['cod_tipo_activo']
                        catalogo_bien.id_porcentaje_iva = id_porcentaje_iva
                        catalogo_bien.cod_tipo_depreciacion = data['cod_tipo_depreciacion']
                        catalogo_bien.id_unidad_medida_vida_util = id_unidad_medida_vida_util
                        catalogo_bien.cantidad_vida_util = data['cantidad_vida_util']
                        catalogo_bien.valor_residual = data['valor_residual']
                        catalogo_bien.id_marca = id_marca
                        catalogo_bien.maneja_hoja_vida = data['maneja_hoja_vida']
                        catalogo_bien.visible_solicitudes = data['visible_solicitudes']
                        catalogo_bien.descripcion = data['descripcion']
                        catalogo_bien.save()
                        serializer = CatalogoBienesSerializer(catalogo_bien, many=False)
                        return Response(serializer.data, status=status.HTTP_200_OK)
                    case 'C':
                        catalogo_bien.nombre = data['nombre']
                        catalogo_bien.cod_metodo_valoracion = data['cod_metodo_valoracion']
                        catalogo_bien.descripcion = data['descripcion']
                        catalogo_bien.id_unidad_medida = id_unidad_medida
                        catalogo_bien.id_porcentaje_iva = id_porcentaje_iva
                        catalogo_bien.stock_minimo = data['stock_minimo']
                        catalogo_bien.stock_maximo = data['stock_maximo']
                        catalogo_bien.solicitable_vivero = data['solicitable_vivero']
                        catalogo_bien.visible_solicitudes = data['visible_solicitudes']

                        catalogo_bien.save()
                        serializer = CatalogoBienesSerializer(catalogo_bien, many=False)
                        return Response(serializer.data, status=status.HTTP_200_OK)
                    case _:
                        return Response({'success':False, 'detail':'No hay ningun bien referente al id_bien enviado'}, status=status.HTTP_400_BAD_REQUEST)    
            else:
                return Response({'success':False, 'detail':'No hay ningun bien referente al id_bien enviado'}, status=status.HTTP_400_BAD_REQUEST)
        #Create
        else:
            #match de los 5 niveles jerarquicos
            match data['nivel_jerarquico']:
                case 1:
                    if int(data['codigo_bien']) >=1 and len(data['codigo_bien'])==1:
                        if CatalogoBienes.objects.filter(codigo_bien=data['codigo_bien']).exists():
                            return Response({'success':False, 'detail':'Ya existe un codigo de bien relacionado en catalogo de bienes'}, status=status.HTTP_400_BAD_REQUEST) 
                        else:
                            nivel_bien_padre = None

                    else:
                        print(len(data['codigo_bien']))
                        return Response({'success':False, 'detail':'Codigo bien fuera de rango'}, status=status.HTTP_400_BAD_REQUEST)                         
                case 2:
                    if (int(data['codigo_bien'][0]))>=1 and len(data['codigo_bien'])==2:
                        if CatalogoBienes.objects.filter(codigo_bien=data['codigo_bien']).exists():
                            return Response({'success':False, 'detail':'Ya existe un codigo de bien relacionado en catalogo de bienes'}, status=status.HTTP_400_BAD_REQUEST) 
                        else:
                            nivel_bien_padre = 1
                    else:
                        print((int(data['codigo_bien'][0]))>=1)
                        print(len(data['codigo_bien'])==2)
                        return Response({'success':False, 'detail':'Codigo bien fuera de rango'}, status=status.HTTP_400_BAD_REQUEST)
                case 3:
                    if int(data['codigo_bien'][0])>=1 and len(data['codigo_bien'])==4:
                        if CatalogoBienes.objects.filter(codigo_bien=data['codigo_bien']).exists():
                            return Response({'success':False, 'detail':'Ya existe un codigo de bien relacionado en catalogo de bienes'}, status=status.HTTP_400_BAD_REQUEST) 
                        else:
                            nivel_bien_padre = 2
                    else:
                        return Response({'success':False, 'detail':'Codigo bien fuera de rango'}, status=status.HTTP_400_BAD_REQUEST)
                case 4:
                    if int(data['codigo_bien'][0])>=1 and len(data['codigo_bien'])==7:
                        if CatalogoBienes.objects.filter(codigo_bien=data['codigo_bien']).exists():
                            return Response({'success':False, 'detail':'Ya existe un codigo de bien relacionado en catalogo de bienes'}, status=status.HTTP_400_BAD_REQUEST) 
                        else:
                            nivel_bien_padre = 3
                    else:
                        return Response({'success':False, 'detail':'Codigo bien fuera de rango'}, status=status.HTTP_400_BAD_REQUEST)
                case 5:
                    if int(data['codigo_bien'][0])>=1 and len(data['codigo_bien'])==12:                  
                        nivel_bien_padre = 4
                    else:
                        return Response({'success':False, 'detail':'Codigo bien fuera de rango'}, status=status.HTTP_400_BAD_REQUEST)
                case _:
                    return Response({'success':False, 'detail':'Nivel jerarquico fuera de rango'}, status=status.HTTP_400_BAD_REQUEST)

            match data['cod_tipo_bien']:
                case 'A':
                    if CatalogoBienes.objects.filter(id_bien=data['id_bien_padre']).exists():
                        padre = CatalogoBienes.objects.get(id_bien=data['id_bien_padre'])
                        nivel_padre = padre.nivel_jerarquico
                        #Crear un catalogo bien para nivel jerarquiro 1 activo fijo
                        if data['nivel_jerarquico']>1 and nivel_padre==nivel_bien_padre:
                                try:
                                    id_unidad_medida = UnidadesMedida.objects.get(id_unidad_medida=data['id_unidad_medida'])
                                    pass
                                except:
                                    return Response({'success':False, 'detail':'El id de unidad de medida ingresado no existe'}, status=status.HTTP_400_BAD_REQUEST)
                                try:
                                    id_porcentaje_iva = PorcentajesIVA.objects.get(id_porcentaje_iva=data['id_porcentaje_iva'])
                                    pass
                                except:
                                    return Response({'success':False, 'detail':'El id de porcentaje de iva ingresado no existe'}, status=status.HTTP_400_BAD_REQUEST)
                                try:
                                    id_unidad_medida_vida_util = UnidadesMedida.objects.get(id_unidad_medida=data['id_unidad_medida_vida_util'])
                                    pass
                                except:
                                    return Response({'success':False, 'detail':'El id de unidad de medida vida util ingresado no existe'}, status=status.HTTP_400_BAD_REQUEST)
                                try:
                                    id_marca = Marcas.objects.get(id_marca=data['id_marca'])
                                    pass
                                except:
                                    return Response({'success':False, 'detail':'El id de marca ingresado no existe'}, status=status.HTTP_400_BAD_REQUEST)
                                catalogo_bien = CatalogoBienes.objects.create(
                                    id_bien=data['id_bien'],
                                    codigo_bien=data['codigo_bien'],
                                    nombre=data['nombre'],
                                    cod_tipo_bien=data['cod_tipo_bien'],
                                    cod_tipo_activo=data['cod_tipo_activo'],
                                    nivel_jerarquico=data['nivel_jerarquico'],
                                    descripcion=data['descripcion'],
                                    id_marca=id_marca,
                                    id_unidad_medida=id_unidad_medida,
                                    id_porcentaje_iva=id_porcentaje_iva,
                                    cod_tipo_depreciacion=data['cod_tipo_depreciacion'],
                                    cantidad_vida_util=data['cantidad_vida_util'],
                                    id_unidad_medida_vida_util=id_unidad_medida_vida_util,
                                    valor_residual=data['valor_residual'],
                                    maneja_hoja_vida=data['maneja_hoja_vida'],
                                    visible_solicitudes=data['visible_solicitudes'],
                                    id_bien_padre=padre  
                                )
                                serializer = self.serializer_class(catalogo_bien)
                        else:
                            return Response({'success':False, 'detail':'el nivel del bien badre no corresponde con el nivel anterior'})
                    elif data['nivel_jerarquico'] == 1:
                            try:
                                id_unidad_medida = UnidadesMedida.objects.get(id_unidad_medida=data['id_unidad_medida'])
                                pass
                            except:
                                return Response({'success':False, 'detail':'El id de unidad de medida ingresado no existe'}, status=status.HTTP_400_BAD_REQUEST)
                            try:
                                id_porcentaje_iva = PorcentajesIVA.objects.get(id_porcentaje_iva=data['id_porcentaje_iva'])
                                pass
                            except:
                                return Response({'success':False, 'detail':'El id de porcentaje de iva ingresado no existe'}, status=status.HTTP_400_BAD_REQUEST)
                            try:
                                id_unidad_medida_vida_util = UnidadesMedida.objects.get(id_unidad_medida=data['id_unidad_medida_vida_util'])
                                pass
                            except:
                                return Response({'success':False, 'detail':'El id de unidad de medida vida util ingresado no existe'}, status=status.HTTP_400_BAD_REQUEST)
                            try:
                                id_marca = Marcas.objects.get(id_marca=data['id_marca'])
                                pass
                            except:
                                return Response({'success':False, 'detail':'El id de marca ingresado no existe'}, status=status.HTTP_400_BAD_REQUEST)
                            catalogo_bien = CatalogoBienes.objects.create(
                                    id_bien=data['id_bien'],
                                    codigo_bien=data['codigo_bien'],
                                    nombre=data['nombre'],
                                    cod_tipo_bien=data['cod_tipo_bien'],
                                    cod_tipo_activo=data['cod_tipo_activo'],
                                    nivel_jerarquico=data['nivel_jerarquico'],
                                    descripcion=data['descripcion'],
                                    id_marca=id_marca,
                                    id_unidad_medida=id_unidad_medida,
                                    id_porcentaje_iva=id_porcentaje_iva,
                                    cod_tipo_depreciacion=data['cod_tipo_depreciacion'],
                                    cantidad_vida_util=data['cantidad_vida_util'],
                                    id_unidad_medida_vida_util=id_unidad_medida_vida_util,
                                    valor_residual=data['valor_residual'],
                                    maneja_hoja_vida=data['maneja_hoja_vida'],
                                    visible_solicitudes=data['visible_solicitudes'],
                                    id_bien_padre=None  
                                )
                            serializer = self.serializer_class(catalogo_bien)
                case 'C':
                    if CatalogoBienes.objects.filter(id_bien=data['id_bien_padre']).exists():
                        padre = CatalogoBienes.objects.get(id_bien=data['id_bien_padre'])
                        nivel_padre = padre.nivel_jerarquico
                        #Crear un catalogo bien para nivel jerarquiro 1 activo fijo
                        if data['nivel_jerarquico']>1 & nivel_padre==nivel_bien_padre:
                            try:
                                id_unidad_medida = UnidadesMedida.objects.get(id_unidad_medida=data['id_unidad_medida'])
                                pass
                            except:
                                return Response({'success':False, 'detail':'El id de unidad de medida ingresado no existe'}, status=status.HTTP_400_BAD_REQUEST)
                            try:
                                id_porcentaje_iva = PorcentajesIVA.objects.get(id_porcentaje_iva=data['id_porcentaje_iva'])
                                pass
                            except:
                                return Response({'success':False, 'detail':'El id de porcentaje de iva ingresado no existe'}, status=status.HTTP_400_BAD_REQUEST)
                            CatalogoBienes.objects.create(
                                    id_bien=data['id_bien'],
                                    codigo_bien=data['codigo_bien'],
                                    nombre=data['nombre'],
                                    cod_tipo_bien=data['cod_tipo_bien'],
                                    nivel_jerarquico=data['nivel_jerarquico'],
                                    nombre_cientifico=data['nombre_cientifico'],
                                    descripcion=data['descripcion'],
                                    id_unidad_medida=id_unidad_medida,
                                    id_porcentaje_iva=id_porcentaje_iva,
                                    metodo_de_valoracion=data['metodo_de_valoracion'],
                                    stock_minimo=data['stock_minimo'],
                                    stock_maximo=data['stock_maximo'],
                                    solicitable_vivero=data['solicitable_vivero'],
                                    id_bien_padre=padre  
                                )
                        elif data['nivel_jerarquico'] == 1:
                            try:
                                id_unidad_medida = UnidadesMedida.objects.get(id_unidad_medida=data['id_unidad_medida'])
                                pass
                            except:
                                return Response({'success':False, 'detail':'El id de unidad de medida ingresado no existe'}, status=status.HTTP_400_BAD_REQUEST)
                            try:
                                id_porcentaje_iva = PorcentajesIVA.objects.get(id_porcentaje_iva=data['id_porcentaje_iva'])
                                pass
                            except:  
                                return Response({'success':False, 'detail':'El id de porcentaje de iva ingresado no existe'}, status=status.HTTP_400_BAD_REQUEST)
                          
                            CatalogoBienes.objects.create(
                                    id_bien=data['id_bien'],
                                    codigo_bien=data['codigo_bien'],
                                    nombre=data['nombre'],
                                    cod_tipo_bien=data['cod_tipo_bien'],
                                    nivel_jerarquico=data['nivel_jerarquico'],
                                    nombre_cientifico=data['nombre_cientifico'],
                                    descripcion=data['descripcion'],
                                    id_unidad_medida=data['id_unidad_medida'],
                                    id_porcentaje_iva=data['id_porcentaje_iva'],
                                    metodo_de_valoracion=data['metodo_de_valoracion'],
                                    stock_minimo=data['stock_minimo'],
                                    stock_maximo=data['stock_maximo'],
                                    solicitable_vivero=data['solicitable_vivero'],
                                    id_bien_padre=None
                                )

                
            return Response(serializer.data)


class GetCatalogoBienesList(generics.ListAPIView):
    serializer_class = CatalogoBienesSerializer
    queryset = CatalogoBienes.objects.all()

    def get(self, request):
        catalogo_bienes_nodos = CatalogoBienes.objects.filter(nro_elemento_bien=None)
        serializador_catalogo = CatalogoBienesSerializer(catalogo_bienes_nodos, many=True)
        return Response({'success':True, 'detail':'Se encontró lo siguiente en almacén', 'data':serializador_catalogo.data}, status=status.HTTP_200_OK)


class DeleteNodos(generics.RetrieveDestroyAPIView):
    serializer_class = CatalogoBienesSerializer
    queryset = CatalogoBienes.objects.all()
    lookup_field = 'id_bien'

    def delete(self, request, id_bien):
        nodo = CatalogoBienes.objects.filter(id_bien=id_bien).first()
        if nodo:
            if nodo.nro_elemento_bien:
                registra_movimiento = Inventario.objects.filter(id_bien=nodo.id_bien)
                if registra_movimiento:
                    return Response({'success': False, 'detail': 'No se puede eliminar un elemento que tenga movimientos en inventario'}, status=status.HTTP_400_BAD_REQUEST)
                nodo.delete()

                #Auditoria Crear Organigrama
                usuario = request.user.id_usuario
                descripcion = {"Codigo bien": str(nodo.codigo_bien), "Numero elemento bien": str(nodo.nro_elemento_bien)}
                direccion=Util.get_client_ip(request)
                auditoria_data = {
                    "id_usuario" : usuario,
                    "id_modulo" : 18,
                    "cod_permiso": "BO",
                    "subsistema": 'ALMA',
                    "dirip": direccion,
                    "descripcion": descripcion, 
                }
                Util.save_auditoria(auditoria_data)
                return Response({'success': True, 'detail': 'Eliminado el elemento'}, status=status.HTTP_204_NO_CONTENT)
            
            hijos = CatalogoBienes.objects.filter(id_bien_padre=nodo.id_bien)
            if hijos:
                return Response({'success': False, 'detail': 'No se puede eliminar un bien si es padre de otros bienes'}, status=status.HTTP_403_FORBIDDEN)  
            nodo.delete()
            
            #Auditoria Crear Organigrama
            usuario = request.user.id_usuario
            descripcion = {"Codigo bien": str(nodo.codigo_bien), "Numero elemento bien": str(nodo.nro_elemento_bien)}
            direccion=Util.get_client_ip(request)
            auditoria_data = {
                "id_usuario" : usuario,
                "id_modulo" : 18,
                "cod_permiso": "BO",
                "subsistema": 'ALMA',
                "dirip": direccion,
                "descripcion": descripcion, 
            }
            Util.save_auditoria(auditoria_data)
            return Response({'success': True,'detail': 'Se ha eliminado el bien correctamente'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'success': False, 'detail': 'No se encontró ningún nodo con el parámetro ingresado'}, status=status.HTTP_404_NOT_FOUND)

class GetElementosByIdNodo(generics.ListAPIView):
    serializer_class = CatalogoBienesSerializer
    queryset = CatalogoBienes.objects.all()

    def get(self, request, id_nodo):
        nodo = CatalogoBienes.objects.filter(id_bien=id_nodo).first()
        if nodo:
            id_nodo = nodo.codigo_bien
            elementos = CatalogoBienes.objects.filter(Q(codigo_bien=id_nodo) & ~Q(nro_elemento_bien=None))
            elementos_serializer = self.serializer_class(elementos, many=True)
            return Response({'success': True, 'detail': 'Busqueda exitosa', 'data': elementos_serializer.data})
        else:
            return Response({'success': False, 'detail': 'No se encontró ningún elemento con el parámetro ingresado'}, status=status.HTTP_404_NOT_FOUND)
class SearchArticuloByDocIdentificador(generics.ListAPIView):
    serializer_class=CatalogoBienesSerializer
    queryset=CatalogoBienes.objects.all()
    
    def get(self,request):
        filter={}
        for key,value in request.query_params.items():
            if key in['cod_tipo_activo','doc_identificador_nro']:
                filter[key]=value
        if not filter.get('doc_identificador_nro'):
            return Response({'success':False,'detail':'Debe enviar el parametro de número de identificación del bien'},status=status.HTTP_404_NOT_FOUND)
        if not filter.get('cod_tipo_activo'):
            return Response({'success':False,'detail':'Debe enviar el parametro del tipo de activo'},status=status.HTTP_404_NOT_FOUND)
        
        bien=CatalogoBienes.objects.filter(**filter).first()
        if bien:
            serializer=self.serializer_class(bien)
            return Response({'success':True,'detail':'Se econtraron elementos','Elementos':serializer.data},status=status.HTTP_200_OK)
        return Response({'success':False,'detail':'No se econtró elementos','data':bien},status=status.HTTP_404_NOT_FOUND)

class SearchArticulosByNombreDocIdentificador(generics.ListAPIView):
    serializer_class=CatalogoBienesSerializer
    queryset=CatalogoBienes.objects.all()
    
    def get(self,request):
        filter={}
        for key,value in request.query_params.items():
            if key in['cod_tipo_activo','nombre','doc_identificador_nro']:
                if key != 'cod_tipo_activo':
                    filter[key+'__icontains']=value
                else:filter[key]=value
        if not filter.get('cod_tipo_activo'):
            return Response({'success':False,'detail':'Debe enviar el parametro del tipo de activo'},status=status.HTTP_404_NOT_FOUND)
        bien=CatalogoBienes.objects.filter(**filter).first()
        if bien:
            serializer=self.serializer_class(bien)
            return Response({'success':True,'detail':'Se econtraron elementos','Elementos':serializer.data},status=status.HTTP_200_OK)
        return Response({'success':False,'detail':'No se econtró elementos','data':bien},status=status.HTTP_404_NOT_FOUND)

class SearchArticulos(generics.ListAPIView):
    serializer_class=CatalogoBienesSerializer
    queryset=CatalogoBienes.objects.all()
    def get(self,request):
        filter={}
        for key,value in request.query_params.items():
            if key in ['nombre','codigo_bien','cod_tipo_activo']:
                if key != 'cod_tipo_activo':
                    filter[key+'__icontains']=value
                else:filter[key]=value
        filter['nro_elemento_bien']=None
        filter['nivel_jerarquico']=5    
        bien=CatalogoBienes.objects.filter(**filter)
        serializador=self.serializer_class(bien,many=True)
        if bien:
            return Response({'success':True,'detail':'se encontró elementos','data':serializador.data},status=status.HTTP_200_OK)
        return Response({'success':True,'detail':'no se econtró elementos','data':bien},status=status.HTTP_404_NOT_FOUND)
    
class GetCatalogoBienesByCodigo(generics.ListAPIView):
    serializer_class = CatalogoBienesSerializer
    queryset = CatalogoBienes.objects.all()

    def get(self, request):
        if not request.query_params.items():
            return Response({'success': False, 'detail': 'Debe ingresar un parámetro de búsqueda', 'data':[]}, status=status.HTTP_404_NOT_FOUND) 
        
        filters = {}
        filters['codigo_bien'] = request.query_params.get('codigo_bien') 
        filters['nivel_jerarquico'] = 5
        filters['nro_elemento_bien'] = None
        
        bien = CatalogoBienes.objects.filter(**filters).first()
        bien_serializer = self.serializer_class(bien)
        
        if bien:
            return Response({'success':True, 'detail':'Busqueda exitosa', 'data':bien_serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success':False, 'detail':'No se encontraron resultados', 'data':[]}, status=status.HTTP_404_NOT_FOUND)


class CreateUpdateEntrada(generics.RetrieveUpdateAPIView):
    serializer_class = EntradaCreateSerializer
    queryset = EntradasAlmacen.objects.all()
    permission_classes = [IsAuthenticated]

    def put(self, request):
        request.data['id_creador'] = request.user.persona.id_persona
        data = request.data
        id_entrada = data.get('id_entrada_almacen')
        
        if id_entrada != None:
            request.data['id_persona_ult_act_dif_creador'] = None
            request.data['fecha_ultima_actualizacion_diferente_creador'] = None
            entrada = EntradasAlmacen.objects.filter(id_entrada_almacen=id_entrada).first()
            if not entrada:
                return Response({'success': False, 'detail': 'No existe ninguna entrada con el id_entrada enviado'}, status=status.HTTP_404_NOT_FOUND)
            
            if request.user.persona.id_persona != entrada.id_creador.id_persona:
                request.data['id_persona_ult_act_dif_creador'] = request.user.persona.id_persona
                request.data['fecha_ultima_actualizacion_diferente_creador'] = datetime.now()

            items_entrada = ItemEntradaAlmacen.objects.filter(id_entrada_almacen=entrada.id_entrada_almacen)
            id_items_entrada = []
            if items_entrada:
                for item in items_entrada:
                    item_inventario = Inventario.objects.filter(id_bien=item.id_bien).first()
                    if str(item_inventario.id_registro_doc_ultimo_movimiento) != str(entrada.id_entrada_almacen):
                        return Response({'success': False, 'detail': 'No se puede actualizar una entrada si el último movimiento de todos los items no fue la entrada'}, status=status.HTTP_403_FORBIDDEN)
                    id_items_entrada.append(item.id_bien.id_bien)

                serializer = EntradaUpdateSerializer(entrada, data=request.data, many=False)
                serializer.is_valid(raise_exception=True)
                tipo_entrada = serializer.validated_data.get('id_tipo_entrada')
                match tipo_entrada.cod_tipo_entrada:
                    case 1:
                        tipo_doc_ultimo_movimiento = 'E_CPR'
                    case 2:
                        tipo_doc_ultimo_movimiento = 'E_DON'
                    case 3:
                        tipo_doc_ultimo_movimiento = 'E_RES'
                    case 4:
                        tipo_doc_ultimo_movimiento = 'E_CPS'
                    case 5:
                        tipo_doc_ultimo_movimiento = 'E_CMD'
                    case 6:
                        tipo_doc_ultimo_movimiento = 'E_CNV'
                    case 7:
                        tipo_doc_ultimo_movimiento = 'E_EMB'
                    case 8:
                        tipo_doc_ultimo_movimiento = 'E_INC'
                    case _:
                        return Response({'success': True, 'detail': 'El tipo de entrada ingresado no es valido'}, status=status.HTTP_400_BAD_REQUEST)
                items_en_inventario = Inventario.objects.filter(id_bien__in=id_items_entrada)
                for item in items_en_inventario:
                    item.cod_tipo_entrada = tipo_entrada
                    item.tipo_doc_ultimo_movimiento = tipo_doc_ultimo_movimiento
                    item.save()
                serializer.save()
            return Response({'success':True, 'detail':'Se ha actualizado la entrada', 'data':serializer.data}, status=status.HTTP_201_CREATED)
        else:
            numero_entrada = data.get('numero_entrada_almacen')
            fecha_entrada = data.get('fecha_entrada')
            if fecha_entrada > str(datetime.now()):
                return Response({'success': False, 'detail': 'No se puede crear una entrada con una fecha superior a la actual'}, status=status.HTTP_400_BAD_REQUEST)
            
            numero_entrada_exist = EntradasAlmacen.objects.filter(numero_entrada_almacen=numero_entrada).first()
            if numero_entrada_exist:
                entradas = EntradasAlmacen.objects.all().order_by('-numero_entrada_almacen').first()
                data['numero_entrada_almacen'] = entradas.numero_entrada_almacen + 1

            serializer = self.serializer_class(data=data, many=False)
            serializer.is_valid(raise_exception=True)
            
            serializer.save()
            return Response({'success':True, 'detail':'Se creó la entrada', 'data':serializer.data}, status=status.HTTP_201_CREATED)


class GetNumeroEntrada(generics.ListAPIView):
    serializer_class = EntradaSerializer
    queryset = EntradasAlmacen.objects.all()

    def get(self, request):
        entrada = EntradasAlmacen.objects.all().order_by('-numero_entrada_almacen').first()
        if not entrada:
            numero_entrada = 1
            return Response({'success': True, 'numero_entrada': numero_entrada})
        numero_entrada = entrada.numero_entrada_almacen + 1

        return Response({'success': True, 'numero_entrada': numero_entrada})


class CreateEntradaandItemsEntrada(generics.CreateAPIView):
    serializer_class = EntradaCreateSerializer
    queryset = EntradasAlmacen.objects.all()

    def post(self, request):
        data = request.data
        entrada_data = data.get('info_entrada')
        items_entrada = data.get('info_items_entrada')
        
        #VALIDACIÓN QUE TODAS LAS ENTRADAS DEBAN TENER UN ITEM
        if not len(items_entrada):
            return Response({'success': False, 'detail': 'No se puede guardar una entrada sin minimo un item de entrada'}, status=status.HTTP_400_BAD_REQUEST)
        entrada_data['id_creador'] = request.user.persona.id_persona
        id_entrada = entrada_data.get('id_entrada_almacen')

        #VALIDACIÓN DE EXISTENCIA DE PROVEEDOR
        id_proveedor = entrada_data.get('id_proveedor')
        proveedor = Personas.objects.filter(id_persona=id_proveedor).first()
        if not proveedor:
            return Response({'success': False, 'detail': 'No se puede crear una entrada con un id_proveedor que no exista'}, status=status.HTTP_400_BAD_REQUEST)

        #VALIDACIÓN DE EXISTENCIA DE TIPO ENTRADA
        id_tipo_entrada = entrada_data.get('id_tipo_entrada')
        tipo_entrada = Personas.objects.filter(id_persona=id_proveedor).first()
        if not tipo_entrada:
            return Response({'success': False, 'detail': 'No se puede crear una entrada con un tipo de entrada que no exista'}, status=status.HTTP_400_BAD_REQUEST)

        #VALIDACIÓN DE FECHAS EN LA ENTRADA
        fecha_entrada = entrada_data.get('fecha_entrada')
        if fecha_entrada > str(datetime.now()):
            return Response({'success': False, 'detail': 'No se puede crear una entrada con una fecha superior a la actual'}, status=status.HTTP_400_BAD_REQUEST)

        #VALIDACIÓN DE EXITENCIA DE BODEGA PARA ENTRADA
        id_bodega_entrada = entrada_data['id_bodega']
        bodega_entrada = Bodegas.objects.filter(id_bodega=id_bodega_entrada).first()
        if not bodega_entrada:
            return Response({'success': False, 'detail': 'La bodega seleccionada para la entrada no existe'}, status=status.HTTP_400_BAD_REQUEST)
        
        #VALIDACIÓN DE EXISTENCIA DE BODEGAS
        id_bodegas_list = [item['id_bodega'] for item in items_entrada]
        if len(id_bodegas_list) != len(items_entrada):
            return Response({'success': False, 'detail': 'Todos los items deben estar asociados a una bodega'}, status=status.HTTP_400_BAD_REQUEST)
        bodega = Bodegas.objects.filter(id_bodega__in=id_bodegas_list)
        if len(set(id_bodegas_list)) != len(bodega):
            return Response({'success': False, 'detail': 'Todas las bodegas enviadas en los items deben existir'}, status=status.HTTP_400_BAD_REQUEST)
        if not bodega:
            return Response({'success': False, 'detail': 'No existe ninguna bodega con los parámetro ingresado'}, status=status.HTTP_404_NOT_FOUND)

        #VALIDACIÓN QUE EL PORCENTAJE DE IVA EXISTA
        id_porcentajes_list = [item['porcentaje_iva'] for item in items_entrada]
        porcentajes_iva = PorcentajesIVA.objects.filter(id_porcentaje_iva__in=id_porcentajes_list)
        if len(set(id_porcentajes_list)) != len(porcentajes_iva):
            return Response({'success': False, 'detail': 'Todas los porcentajes iva enviadas deben existir'}, status=status.HTTP_400_BAD_REQUEST)

        #VALIDACIÓN QUE EL ID_UNIDAD_MEDIDA EXISTA
        unidad_medida_list = [item['id_unidad_medida_vida_util'] for item in items_entrada if item['id_bien_padre'] != None]
        unidades_medida = UnidadesMedida.objects.filter(id_unidad_medida__in=unidad_medida_list)
        if len(set(unidad_medida_list)) != len(unidades_medida):
            return Response({'success': False, 'detail': 'Todas las unidades de medida enviadas deben existir'}, status=status.HTTP_400_BAD_REQUEST)

        #VALIDACIÓN QUE EL NUMERO POSICION NO VENGA REPETIDO
        numero_posicion_list = [item['numero_posicion'] for item in items_entrada]
        if len(set(numero_posicion_list)) != len(numero_posicion_list):
            return Response({'success': False, 'detail': 'Todas los numeros de posicion deben ser unicos'}, status=status.HTTP_400_BAD_REQUEST)
        
        #VALIDACION EN CAMPO TIENE HOJA DE VIDA
        tiene_hoja_vida_list = [item['tiene_hoja_vida'] for item in items_entrada if item['id_bien_padre'] != None and item['tiene_hoja_vida'] !=True and item['tiene_hoja_vida'] != False]
        if tiene_hoja_vida_list:
            return Response({'success': False, 'detail': 'Debe ser enviado un valor válido en el campo tiene hoja de vida'}, status=status.HTTP_400_BAD_REQUEST)

        #VALIDACIÓN DEL NÚMERO DE ENTRADA
        numero_entrada_exist = EntradasAlmacen.objects.all().order_by('-numero_entrada_almacen').first()
        if numero_entrada_exist:
            entrada_data['numero_entrada_almacen'] = numero_entrada_exist.numero_entrada_almacen + 1
        else:
            entrada_data['numero_entrada_almacen'] = 1

        #CREACIÓN DE LA ENTRADA
        serializer = self.serializer_class(data=entrada_data, many=False)
        serializer.is_valid(raise_exception=True)
        entrada_creada = serializer.save()
        entrada_serializada = EntradaSerializer(entrada_creada)

        #ASIGNACIÓN DEL ID DE LA ENTRADA QUE SE ACABÓ DE CREAR
        for item in items_entrada:
            item['id_entrada_almacen'] = entrada_creada.pk

        #FILTRAMOS LOS ACTIVOS FIJOS Y EMPEZAMOS CREACIÓN DE ACTIVOS FIJOS
        items_activos_fijos = list(filter(lambda item:item['id_bien_padre'] != None and item['id_bien'] == None, items_entrada))
        items_activos_consumo = list(filter(lambda item:item['id_bien_padre'] == None and item['id_bien'] != None, items_entrada))
        items_activos_fijos_guardados = []

        for item in items_activos_fijos:
            id_bien_padre = item.get('id_bien_padre')
            doc_identificador_bien = item.get('doc_identificador_bien')
            id_porcentaje_iva = item.get('porcentaje_iva')
            cantidad_vida_util = item.get('cantidad_vida_util')
            id_unidad_medida_vida_util = item.get('id_unidad_medida_vida_util')
            valor_residual = item.get('valor_residual')
            tiene_hoja_vida = item.get('tiene_hoja_vida')
            id_bodega = item.get('id_bodega')
            valor_total_item = item.get('valor_total_item')
            cod_estado = item.get('cod_estado')

            #CREACIÓN DE UN ITEM ACTIVO FIJO EN BASE A CAMPOS HEREDADOS DEL PADRE
            bien_padre = CatalogoBienes.objects.filter(id_bien=id_bien_padre).first()
            bien_padre_serializado = CatalogoBienesSerializer(bien_padre)
                    
            #ASIGNACIÓN DEL ÚLTIMO NÚMERO DEL ELEMENTO
            ultimo_numero_elemento = CatalogoBienes.objects.filter(Q(codigo_bien=bien_padre.codigo_bien) & ~Q(nro_elemento_bien=None)).order_by('-nro_elemento_bien').first()
            numero_elemento = 1
            if ultimo_numero_elemento:
                numero_elemento = ultimo_numero_elemento.nro_elemento_bien + 1

            #ASIGNACIÓN DE INFORMACIÓN PARA LA CREACIÓN DEL ELEMENTO
            data_create = bien_padre_serializado.data
            data_create['nro_elemento_bien'] = numero_elemento
            data_create['doc_identificador_nro'] = doc_identificador_bien
            data_create['id_porcentaje_iva'] = id_porcentaje_iva
            data_create['cantidad_vida_util'] = cantidad_vida_util
            data_create['id_unidad_medida_vida_util'] = id_unidad_medida_vida_util
            data_create['valor_residual'] = valor_residual
            data_create['tiene_hoja_vida'] = tiene_hoja_vida
            data_create['id_bien_padre'] = id_bien_padre
            del data_create['id_bien']
            del data_create['maneja_hoja_vida']
            del data_create['visible_solicitudes']
            serializer = CatalogoBienesSerializer(data=data_create, many=False)
            serializer.is_valid(raise_exception=True)
            elemento_creado = serializer.save()

            #REGISTRAR LA ENTRADA EN INVENTARIO
            bodega = Bodegas.objects.filter(id_bodega=id_bodega).first()
            match entrada_creada.id_tipo_entrada.cod_tipo_entrada:
                case 1:
                    tipo_doc_ultimo_movimiento = 'E_CPR'
                case 2:
                    tipo_doc_ultimo_movimiento = 'E_DON'
                case 3:
                    tipo_doc_ultimo_movimiento = 'E_RES'
                case 4:
                    tipo_doc_ultimo_movimiento = 'E_CPS'
                case 5:
                    tipo_doc_ultimo_movimiento = 'E_CMD'
                case 6:
                    tipo_doc_ultimo_movimiento = 'E_CNV'
                case 7:
                    tipo_doc_ultimo_movimiento = 'E_EMB'
                case 8:
                    tipo_doc_ultimo_movimiento = 'E_INC'
                case _:
                    return Response({'success': True, 'detail': 'El tipo de entrada ingresado no es valido'}, status=status.HTTP_400_BAD_REQUEST)

            registro_inventario = Inventario.objects.create(
                id_bien = elemento_creado,
                id_bodega = bodega,
                cod_tipo_entrada = entrada_creada.id_tipo_entrada,
                fecha_ingreso = datetime.now(),
                id_persona_origen = entrada_creada.id_proveedor,
                numero_doc_origen = entrada_creada.numero_entrada_almacen,
                valor_ingreso = valor_total_item,
                ubicacion_en_bodega = True,
                cod_estado_activo = cod_estado,
                fecha_ultimo_movimiento = datetime.now(),
                tipo_doc_ultimo_movimiento = tipo_doc_ultimo_movimiento,
                id_registro_doc_ultimo_movimiento = entrada_creada.id_entrada_almacen
            )

            if tiene_hoja_vida == True:
                match bien_padre.cod_tipo_activo:
                    case 'Com':
                        create_hoja_vida = HojaDeVidaComputadores.objects.create(
                            id_articulo = elemento_creado
                        )
                    case 'Veh':
                        create_hoja_vida = HojaDeVidaVehiculos.objects.create(
                            id_articulo = elemento_creado
                        )
                    case 'OAc':
                        create_hoja_vida = HojaDeVidaOtrosActivos.objects.create(
                            id_articulo = elemento_creado
                        )
                    case _:
                        return Response({'success': False, 'detail': 'No existe el tipo de activo seleccionado'}, status=status.HTTP_400_BAD_REQUEST) 
            item['id_bien'] = elemento_creado.id_bien
            serializador_item_entrada = SerializerItemEntradaActivosFijos(data=item, many=False)
            serializador_item_entrada.is_valid(raise_exception=True)
            serializador_item_entrada.save()
            items_activos_fijos_guardados.append(serializador_item_entrada.data)
        return Response({'success': True, 'data_entrada_creada': entrada_serializada.data, 'data_items_creados': items_activos_fijos_guardados})


class DeleteItemsEntrada(generics.RetrieveDestroyAPIView):
    serializer_class = ItemEntradaSerializer
    queryset = ItemEntradaAlmacen.objects.all()

    def delete(self, request):
        items_enviados = request.data
        

        #VALIDAR QUE LA ENTRADA NO SE VAYA A QUEDAR SIN ITEMS
        id_entrada = [item['id_entrada_almacen'] for item in items_enviados]
        if len(set(id_entrada)) > 1:
            return Response({'success': False, 'detail': 'Todos los items por eliminar deben pertenecer a la misma entrada'}, status=status.HTTP_403_FORBIDDEN)  

        #VALIDAR QUE TODOS LOS ID_ITEMS_ENVIADOS ENVIADOS PARA ELIMINAR EXISTAN
        ids_items_enviados = [item['id_item_entrada_almacen'] for item in items_enviados]
        items_existentes = ItemEntradaAlmacen.objects.filter(id_item_entrada_almacen__in=ids_items_enviados)
        if len(set(ids_items_enviados)) != len(items_existentes):
            return Response({'success': False, 'detail': 'Todos los id_items enviados deben existir'}, status=status.HTTP_400_BAD_REQUEST) 

        #VALIDAR QUE LA ENTRADA NO SE VAYA A QUEDAR SIN ITEMS
        items_entrada = ItemEntradaAlmacen.objects.filter(id_entrada_almacen=id_entrada[0])
        id_items_entrada_existentes = [item.id_item_entrada_almacen for item in items_entrada]
        if len(ids_items_enviados) == len(id_items_entrada_existentes):
            return Response({'success': False, 'detail': 'No se puede eliminar ya que una entrada no puede quedar sin items'}, status=status.HTTP_403_FORBIDDEN)

        #VALIDACIÓN SI LA ENTRADA FUE EL ÚLTIMO MOVIMIENTO EN INVENTARIO
        id_bienes_enviados = [item['id_bien'] for item in items_enviados]
        inventario_item_instance = Inventario.objects.filter(id_bien__in=id_bienes_enviados)
        for item in inventario_item_instance:
            item_entrada_instance = ItemEntradaAlmacen.objects.filter(id_bien=item.id_bien.id_bien).first()
            if str(item_entrada_instance.id_entrada_almacen.id_entrada_almacen) != str(item.id_registro_doc_ultimo_movimiento):
                return Response({'success': False, 'detail': 'No se puede eliminar este item si la entrada no fue su último movimiento'}, status=status.HTTP_403_FORBIDDEN)

        # VALIDACIÓN SI TIENE HOJA DE VIDA
        objects_items_enviado = [item for item in items_enviados]
        for item in objects_items_enviado:
            item_instance = ItemEntradaAlmacen.objects.filter(id_item_entrada_almacen=item['id_item_entrada_almacen']).first()
            
            if item_instance.id_bien.cod_tipo_bien == 'A':
                item_hv_comp = HojaDeVidaComputadores.objects.filter(id_articulo=item_instance.id_bien.id_bien).first()
                item_hv_veh = HojaDeVidaVehiculos.objects.filter(id_articulo=item_instance.id_bien.id_bien).first()
                item_hv_oac = HojaDeVidaOtrosActivos.objects.filter(id_articulo=item_instance.id_bien.id_bien).first()
                if item_hv_comp or item_hv_veh or item_hv_oac:
                    return Response({'success': False, 'detail': 'No se puede eliminar por que tiene hoja de vida'}, status=status.HTTP_403_FORBIDDEN)
                item_instance_serializer = SerializerItemEntradaActivosFijos(item_instance, data=item)

                bien_eliminar = CatalogoBienes.objects.filter(id_bien=item_instance.id_bien.id_bien).first()
                inventario_item_instance_delete = Inventario.objects.filter(id_bien=item_instance.id_bien.id_bien)

                #ELIMINA EL REGISTRO EN INVENTARIO, CATALOGO DE BIENES E ITEM ENTRADA
                inventario_item_instance_delete.delete()
                bien_eliminar.delete()
                item_instance.delete()
        
        return Response({'success': True, 'detail': 'Se ha eliminado correctamente'}, status=status.HTTP_204_NO_CONTENT)


class UpdateEntrada(generics.RetrieveUpdateAPIView):
    serializer_class = EntradaUpdateSerializer
    queryset = EntradasAlmacen.objects.all()

    def put(self, request, id_entrada):
        data = request.data
        entrada = EntradasAlmacen.objects.filter(id_entrada_almacen=id_entrada).first()
        if not entrada:
            return Response({'success': False, 'detail': 'No se encontró ninguna entrada con el parámetro ingresado'}, status=status.HTTP_404_NOT_FOUND)
        cod_tipo_entrada = data['id_tipo_entrada']
        if cod_tipo_entrada != entrada.id_tipo_entrada:
            items_entrada = ItemEntradaAlmacen.objects.filter(id_entrada_almacen=entrada.id_entrada_almacen)
            id_bien_items_list = [item.id_bien for item in items_entrada]
            for id_bien in id_bien_items_list:
                bien_inventario = Inventario.objects.filter(id_bien=id_bien).first()
                if str(bien_inventario.id_registro_doc_ultimo_movimiento) != str(entrada.id_entrada_almacen):
                    return Response({'success': False, 'detail': 'No se puede actualizar ya que los items asociados a esta entrada no tienen como último movimiento la entrada'}, status=status.HTTP_403_FORBIDDEN)



# # class CreateUpdateDeleteItemsEntrada(generics.RetrieveUpdateDestroyAPIView):
#     serializer_class = EntradaCreateSerializer
#     queryset = ItemEntradaAlmacen.objects.all()

#     def put(self, request):
#         data = request.data
#         entrada_data = data.get('info_entrada')
#         items_entrada = data.get('info_items_entrada')

#         # #VALIDACIÓN QUE TODAS LAS ENTRADAS DEBAN TENER UN ITEM
#         # if not len(items_entrada):
#         #     return Response({'success': False, 'detail': 'No se puede guardar una entrada sin minimo un item de entrada'}, status=status.HTTP_400_BAD_REQUEST)
#         entrada_data['id_creador'] = request.user.persona.id_persona
#         id_entrada = entrada_data.get('id_entrada_almacen')

#         # #VALIDACIÓN DE EXISTENCIA DE PROVEEDOR
#         # id_proveedor = entrada_data.get('id_proveedor')
#         # proveedor = Personas.objects.filter(id_persona=id_proveedor).first()
#         # if not proveedor:
#         #     return Response({'success': False, 'detail': 'No se puede crear una entrada con un id_proveedor que no exista'}, status=status.HTTP_400_BAD_REQUEST)

#         # #VALIDACIÓN DE EXISTENCIA DE TIPO ENTRADA
#         # id_tipo_entrada = entrada_data.get('id_tipo_entrada')
#         # tipo_entrada = Personas.objects.filter(id_persona=id_proveedor).first()
#         # if not tipo_entrada:
#         #     return Response({'success': False, 'detail': 'No se puede crear una entrada con un tipo de entrada que no exista'}, status=status.HTTP_400_BAD_REQUEST)

#         # #VALIDACIÓN DE FECHAS EN LA ENTRADA
#         # fecha_entrada = entrada_data.get('fecha_entrada')
#         # if fecha_entrada > str(datetime.now()):
#         #     return Response({'success': False, 'detail': 'No se puede crear una entrada con una fecha superior a la actual'}, status=status.HTTP_400_BAD_REQUEST)

#         # #VALIDACIÓN DE EXISTENCIA DE BODEGAS
#         # id_bodegas_list = [item['id_bodega'] for item in items_entrada]
#         # if len(id_bodegas_list) != len(items_entrada):
#         #     return Response({'success': False, 'detail': 'Todos los items deben estar asociados a una bodega'}, status=status.HTTP_400_BAD_REQUEST)
#         # bodega = Bodegas.objects.filter(id_bodega__in=id_bodegas_list)
#         # if len(set(id_bodegas_list)) != len(bodega):
#         #     return Response({'success': False, 'detail': 'Todas las bodegas enviadas deben existir'}, status=status.HTTP_400_BAD_REQUEST)
#         # if not bodega:
#         #     return Response({'success': False, 'detail': 'No existe ninguna bodega con el parámetro ingresado'}, status=status.HTTP_404_NOT_FOUND)

#         # #VALIDACIÓN QUE EL ID ENTRADA ENVIADO Y ID ITEMS ENVIADOS SI SE RELACIONEN
#         # id_entrada_enviado = entrada_data['id_entrada_almacen'] if entrada_data['id_entrada_almacen'] != None else '0'
#         # if id_entrada_enviado != '0':
#         #     entrada_instance = EntradasAlmacen.objects.filter(id_entrada_almacen=id_entrada_enviado).first()
#         #     if not entrada_instance:
#         #         return Response({'success': False, 'detail': 'No existe ninguna entrada con el id_entrada ingresado'}, status=status.HTTP_404_NOT_FOUND)
#         #     #VALIDACIÓN QUE SI MANDAN EL ID ENTRADA DEBEN ENVIAR UN ID ITEM
#         #     items_enviados = [item['id_item_entrada_almacen'] for item in items_entrada if item['id_item_entrada_almacen'] != None]
#         #     if not items_enviados:
#         #         return Response({'success': False, 'detail': 'No se puede enviar el id de la entrada sin el id de al menos un item, ya que debería estar actualizando'}, status=status.HTTP_400_BAD_REQUEST)
        
        
#         #VALIDACIÓN QUE LOS ITEMS DE ENTRADA ENVIADOS DEBEN EXISTIR
#         id_items_enviados = [item['id_item_entrada_almacen'] for item in items_entrada if item['id_item_entrada_almacen'] != None]
#         items_enviados_instance = ItemEntradaAlmacen.objects.filter(id_item_entrada_almacen__in=id_items_enviados)
#         if len(id_items_enviados) != len(items_enviados_instance):
#             return Response({'success': False, 'detail': 'Todos los items entradas deben existir'}, status=status.HTTP_400_BAD_REQUEST)

#         #TODOS LOS IDS DE ENTRADA ENVIADOS EN LOS ITEMS DEBEN SER IGUALES
#         id_entrada_items_enviados_list = [item.id_entrada_almacen.id_entrada_almacen for item in items_enviados_instance]
#         if len(set(id_entrada_items_enviados_list)) > 1:
#             return Response({'success': False, 'detail': 'Todos los id_entradas deben ser iguales'}, status=status.HTTP_400_BAD_REQUEST)
        
#         #TODOS LOS IDS DE ENTRADA ENVIADOS EN CADA ITEM DEBEN SER IGUALES AL ID ENTRADA ENVIADO EN LA ENTRADA
#         if id_entrada_items_enviados_list: 
#             if id_entrada_items_enviados_list[0] != entrada_data['id_entrada_almacen']: 
#                 return Response({'success': False, 'detail': 'Todos los id_entradas_items deben ser iguales al id entrada enviado en entrada'}, status=status.HTTP_400_BAD_REQUEST)
             

#         #VALIDACIÓN QUE LOS ID_ITEM_ENTRADA ENVIADOS EXISTAN EN CONJUNTO
#         item_entrada_list = [item['id_item_entrada_almacen'] for item in items_entrada if item['id_item_entrada_almacen'] != None]
#         item_entrada = ItemEntradaAlmacen.objects.filter(id_item_entrada_almacen__in=item_entrada_list)
#         if len(set(item_entrada_list)) != len(item_entrada):
#             return Response({'success': False, 'detail': 'Todos los items por actualizar deben existir'}, status=status.HTTP_400_BAD_REQUEST)

#         #VALIDACIÓN QUE EL ID PADRE EXISTA PARA LOS QUE SON ACTIVOS FIJOS
#         id_padres_list = [item['id_bien_padre'] for item in items_entrada if item['id_bien_padre'] != None]
#         padres = CatalogoBienes.objects.filter(id_bien__in=id_padres_list)
#         if len(set(id_padres_list)) != len(padres):
#             return Response({'success': False, 'detail': 'Todas los id_padres enviadas deben existir'}, status=status.HTTP_400_BAD_REQUEST)
        
#         # #VALIDACIÓN QUE EL PORCENTAJE DE IVA EXISTA
#         # id_porcentajes_list = [item['porcentaje_iva'] for item in items_entrada]
#         # porcentajes_iva = PorcentajesIVA.objects.filter(id_porcentaje_iva__in=id_porcentajes_list)
#         # if len(set(id_porcentajes_list)) != len(porcentajes_iva):
#         #     return Response({'success': False, 'detail': 'Todas los porcentajes iva enviadas deben existir'}, status=status.HTTP_400_BAD_REQUEST)

#         # #VALIDACIÓN QUE EL DOC IDENTIFICADOR DEL BIEN SEA ÚNICO
#         # doc_identificador_list = [item['doc_identificador_bien'] for item in items_entrada if item['id_bien_padre'] != None]
#         # if len(doc_identificador_list) != len(set(doc_identificador_list)):
#         #     return Response({'success': False, 'detail': 'Todos los documentos identificadores deben ser únicos'})

#         # #VALIDACIÓN QUE EL ID_UNIDAD_MEDIDA EXISTA
#         # unidad_medida_list = [item['id_unidad_medida_vida_util'] for item in items_entrada if item['id_bien_padre'] != None]
#         # unidades_medida = UnidadesMedida.objects.filter(id_unidad_medida__in=unidad_medida_list)
#         # if len(set(unidad_medida_list)) != len(unidades_medida):
#         #     return Response({'success': False, 'detail': 'Todas las unidades de medida enviadas deben existir'}, status=status.HTTP_400_BAD_REQUEST)
        
#         # #VALIDACIÓN QUE EL NUMERO POSICION NO VENGA REPETIDO
#         # numero_posicion_list = [item['numero_posicion'] for item in items_entrada]
#         # if len(set(numero_posicion_list)) != len(numero_posicion_list):
#         #     return Response({'success': False, 'detail': 'Todas los numeros de posicion deben ser unicos'}, status=status.HTTP_400_BAD_REQUEST)
        
#         # #VALIDACION EN CAMPO TIENE HOJA DE VIDA
#         # tiene_hoja_vida_list = [item['tiene_hoja_vida'] for item in items_entrada if item['id_bien_padre'] != None and item['tiene_hoja_vida'] !=True and item['tiene_hoja_vida'] != False]
#         # if tiene_hoja_vida_list:
#         #     return Response({'success': False, 'detail': 'Debe ser enviado un valor válido en el campo tiene hoja de vida'}, status=status.HTTP_400_BAD_REQUEST)

#         if id_entrada != None:
#             items_guardados = []
#             entrada_data['id_persona_ult_act_dif_creador'] = None
#             entrada_data['fecha_ultima_actualizacion_diferente_creador'] = None

#             entrada = EntradasAlmacen.objects.filter(id_entrada_almacen=id_entrada).first()
#             if request.user.persona.id_persona != entrada.id_creador.id_persona:
#                 entrada_data['id_persona_ult_act_dif_creador'] = request.user.persona.id_persona
#                 entrada_data['fecha_ultima_actualizacion_diferente_creador'] = datetime.now()

#             #VALIDAR QUE TODOS LOS ID BIENES ENVIADOS EN LOS ITEMS PARA ACTUALIZAR EXISTAN
#             ids_items_enviados = [item['id_bien'] for item in items_entrada if item['id_bien'] != None]
#             items_inventario = Inventario.objects.filter(id_bien__in=ids_items_enviados)
#             if len(set(ids_items_enviados)) != len(items_inventario):
#                 return Response({'success': False, 'detail': 'Todos los id_bien enviados en los items deben existir'}, status=status.HTTP_400_BAD_REQUEST) 

#             #VALIDAR QUE TODOS LOS ELEMENTOS ENVIADOS TENGAN COMO ÚLTIMO MOVIMIENTO LA ENTRADA
#             elementos_pasaron = []
#             elementos_no_pasaron = []
#             items_entrantes_actualizar = [item for item in items_entrada if item['id_item_entrada_almacen'] != None]
            
#             for item in items_entrantes_actualizar:
#                 item_inventario = Inventario.objects.filter(id_bien=item['id_bien']).first()
#                 if str(item_inventario.id_registro_doc_ultimo_movimiento) != str(entrada.id_entrada_almacen):
#                     elementos_no_pasaron.append(item)
#                 else:
#                     elementos_pasaron.append(item)
                
#             print('elementos pasaron:', elementos_pasaron, 'elementos no pasaron:', elementos_no_pasaron)
#             # return Response({'success': False, 'elementos pasaron': elementos_pasaron, 'elementos no pasaron': elementos_no_pasaron})

#             serializer = EntradaUpdateSerializer(entrada, data=entrada_data, many=False)
#             serializer.is_valid(raise_exception=True)
#             tipo_entrada = serializer.validated_data.get('id_tipo_entrada')
            
#             if tipo_entrada != entrada.id_tipo_entrada.cod_tipo_entrada:
#                 match tipo_entrada.cod_tipo_entrada:
#                     case 1:
#                         tipo_doc_ultimo_movimiento = 'E_CPR'
#                     case 2:
#                         tipo_doc_ultimo_movimiento = 'E_DON'
#                     case 3:
#                         tipo_doc_ultimo_movimiento = 'E_RES'
#                     case 4:
#                         tipo_doc_ultimo_movimiento = 'E_CPS'
#                     case 5:
#                         tipo_doc_ultimo_movimiento = 'E_CMD'
#                     case 6:
#                         tipo_doc_ultimo_movimiento = 'E_CNV'
#                     case 7:
#                         tipo_doc_ultimo_movimiento = 'E_EMB'
#                     case 8:
#                         tipo_doc_ultimo_movimiento = 'E_INC'
#                     case _:
#                         return Response({'success': True, 'detail': 'El tipo de entrada ingresado no es valido'}, status=status.HTTP_400_BAD_REQUEST)
#                 id_items_pasaron = [item['id_bien'] for item in elementos_pasaron]
#                 items_en_inventario = Inventario.objects.filter(id_bien__in=id_items_pasaron)
#                 for item_inventario in items_en_inventario:
#                     item_inventario.cod_tipo_entrada = tipo_entrada
#                     item_inventario.tipo_doc_ultimo_movimiento = tipo_doc_ultimo_movimiento
#                     item_inventario.save()
#             serializado = serializer.save()

#             #HASTA ACÁ FUNCIONA
            

#             item_entrada = ItemEntradaAlmacen.objects.filter(id_item_entrada_almacen=id_item_entrada).first()
#             #ACTUALIZACIÓN DE UN ITEM QUE YA EXISTA Y SEA ACTIVO FIJO
#             if item_entrada.id_bien.cod_tipo_bien == 'A':
#                 campo_inventario = Inventario.objects.filter(id_bien=item_entrada.id_bien.id_bien).first()

#                 #VALIDACIÓN QUE EL ÚLTIMO MOVIMIENTO EN INVENTARIO SEA LA ENTRADA A ACTUALIZAR
#                 if str(campo_inventario.id_registro_doc_ultimo_movimiento) != str(item_entrada.id_entrada_almacen.id_entrada_almacen):
#                     return Response({'success': False, 'detail': 'No se puede actualizar un elemento si el último registro en inventario no fue la entrada'}, status=status.HTTP_400_BAD_REQUEST)
#                 campo_inventario.id_bodega = bodega
#                 campo_inventario.valor_ingreso = valor_total_item
#                 campo_inventario.cod_estado_activo = cod_estado
#                 campo_inventario.save()

#                 serializer = SerializerUpdateItemEntradaActivosFijos(item_entrada, data=item, many=False)
#                 serializer.is_valid(raise_exception=True)
#                 serializer.save()
#                 # elementos_guardados.append(serializer.data)






#             return Response({'success':True, 'detail':'Se ha actualizado la entrada', 'data_entrada': serializer.data, 'data_items': items_guardados}, status=status.HTTP_201_CREATED)
#         else:
#             numero_entrada = entrada_data.get('numero_entrada_almacen')
#             numero_entrada_exist = EntradasAlmacen.objects.filter(numero_entrada_almacen=numero_entrada).first()
#             if numero_entrada_exist:
#                 entradas = EntradasAlmacen.objects.all().order_by('-numero_entrada_almacen').first()
#                 entrada_data['numero_entrada_almacen'] = entradas.numero_entrada_almacen + 1

#             serializer = self.serializer_class(data=entrada_data, many=False)
#             serializer.is_valid(raise_exception=True)
            
#             entrada_creada = serializer.save()
#             # return Response({'success':True, 'detail':'Se creó la entrada', 'data':serializer.data}, status=status.HTTP_201_CREATED)

#             for item in items_entrada:
#                 item['id_entrada_almacen'] = entrada_creada.pk

#             items_activos_fijos = list(filter(lambda item:item['id_bien_padre'] != None, items_entrada))
#             print(items_activos_fijos)
            
#             items_activos_fijos_guardados = []

#             for item in items_activos_fijos:
#                 id_item_entrada = item.get('id_item_entrada_almacen')
#                 id_bien_padre = item.get('id_bien_padre')
#                 doc_identificador_bien = item.get('doc_identificador_bien')
#                 id_porcentaje_iva = item.get('porcentaje_iva')
#                 cantidad_vida_util = item.get('cantidad_vida_util')
#                 id_unidad_medida_vida_util = item.get('id_unidad_medida_vida_util')
#                 valor_residual = item.get('valor_residual')
#                 tiene_hoja_vida = item.get('tiene_hoja_vida')
#                 id_bodega = item.get('id_bodega')
#                 valor_total_item = item.get('valor_total_item')
#                 cod_estado = item.get('cod_estado')

#                 #SI ENVIAN EL ID_ITEM_ENTRADA ENTONCES ACTUALIZAN
#                 if id_item_entrada != None:
#                     item_entrada = ItemEntradaAlmacen.objects.filter(id_item_entrada_almacen=id_item_entrada).first()
#                     #ACTUALIZACIÓN DE UN ITEM QUE YA EXISTA Y SEA ACTIVO FIJO
#                     if item_entrada.id_bien.cod_tipo_bien == 'A':
#                         campo_inventario = Inventario.objects.filter(id_bien=item_entrada.id_bien.id_bien).first()

#                         #VALIDACIÓN QUE EL ÚLTIMO MOVIMIENTO EN INVENTARIO SEA LA ENTRADA A ACTUALIZAR
#                         if str(campo_inventario.id_registro_doc_ultimo_movimiento) != str(item_entrada.id_entrada_almacen.id_entrada_almacen):
#                             return Response({'success': False, 'detail': 'No se puede actualizar un elemento si el último registro en inventario no fue la entrada'}, status=status.HTTP_400_BAD_REQUEST)
#                         campo_inventario.id_bodega = bodega
#                         campo_inventario.valor_ingreso = valor_total_item
#                         campo_inventario.cod_estado_activo = cod_estado
#                         campo_inventario.save()

#                         serializer = SerializerUpdateItemEntradaActivosFijos(item_entrada, data=item, many=False)
#                         serializer.is_valid(raise_exception=True)
#                         serializer.save()
#                         items_activos_fijos_guardados.append(serializer.data)

#                 #CREACIÓN DE UN ITEM ACTIVO FIJO EN BASE A CAMPOS HEREDADOS DEL PADRE
#                 bien_padre = CatalogoBienes.objects.filter(id_bien=id_bien_padre).first()
#                 bien_padre_serializado = CatalogoBienesSerializer(bien_padre)
                        
#                 #ASIGNACIÓN DEL ÚLTIMO NÚMERO DEL ELEMENTO
#                 ultimo_numero_elemento = CatalogoBienes.objects.filter(Q(codigo_bien=bien_padre.codigo_bien) & ~Q(nro_elemento_bien=None)).order_by('-nro_elemento_bien').first()
#                 numero_elemento = 1
#                 if ultimo_numero_elemento:
#                     numero_elemento = ultimo_numero_elemento.nro_elemento_bien + 1

#                 #ASIGNACIÓN DE INFORMACIÓN PARA LA CREACIÓN DEL ELEMENTO
#                 data_create = bien_padre_serializado.data
#                 data_create['nro_elemento_bien'] = numero_elemento
#                 data_create['doc_identificador_nro'] = doc_identificador_bien
#                 data_create['id_porcentaje_iva'] = id_porcentaje_iva
#                 data_create['cantidad_vida_util'] = cantidad_vida_util
#                 data_create['id_unidad_medida_vida_util'] = id_unidad_medida_vida_util
#                 data_create['valor_residual'] = valor_residual
#                 data_create['tiene_hoja_vida'] = tiene_hoja_vida
#                 data_create['id_bien_padre'] = id_bien_padre
#                 del data_create['id_bien']
#                 del data_create['maneja_hoja_vida']
#                 del data_create['visible_solicitudes']
#                 serializer = CatalogoBienesSerializer(data=data_create, many=False)
#                 serializer.is_valid(raise_exception=True)
#                 elemento_creado = serializer.save()

#                 #REGISTRAR LA ENTRADA EN INVENTARIO
#                 bodega = Bodegas.objects.filter(id_bodega=id_bodega).first()

#                 match entrada_creada.id_tipo_entrada.cod_tipo_entrada:
#                     case 1:
#                         tipo_doc_ultimo_movimiento = 'E_CPR'
#                     case 2:
#                         tipo_doc_ultimo_movimiento = 'E_DON'
#                     case 3:
#                         tipo_doc_ultimo_movimiento = 'E_RES'
#                     case 4:
#                         tipo_doc_ultimo_movimiento = 'E_CPS'
#                     case 5:
#                         tipo_doc_ultimo_movimiento = 'E_CMD'
#                     case 6:
#                         tipo_doc_ultimo_movimiento = 'E_CNV'
#                     case 7:
#                         tipo_doc_ultimo_movimiento = 'E_EMB'
#                     case 8:
#                         tipo_doc_ultimo_movimiento = 'E_INC'
#                     case _:
#                         return Response({'success': True, 'detail': 'El tipo de entrada ingresado no es valido'}, status=status.HTTP_400_BAD_REQUEST)

#                 registro_inventario = Inventario.objects.create(
#                     id_bien = elemento_creado,
#                     id_bodega = bodega,
#                     cod_tipo_entrada = entrada_creada.id_tipo_entrada,
#                     fecha_ingreso = datetime.now(),
#                     id_persona_origen = entrada_creada.id_proveedor,
#                     numero_doc_origen = entrada_creada.numero_entrada_almacen,
#                     valor_ingreso = valor_total_item,
#                     ubicacion_en_bodega = True,
#                     cod_estado_activo = cod_estado,
#                     fecha_ultimo_movimiento = datetime.now(),
#                     tipo_doc_ultimo_movimiento = tipo_doc_ultimo_movimiento,
#                     id_registro_doc_ultimo_movimiento = entrada_creada.id_entrada_almacen
#                 )

#                 if tiene_hoja_vida == True:
#                     match bien_padre.cod_tipo_activo:
#                         case 'Com':
#                             create_hoja_vida = HojaDeVidaComputadores.objects.create(
#                                 id_articulo = elemento_creado
#                             )
#                         case 'Veh':
#                             create_hoja_vida = HojaDeVidaVehiculos.objects.create(
#                                 id_articulo = elemento_creado
#                             )
#                         case 'OAc':
#                             create_hoja_vida = HojaDeVidaOtrosActivos.objects.create(
#                                 id_articulo = elemento_creado
#                             )
#                         case _:
#                             return Response({'success': False, 'detail': 'No existe el tipo de activo seleccionado'}, status=status.HTTP_400_BAD_REQUEST) 
#                 item['id_bien'] = elemento_creado.id_bien
#                 serializador_item_entrada = SerializerItemEntradaActivosFijos(data=item, many=False)
#                 serializador_item_entrada.is_valid(raise_exception=True)
#                 serializador_item_entrada.save()
#                 items_activos_fijos_guardados.append(serializador_item_entrada.data)

#             return Response({'success': True, 'data': items_activos_fijos_guardados})

                


#             #     #SI ENVIAN EL ID_ITEM_ENTRADA ENTONCES ACTUALIZAN
#             #     if id_item_entrada != None:
#             #         item_entrada = ItemEntradaAlmacen.objects.filter(id_item_entrada_almacen=id_item_entrada).first()
#             #         if item_entrada:
#             #             #ACTUALIZACIÓN DE UN ITEM QUE YA EXISTA Y SEA ACTIVO FIJO
#             #             if item_entrada.id_bien.cod_tipo_bien == 'A':
#             #                 campo_inventario = Inventario.objects.filter(id_bien=item_entrada.id_bien.id_bien).first()

#             #                 #VALIDACIÓN QUE EL ÚLTIMO MOVIMIENTO EN INVENTARIO SEA LA ENTRADA A ACTUALIZAR
#             #                 if str(campo_inventario.id_registro_doc_ultimo_movimiento) != str(item_entrada.id_entrada_almacen.id_entrada_almacen):
#             #                     return Response({'success': False, 'detail': 'No se puede actualizar un elemento si el último registro en inventario no fue la entrada'}, status=status.HTTP_400_BAD_REQUEST)
#             #                 campo_inventario.id_bodega = bodega
#             #                 campo_inventario.valor_ingreso = valor_total_item
#             #                 campo_inventario.cod_estado_activo = cod_estado
#             #                 campo_inventario.save()

#             #                 serializer = SerializerUpdateItemEntradaActivosFijos(item_entrada, data=item, many=False)
#             #                 serializer.is_valid(raise_exception=True)
#             #                 serializer.save()
#             #                 elementos_guardados.append(serializer.data)
#             #         else:
#             #             return Response({'success': False, 'detail': 'No se encontró ningun item entrada con el parámetro ingresado'}, status=status.HTTP_404_NOT_FOUND)

















        


# #                 #SI ENVIAN EL ID_ITEM_ENTRADA ENTONCES ACTUALIZAN
# #                 if id_item_entrada != None:
# #                     item_entrada = ItemEntradaAlmacen.objects.filter(id_item_entrada_almacen=id_item_entrada).first()
# #                     if item_entrada:
# #                         #ACTUALIZACIÓN DE UN ITEM QUE YA EXISTA Y SEA ACTIVO FIJO
# #                         if item_entrada.id_bien.cod_tipo_bien == 'A':
# #                             campo_inventario = Inventario.objects.filter(id_bien=item_entrada.id_bien.id_bien).first()

# #                             #VALIDACIÓN QUE EL ÚLTIMO MOVIMIENTO EN INVENTARIO SEA LA ENTRADA A ACTUALIZAR
# #                             if str(campo_inventario.id_registro_doc_ultimo_movimiento) != str(item_entrada.id_entrada_almacen.id_entrada_almacen):
# #                                 return Response({'success': False, 'detail': 'No se puede actualizar un elemento si el último registro en inventario no fue la entrada'}, status=status.HTTP_400_BAD_REQUEST)
# #                             campo_inventario.id_bodega = bodega
# #                             campo_inventario.valor_ingreso = valor_total_item
# #                             campo_inventario.cod_estado_activo = cod_estado
# #                             campo_inventario.save()

# #                             serializer = SerializerUpdateItemEntradaActivosFijos(item_entrada, data=item, many=False)
# #                             serializer.is_valid(raise_exception=True)
# #                             serializer.save()
# #                             elementos_guardados.append(serializer.data)
# #                     else:
# #                         return Response({'success': False, 'detail': 'No se encontró ningun item entrada con el parámetro ingresado'}, status=status.HTTP_404_NOT_FOUND)
