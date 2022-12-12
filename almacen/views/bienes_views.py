from almacen.models.bienes_models import CatalogoBienes
from rest_framework import generics, status
from rest_framework.views import APIView
from almacen.serializers.bienes_serializers import (
    CatalogoBienesSerializer,
    EntradaCreateSerializer,
    EntradaUpdateSerializer,
    CreateUpdateItemEntradaConsumoSerializer,
    SerializerItemEntradaActivosFijos,
    SerializerUpdateItemEntradaActivosFijos
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
from almacen.models.generics_models import UnidadesMedida , PorcentajesIVA 
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
                    id_marca = UnidadesMedida.objects.get(id_marca=data['id_marca'])
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
                                catalogo_bien = CatalogoBienes.objects.create(
                                    id_bien=data['id_bien'],
                                    codigo_bien=data['codigo_bien'],
                                    nombre=data['nombre'],
                                    cod_tipo_bien=data['cod_tipo_bien'],
                                    cod_tipo_activo=data['cod_tipo_activo'],
                                    nivel_jerarquico=data['nivel_jerarquico'],
                                    descripcion=data['descripcion'],
                                    id_marca=data['id_marca'],
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

                            catalogo_bien = CatalogoBienes.objects.create(
                                    id_bien=data['id_bien'],
                                    codigo_bien=data['codigo_bien'],
                                    nombre=data['nombre'],
                                    cod_tipo_bien=data['cod_tipo_bien'],
                                    cod_tipo_activo=data['cod_tipo_activo'],
                                    nivel_jerarquico=data['nivel_jerarquico'],
                                    descripcion=data['descripcion'],
                                    id_marca=data['id_marca'],
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
        codigo_bien = request.query_params.get('codigo-bien')
        nombre = request.query_params.get('nombre')

        # FILTROS
        if codigo_bien or nombre:
            nodo_found = []
            if codigo_bien and not nombre:
                nodo_found = CatalogoBienes.objects.filter(nro_elemento_bien=None, codigo_bien=codigo_bien).values().first()
            elif not codigo_bien and nombre:
                nodo_found = CatalogoBienes.objects.filter(nro_elemento_bien=None, nombre=nombre).values().first()
            elif codigo_bien and nombre:
                nodo_found = CatalogoBienes.objects.filter(nro_elemento_bien=None, codigo_bien=codigo_bien, nombre=nombre).values().first()
            
            if nodo_found:
                nodo_padre = [nodo_found]
                id_bien_padre = nodo_found['id_bien_padre_id']
                for i in range(nodo_found['nivel_jerarquico']-1, 0, -1):
                    nodo_padre_for = CatalogoBienes.objects.filter(id_bien=id_bien_padre).values().first()
                    nodo_padre_for['nodos_hijos'] = nodo_padre
                    id_bien_padre = nodo_padre_for['id_bien_padre_id']
                    nodo_padre = [nodo_padre_for]
                return Response({'status':True, 'detail':'Se encontraron resultados', 'data':nodo_padre}, status=status.HTTP_200_OK)
            else:
                nodo_found = []
                return Response({'status':True, 'detail':'No se encontró el nodo por los parámetros indicados', 'data':nodo_found}, status=status.HTTP_200_OK)
        
        # GET TODOS LOS NODOS
        else:
            nodos_principales = CatalogoBienes.objects.filter(nro_elemento_bien=None, nivel_jerarquico=1).values()
            if not nodos_principales:
                return Response({'success':True, 'detail':'No se encontró nada en almacén', 'data':nodos_principales}, status=status.HTTP_200_OK)
            
            for nodo in nodos_principales:
                nodos_nivel_dos = CatalogoBienes.objects.filter(nro_elemento_bien=None, nivel_jerarquico=2, id_bien_padre=nodo['id_bien']).values()
                if nodos_nivel_dos:
                    nodo['nodos_hijos'] = nodos_nivel_dos
                    for nodo_dos in nodos_nivel_dos:
                        nodos_nivel_tres = CatalogoBienes.objects.filter(nro_elemento_bien=None, nivel_jerarquico=3, id_bien_padre=nodo_dos['id_bien']).values()
                        if nodos_nivel_tres:
                            nodo_dos['nodos_hijos'] = nodos_nivel_tres
                            for nodo_tres in nodos_nivel_tres:
                                nodos_nivel_cuatro = CatalogoBienes.objects.filter(nro_elemento_bien=None, nivel_jerarquico=4, id_bien_padre=nodo_tres['id_bien']).values()
                                if nodos_nivel_cuatro:
                                    nodo_tres['nodos_hijos'] = nodos_nivel_cuatro
                                    for nodo_cuatro in nodos_nivel_cuatro:
                                        nodos_nivel_cinco = CatalogoBienes.objects.filter(nro_elemento_bien=None, nivel_jerarquico=5, id_bien_padre=nodo_cuatro['id_bien']).values()
                                        if nodos_nivel_cinco:
                                            nodo_cuatro['nodos_hijos'] = nodos_nivel_cinco
                
            return Response({'success':True, 'detail':'Se encontró lo siguiente en almacén', 'data':nodos_principales}, status=status.HTTP_200_OK)


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
        return Response({'success':True,'detail':'no se econtrò elementos','data':bien},status=status.HTTP_404_NOT_FOUND)
    
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


class CreateUpdateDeleteItemsEntrada(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CreateUpdateItemEntradaConsumoSerializer
    queryset = ItemEntradaAlmacen.objects.all()

    def put(self, request, id_entrada):
        entrada = EntradasAlmacen.objects.filter(id_entrada_almacen=id_entrada).first()
        data = request.data
        if entrada:
            #VALIDACIÓN DEL ID_ENTRADA
            entradas_items_list = [item['id_entrada_almacen'] for item in data]
            if len(set(entradas_items_list)) != 1:
                return Response({'success':False, 'detail':'Debe validar que los items pertenezcan a una misma entrada'}, status=status.HTTP_400_BAD_REQUEST)
            elif entradas_items_list[0] != int(id_entrada):
                return Response({'success':False, 'detail':'El id entrada de la petición debe ser igual al enviado en url'}, status=status.HTTP_400_BAD_REQUEST)
            
            #ELIMINACIÓN DE ITEMS NO ENVIADOS PARA ACTIVOS FIJOS
            items_list = [item['id_item_entrada_almacen'] for item in data]
            items_entrada = ItemEntradaAlmacen.objects.filter(id_entrada_almacen=id_entrada)
            items_entrada_list = [item.id_item_entrada_almacen for item in items_entrada]
            
            if not set(items_entrada_list).issubset(items_list): 
                item_difference_list = [item for item in items_entrada_list if item not in items_list]
                
                for item in item_difference_list:
                    #VALIDACIÓN SI TIENE HOJA DE VIDA
                    item_instance = ItemEntradaAlmacen.objects.filter(id_item_entrada_almacen=item).first()
                    #ELIMINACIÓN SI EL ITEM DE LA ENTRADA TIENE UN BIEN ACTIVO FIJO
                    if item_instance.id_bien.cod_tipo_bien == 'A':
                        item_hv_comp = HojaDeVidaComputadores.objects.filter(id_articulo=item_instance.id_bien.id_bien).first()
                        item_hv_veh = HojaDeVidaVehiculos.objects.filter(id_articulo=item_instance.id_bien.id_bien).first()
                        item_hv_oac = HojaDeVidaOtrosActivos.objects.filter(id_articulo=item_instance.id_bien.id_bien).first()
                        item_instance_serializer = SerializerItemEntradaActivosFijos(item_instance, many=False)

                        #VALIDACIÓN SI LA ENTRADA FUE EL ÚLTIMO MOVIMIENTO EN INVENTARIO
                        inventario_item_instance = Inventario.objects.filter(id_bien=item_instance.id_bien.id_bien).first()
                        if str(item_instance.id_entrada_almacen.id_entrada_almacen) != str(inventario_item_instance.id_registro_doc_ultimo_movimiento):
                            return Response({'success': False, 'detail': 'No se puede eliminar este item si la entrada no fue su último movimiento', 'data': item_instance_serializer.data}, status=status.HTTP_403_FORBIDDEN)
                        #VALIDACIÓN SI EL ELEMENTO DE LA ENTRADA TIENE HOJA DE VIDA
                        if item_hv_comp or item_hv_veh or item_hv_oac:
                            return Response({'success': False, 'detail': 'No se puede eliminar este item por que el elemento tiene hoja de vida', 'data': item_instance_serializer.data}, status=status.HTTP_403_FORBIDDEN)
                        #SE TRAE EL BIEN DEL ITEM QUE ESTÁ EN CATALOGO
                        bien_eliminar = CatalogoBienes.objects.filter(id_bien=item_instance.id_bien.id_bien).first()

                        inventario_item_instance.delete()
                        bien_eliminar.delete()
                        item_instance.delete()

            elementos_guardados = []
            #ITERACIÓN POR CADA ITEM ENVIADO EN DATA
            for item in data:
                #OBTENER DATA DEL REQUEST
                id_item_entrada = item.get('id_item_entrada_almacen')
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

                #VALIDACIÓN DE EXISTENCIA DE BODEGAS
                bodega = Bodegas.objects.filter(id_bodega=id_bodega).first()
                if not bodega:
                    return Response({'success': False, 'detail': 'No existe ninguna bodega con el parámetro ingresado'}, status=status.HTTP_404_NOT_FOUND)

                #SI ENVIAN EL ID_ITEM_ENTRADA ENTONCES ACTUALIZAN
                if id_item_entrada != None:
                    item_entrada = ItemEntradaAlmacen.objects.filter(id_item_entrada_almacen=id_item_entrada).first()
                    if item_entrada:
                        #ACTUALIZACIÓN DE UN ITEM QUE YA EXISTA Y SEA ACTIVO FIJO
                        if item_entrada.id_bien.cod_tipo_bien == 'A':
                            campo_inventario = Inventario.objects.filter(id_bien=item_entrada.id_bien.id_bien).first()

                            #VALIDACIÓN QUE EL ÚLTIMO MOVIMIENTO EN INVENTARIO SEA LA ENTRADA A ACTUALIZAR
                            if str(campo_inventario.id_registro_doc_ultimo_movimiento) != str(item_entrada.id_entrada_almacen.id_entrada_almacen):
                                return Response({'success': False, 'detail': 'No se puede actualizar un elemento si el último registro en inventario no fue la entrada'}, status=status.HTTP_400_BAD_REQUEST)
                            campo_inventario.id_bodega = bodega
                            campo_inventario.valor_ingreso = valor_total_item
                            campo_inventario.cod_estado_activo = cod_estado
                            campo_inventario.save()

                            serializer = SerializerUpdateItemEntradaActivosFijos(item_entrada, data=item, many=False)
                            serializer.is_valid(raise_exception=True)
                            serializer.save()
                            elementos_guardados.append(serializer.data)
                    else:
                        return Response({'success': False, 'detail': 'No se encontró ningun item entrada con el parámetro ingresado'}, status=status.HTTP_404_NOT_FOUND)
                else:
                    #CREAR EL ELEMENTO EN CATALOGO DE BIENES
                    if id_bien_padre:
                        bien_padre = CatalogoBienes.objects.filter(id_bien=id_bien_padre).first()
                        if not bien_padre:
                            return Response({'success': False, 'detail': 'No existe el bien padre ingresado'}, status=status.HTTP_400_BAD_REQUEST)
                        #CREACIÓN DE UN ITEM ACTIVO FIJO EN BASE A CAMPOS HEREDADOS DEL PADRE
                        if bien_padre.cod_tipo_bien == 'A':
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
                            match entrada.id_tipo_entrada.cod_tipo_entrada:
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
                                cod_tipo_entrada = entrada.id_tipo_entrada,
                                fecha_ingreso = datetime.now(),
                                id_persona_origen = entrada.id_proveedor,
                                numero_doc_origen = entrada.numero_entrada_almacen,
                                valor_ingreso = valor_total_item,
                                ubicacion_en_bodega = True,
                                cod_estado_activo = cod_estado,
                                fecha_ultimo_movimiento = datetime.now(),
                                tipo_doc_ultimo_movimiento = tipo_doc_ultimo_movimiento,
                                id_registro_doc_ultimo_movimiento = entrada.id_entrada_almacen
                            )

                            #CREACIÓN DE LA HOJA DE VIDA
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
                            elementos_guardados.append(serializador_item_entrada.data)
                    else:
                        return Response({'success': False, 'detail': 'Para realizar esta acción es necesario enviar el id_bien_padre'}, status=status.HTTP_400_BAD_REQUEST)

            return Response({'detail': 'Se guardó exitosamente', 'data': elementos_guardados}, status=status.HTTP_201_CREATED)
        else:
            return Response({'success': False, 'detail': 'No se encontró ninguna entrada con el parámetro ingresado'}, status=status.HTTP_404_NOT_FOUND)