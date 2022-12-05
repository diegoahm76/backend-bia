from almacen.models.bienes_models import CatalogoBienes
from rest_framework import generics, status
from rest_framework.views import APIView
from almacen.serializers.bienes_serializers import (
    CatalogoBienesSerializer
)
from almacen.models.inventario_models import (
    Inventario,
) 
from almacen.models.generics_models import UnidadesMedida , PorcentajesIVA 

from seguridad.utils import Util  
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError


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
