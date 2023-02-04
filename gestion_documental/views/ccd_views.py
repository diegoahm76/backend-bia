from rest_framework import status
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Q
from seguridad.utils import Util
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from gestion_documental.serializers.ccd_serializers import (
    SubseriesDocSerializer,
    CCDPostSerializer,
    CCDPutSerializer,
    CCDActivarSerializer,
    CCDSerializer,
    SeriesDocPostSerializer,
    SeriesDocSerializer,
    SeriesSubseriesUnidadOrgSerializer
)
from almacen.models.organigrama_models import Organigramas
from operator import itemgetter
from seguridad.models import (
    User,
    Modulos,
    Permisos
)
from gestion_documental.models.ccd_models import (
    CuadrosClasificacionDocumental,
    SeriesDoc,
    SubseriesDoc,
    SeriesSubseriesUnidadOrg
)
from almacen.models.organigrama_models import (
    UnidadesOrganizacionales
)
from gestion_documental.models.trd_models import (
    TablaRetencionDocumental
)

import copy

class CreateCuadroClasificacionDocumental(generics.CreateAPIView):
    serializer_class = CCDPostSerializer
    queryset = CuadrosClasificacionDocumental.objects.all()
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            pass
        except:
            return Response({'success': False, 'detail': 'Valide la información ingresada, el id organigrama es requerido, el nombre y la versión son requeridos y deben ser únicos'}, status=status.HTTP_400_BAD_REQUEST)
        
        #Validación de seleccionar solo trd terminados
        organigrama = serializer.validated_data.get('id_organigrama')
        organigrama_instance = Organigramas.objects.filter(id_organigrama=organigrama.id_organigrama).first()
        if organigrama_instance:
            if organigrama_instance.fecha_terminado == None:
                return Response({'success': False, 'detail': 'No se pueden seleccionar organigramas que no estén terminados'}, status=status.HTTP_403_FORBIDDEN)
            serializador = serializer.save()

            #Auditoria Crear Cuadro de Clasificación Documental
            usuario = request.user.id_usuario
            descripcion = {"Nombre": str(serializador.nombre), "Versión": str(serializador.version)}
            direccion=Util.get_client_ip(request)
            auditoria_data = {
                "id_usuario" : usuario,
                "id_modulo" : 27,
                "cod_permiso": "CR",
                "subsistema": 'GEST',
                "dirip": direccion,
                "descripcion": descripcion, 
            }
            Util.save_auditoria(auditoria_data)
            
            return Response({'success': True, 'detail': 'Cuadro de Clasificación Documental creado exitosamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({'success': False, 'detail': 'No existe un organigrama con el id_organigrama enviado'}, status=status.HTTP_400_BAD_REQUEST)

class UpdateCuadroClasificacionDocumental(generics.RetrieveUpdateAPIView):
    serializer_class = CCDPutSerializer
    queryset = CuadrosClasificacionDocumental.objects.all()
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            ccd = CuadrosClasificacionDocumental.objects.get(id_ccd=pk)
            previoud_ccd = copy.copy(ccd)
            pass
        except:
            return Response({'success': False, 'detail': 'No existe ningún Cuadro de Clasificación Documental con los parámetros ingresados'}, status=status.HTTP_404_NOT_FOUND)

        if ccd.fecha_terminado:
            return Response({'success': False,'detail': 'No se puede actualizar un CCD terminado'}, status=status.HTTP_403_FORBIDDEN)
            
        serializer = self.serializer_class(ccd, data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            pass 
        except:
            return Response({'success': False, 'detail': 'Validar data enviada, el nombre y la versión son requeridos y deben ser únicos'}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()
        
        # AUDITORIA DE UPDATE DE CCD
        user_logeado = request.user.id_usuario
        dirip = Util.get_client_ip(request)
        descripcion = {'nombre':str(previoud_ccd.nombre), 'version':str(previoud_ccd.version)}
        valores_actualizados={'previous':previoud_ccd, 'current':ccd}
        auditoria_data = {
            'id_usuario': user_logeado,
            'id_modulo': 27,
            'cod_permiso': 'AC',
            'subsistema': 'GEST',
            'dirip': dirip,
            'descripcion': descripcion,
            'valores_actualizados': valores_actualizados
        }
        Util.save_auditoria(auditoria_data)
        
        return Response({'success': True, 'detail': 'Cuadro de Clasificación Documental actualizado exitosamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)


class FinalizarCuadroClasificacionDocumental(generics.RetrieveUpdateAPIView):
    serializer_class = CCDActivarSerializer
    queryset = CuadrosClasificacionDocumental

    def put(self, request, pk):
        ccd = CuadrosClasificacionDocumental.objects.filter(id_ccd=pk).first()
        confirm = request.query_params.get('confirm')
        if ccd:
            #Validacion existencia del ccd a finalizar
            if ccd.fecha_terminado == None:
                
                unidades = UnidadesOrganizacionales.objects.filter(Q(id_organigrama=ccd.id_organigrama) & ~Q(cod_agrupacion_documental=None))
                unidades_list = [unidad.id_unidad_organizacional for unidad in unidades]
                
                series = SeriesDoc.objects.filter(id_ccd=pk)
                series_list = [serie.id_serie_doc for serie in series]

                subseries = SubseriesDoc.objects.filter(id_ccd=pk)
                subseries_list = [subserie.id_subserie_doc for subserie in subseries]


                serie_subserie_unidad = SeriesSubseriesUnidadOrg.objects.filter(id_serie_doc__in=series_list)
                unidades_asignacion_list = [serie.id_unidad_organizacional.id_unidad_organizacional for serie in serie_subserie_unidad]
                series_asignacion_list = [serie.id_serie_doc.id_serie_doc for serie in serie_subserie_unidad]

                subseries_asignacion_list = [subserie.id_sub_serie_doc.id_subserie_doc for subserie in serie_subserie_unidad if subserie.id_sub_serie_doc]

                if not confirm or confirm != 'true':
                    if not set(unidades_list).issubset(unidades_asignacion_list):
                        unidades_difference_list = [unidad for unidad in unidades_list if unidad not in unidades_asignacion_list]
                        unidades_difference_instance = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional__in=unidades_difference_list)
                        unidades_names = [unidad.nombre for unidad in unidades_difference_instance]
                        print('Unidades sin usar: ', unidades_difference_instance)
                        return Response({'success': False, 'detail': 'Debe asociar todas las unidades', 'data': unidades_names, 'delete':False}, status=status.HTTP_400_BAD_REQUEST)

                    if not set(series_list).issubset(series_asignacion_list):
                        #Mostrar las series sin asignar
                        series_difference_list = [serie for serie in series_list if serie not in series_asignacion_list]
                        series_difference_instance = SeriesDoc.objects.filter(id_serie_doc__in=series_difference_list)
                        series_names = [serie.nombre for serie in series_difference_instance]
                        return Response({'success': False, 'detail': 'Debe asociar todas las series', 'data': series_names, 'delete':True}, status=status.HTTP_400_BAD_REQUEST)

                    #Agregar validación para cuando una lista viene vacia
                    if subseries_list and not subseries_asignacion_list:
                        subseries_difference_list = [subserie for subserie in subseries_list if subserie not in subseries_asignacion_list]
                        subseries_difference_instance = SubseriesDoc.objects.filter(id_subserie_doc__in=subseries_difference_list)
                        subseries_names = [subserie.nombre for subserie in subseries_difference_instance]
                        return Response({'success': False, 'detail': 'Debe asociar todas las subseries creadas, no hay ninguna asignada', 'data': subseries_names, 'delete':True}, status=status.HTTP_400_BAD_REQUEST)
                    
                    if not set(subseries_list).issubset(set(subseries_asignacion_list)):
                        subseries_difference_list = [subserie for subserie in subseries_list if subserie not in subseries_asignacion_list]
                        subseries_difference_instance = SubseriesDoc.objects.filter(id_subserie_doc__in=subseries_difference_list)
                        subseries_names = [subserie.nombre for subserie in subseries_difference_instance]
                        return Response({'success': False, 'detail': 'Debe asociar todas las subseries creadas', 'data': subseries_names, 'delete':True}, status=status.HTTP_400_BAD_REQUEST)

                if confirm == 'true':
                    if not set(series_list).issubset(series_asignacion_list):
                        #Mostrar las series sin asignar
                        series_difference_list = [serie for serie in series_list if serie not in series_asignacion_list]
                        series_difference_instance = SeriesDoc.objects.filter(id_serie_doc__in=series_difference_list)
                        #return Response({'success': False, 'detail': 'Debe asociar todas las series', 'Series sin asignar': series_difference_instance}, status=status.HTTP_400_BAD_REQUEST)

                    #Agregar validación para cuando una lista viene vacia
                    if subseries_list and not subseries_asignacion_list:
                        subseries_difference_list = [subserie for subserie in subseries_list if subserie not in subseries_asignacion_list]
                        subseries_difference_instance = SubseriesDoc.objects.filter(id_subserie_doc__in=subseries_difference_list)
                        #return Response({'success': False, 'detail': 'Debe asociar todas las subseries creadas, no hay ninguna asignada', 'Subseries sin asignar': subseries_difference_instance}, status=status.HTTP_400_BAD_REQUEST)
                    if not set(subseries_list).issubset(set(subseries_asignacion_list)):
                        subseries_difference_list = [subserie for subserie in subseries_list if subserie not in subseries_asignacion_list]
                        subseries_difference_instance = SubseriesDoc.objects.filter(id_subserie_doc__in=subseries_difference_list)
                        #return Response({'success': False, 'detail': 'Debe asociar todas las subseries creadas', 'Subseries sin asignar': subseries_difference_instance}, status=status.HTTP_400_BAD_REQUEST)

                    series_difference_instance.delete()
                    subseries_difference_instance.delete()
                    
                ccd.fecha_terminado = datetime.now()
                ccd.save()
                return Response({'success': True, 'detail': 'Finalizado el CCD'}, status=status.HTTP_201_CREATED)
            
            else:
                return Response({'success': False, 'detail': 'Ya se encuentra finalizado este CCD'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'success': False, 'detail': 'No se encontró ningún CCD con estos parámetros'}, status=status.HTTP_404_NOT_FOUND)    
        
        

class GetCuadroClasificacionDocumental(generics.ListAPIView):
    serializer_class = CCDSerializer  
    queryset = CuadrosClasificacionDocumental.objects.all()

    def get(self, request):
        consulta = request.query_params.get('pk')
        if consulta == None:
            ccds = self.queryset.all()
            
            if len(ccds) == 0:
                return Response({'success':True, 'detail':'Aún no hay Cuadros de Clasificación Documental registrados', 'data':[]}, status=status.HTTP_200_OK)
            
            serializer = self.serializer_class(ccds, many=True)
            
            return Response({'success': True, 'detail':'Se encontraron los siguientes CCDs', 'data':serializer.data}, status=status.HTTP_200_OK) 
        else:
            ccd = CuadrosClasificacionDocumental.objects.filter(id_ccd=consulta)
        
            if len(ccd) == 0:
                return Response({'success':False, 'detail':'No se encontró el Cuadro de Clasificación Documental ingresado'}, status=status.HTTP_404_NOT_FOUND)

            serializer = self.serializer_class(ccd, many=True)
        
            return Response({'success': True,'detail':'Se encontró el siguiente CCD', 'data':serializer.data}, status=status.HTTP_200_OK)

class GetCCDTerminado(generics.ListAPIView):
    serializer_class = CCDSerializer  
    queryset = CuadrosClasificacionDocumental.objects.filter(~Q(fecha_terminado = None) & Q(fecha_retiro_produccion=None))

#Crear Series documentales
class CreateSeriesDoc(generics.UpdateAPIView):
    serializer_class = SeriesDocPostSerializer
    queryset = SeriesDoc.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self, request, id_ccd):
        id_ccd_ingresada = id_ccd
        data_ingresada = request.data
        
        # VALIDACIONES
        fecha_ccd = (CuadrosClasificacionDocumental.objects.filter(id_ccd=id_ccd_ingresada).values().first())
        if fecha_ccd:
            if fecha_ccd['fecha_terminado'] != None:
                return Response({'success':False, "detail" : "No se pueden realizar modificaciones sobre esta CCD, ya está terminado"}, status=status.HTTP_400_BAD_REQUEST)    
        ccd = CuadrosClasificacionDocumental.objects.filter(id_ccd = id_ccd_ingresada).first()
        
        usuario = request.user.id_usuario
        descripcion = {"nombre": str(ccd.nombre), "version": str(ccd.version)}
        direccion = Util.get_client_ip(request)
        
        if ccd == None:
            return Response({'success': False, "detail" : "No se encontró esa ccd"}, status=status.HTTP_400_BAD_REQUEST)
        if request.data == []:
            series_eliminar = SeriesDoc.objects.filter(id_ccd=id_ccd)
            series_eliminar_id = [serie.id_serie_doc for serie in series_eliminar]
            
            serie_subserie_unidad = SeriesSubseriesUnidadOrg.objects.filter(id_serie_doc__in=series_eliminar_id)
            if serie_subserie_unidad:
                return Response({'success':False, 'detail':'Una o varias series a eliminar ya están asociadas al CCD, por favor eliminar asociaciones primero'})
            
            valores_eliminados_detalles = [{'nombre':serie.nombre, 'codigo':serie.codigo} for serie in series_eliminar]
                    
            series_eliminar.delete()
            
            # AUDITORIA MAESTRO DETALLE
            auditoria_data = {
                "id_usuario" : usuario,
                "id_modulo" : 27,
                "cod_permiso": "AC",
                "subsistema": 'GEST',
                "dirip": direccion,
                "descripcion": descripcion,
                "valores_eliminados_detalles": valores_eliminados_detalles
            }
            Util.save_auditoria_maestro_detalle(auditoria_data)   

            return Response({'success':True, 'detail':'Se han eliminado todas las series'}, status=status.HTTP_204_NO_CONTENT)
           
        ccd_list = [subserie['id_ccd'] for subserie in data_ingresada]

        if len(set(ccd_list)) != 1:
            return Response({'success':False, 'detail':'Debe validar que las subseries pertenezcan a un mismo CCD'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            if ccd_list[0] != int(id_ccd):
                return Response({'success':False, 'detail':'El id ccd de la petición debe ser igual al enviado en url'}, status=status.HTTP_400_BAD_REQUEST)
                            
                                     
        # SE OBTIENEN LOS DATOS A ACTUALIZAR Y A CREAR
        series_update = list(filter(lambda serie: serie['id_serie_doc'] != None, data_ingresada))
        series_create = list(filter(lambda serie: serie['id_serie_doc'] == None, data_ingresada))           
        
        data = []

        # CREATE
        valores_creados_detalles = []
        
        series_id_create = []
        if series_create:
            serializer = self.serializer_class(data=series_create, many=True)
            serializer.is_valid(raise_exception=True)
            serializador = serializer.save()
            series_id_create.extend([serie.id_serie_doc for serie in serializador])
            valores_creados_detalles = [{'nombre':serie['nombre'], 'codigo':serie['codigo']} for serie in series_create]
            for serie in serializer.data:
                data.append(serie)

        # UPDATE SERIES
        valores_actualizados_detalles = []
        
        if series_update:
            for i in series_update:
                instancia = SeriesDoc.objects.filter(id_serie_doc=i['id_serie_doc']).first()
                previous_serie = copy.copy(instancia)
                if instancia:
                    for serie in series_update:
                        data.append(serie)
                    descripcion_subserie = {'nombre':previous_serie.nombre, 'codigo':previous_serie.codigo}
                    serializer = self.serializer_class(instancia, data=i, many=False)
                    serializer.is_valid(raise_exception=True)
                    serializador = serializer.save()
                    valores_actualizados_detalles.append({'descripcion':descripcion_subserie, 'previous':previous_serie, 'current':instancia})

        # ELIMINAR SERIES
        lista_series_id = [serie['id_serie_doc'] for serie in series_update]
        lista_series_id.extend(series_id_create)
        series_eliminar = SeriesDoc.objects.filter(id_ccd=id_ccd).exclude(id_serie_doc__in=lista_series_id)
        
        series_eliminar_id = [serie.id_serie_doc for serie in series_eliminar]
        serie_subserie_unidad = SeriesSubseriesUnidadOrg.objects.filter(id_serie_doc__in=series_eliminar_id)
        
        if serie_subserie_unidad:
            return Response({'success':False, 'detail':'Una o varias series a eliminar ya están asociadas al CCD, por favor eliminar asociaciones primero'})
        
        valores_eliminados_detalles = [{'nombre':serie.nombre, 'codigo':serie.codigo} for serie in series_eliminar]
        
        series_eliminar.delete()
        
        # AUDITORIA MAESTRO DETALLE
        auditoria_data = {
            "id_usuario" : usuario,
            "id_modulo" : 27,
            "cod_permiso": "AC",
            "subsistema": 'GEST',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_actualizados_detalles": valores_actualizados_detalles,
            "valores_creados_detalles": valores_creados_detalles,
            "valores_eliminados_detalles": valores_eliminados_detalles
        }
        Util.save_auditoria_maestro_detalle(auditoria_data)    
            
        return Response({'success': True, "detail" : "Datos guardados con éxito", 'data': data}, status=status.HTTP_201_CREATED)

class GetSeriesDoc(generics.ListAPIView):
    serializer_class = SeriesDocSerializer
    
    def get(self, request, id_ccd):
        dato_buscado = id_ccd
        if dato_buscado == None:
            series_doc = SeriesDoc.objects.all().values()
            if len(series_doc) == 0:
                return Response({'success': False, "detail" : 'Aún no hay series documentales registradas'}, status=status.HTTP_404_NOT_FOUND)
            return Response({'Series documentales' : series_doc}, status=status.HTTP_200_OK) 
        series_doc = SeriesDoc.objects.filter(id_ccd=int(dato_buscado)).values()
        if len(series_doc) == 0:
            return Response({'success': False, "detail" : 'No se encontró la serie documental ingresada'}, status=status.HTTP_404_NOT_FOUND)
        ccd = CuadrosClasificacionDocumental.objects.filter(id_ccd = dato_buscado).values()
        datos_finales = {"CCD" : ccd, "Series documentales" : series_doc}
        return Response({'success': True, "detail" : datos_finales}, status=status.HTTP_200_OK)


class UpdateSubseriesDoc(generics.UpdateAPIView):
    serializer_class = SubseriesDocSerializer
    queryset = SubseriesDoc.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self, request, id_ccd):
        data = request.data
        ccd = CuadrosClasificacionDocumental.objects.filter(id_ccd=id_ccd).first()
        usuario = request.user.id_usuario
        descripcion = {"nombre": str(ccd.nombre), "version": str(ccd.version)}
        direccion = Util.get_client_ip(request)
        if ccd:
            if not ccd.fecha_terminado:
                if data:
                    # VALIDAR QUE EL ID_CCD SEA EL MISMO
                    ccd_list = [subserie['id_ccd'] for subserie in data]
                    if len(set(ccd_list)) != 1:
                        return Response({'success':False, 'detail':'Debe validar que las subseries pertenezcan a un mismo CCD'}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        print(ccd_list[0])
                        if ccd_list[0] != int(id_ccd):
                            return Response({'success':False, 'detail':'El id ccd de la petición debe ser igual al enviado en url'}, status=status.HTTP_400_BAD_REQUEST)
                                     
                    # VALIDAR QUE LOS CODIGOS SEAN UNICOS
                    codigos_list = [subserie['codigo'] for subserie in data]
                    if len(codigos_list) != len(set(codigos_list)):
                        return Response({'success':False, 'detail':'Debe validar que los códigos de las subseries sean únicos'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    # VALIDAR QUE LOS NOMBRES SEAN UNICOS
                    nombres_list = [subserie['nombre'] for subserie in data]
                    if len(nombres_list) != len(set(nombres_list)):
                        return Response({'success':False, 'detail':'Debe validar que los nombres de las subseries sean únicos'}, status=status.HTTP_400_BAD_REQUEST)

                    subseries_modificadas = []

                    # CREAR SUBSERIES
                    valores_creados_detalles = []
                    
                    subseries_create = list(filter(lambda subserie: subserie['id_subserie_doc'] == None, data))
                    subseries_id_create = []
                    print(subseries_create)
                    if subseries_create:
                        serializer = self.serializer_class(data=subseries_create, many=True)
                        serializer.is_valid(raise_exception=True)
                        serializador = serializer.save()
                        subseries_id_create.extend([subserie.id_subserie_doc for subserie in serializador])
                        valores_creados_detalles = [{'nombre':subserie['nombre'], 'codigo':subserie['codigo']} for subserie in subseries_create]
                        
                        for subserie in serializer.data:
                            subseries_modificadas.append(subserie)

                    # ACTUALIZAR SUBSERIES
                    valores_actualizados_detalles = []
                    
                    subseries_update = list(filter(lambda subserie: subserie['id_subserie_doc'] != None, data))
                    if subseries_update:
                        for subserie in subseries_update:
                            subserie_existe = SubseriesDoc.objects.filter(id_subserie_doc=subserie['id_subserie_doc']).first()
                            previous_subserie = copy.copy(subserie_existe)
                            if subserie_existe:
                                for subserie in subseries_update:
                                    subseries_modificadas.append(subserie)
                                descripcion_subserie = {'nombre':previous_subserie.nombre, 'codigo':previous_subserie.codigo}
                                serializer = self.serializer_class(subserie_existe, data=subserie)
                                serializer.is_valid(raise_exception=True)
                                serializer.save()
                                valores_actualizados_detalles.append({'descripcion':descripcion_subserie, 'previous':previous_subserie, 'current':subserie_existe})

                    # ELIMINAR SUBSERIES
                    lista_subseries_id = [subserie['id_subserie_doc'] for subserie in subseries_update]
                    lista_subseries_id.extend(subseries_id_create)
                    subseries_eliminar = SubseriesDoc.objects.filter(id_ccd=id_ccd).exclude(id_subserie_doc__in=lista_subseries_id)
                    
                    # VALIDAR QUE NO SE ESTÉN USANDO LAS SUBSERIES A ELIMINAR
                    subseries_eliminar_id = [subserie.id_subserie_doc for subserie in subseries_eliminar]
                    serie_subserie_unidad = SeriesSubseriesUnidadOrg.objects.filter(id_sub_serie_doc__in=subseries_eliminar_id)
                    if serie_subserie_unidad:
                        return Response({'success':False, 'detail':'Una o varias subseries a eliminar ya están asociadas al CCD, por favor eliminar asociaciones primero'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    valores_eliminados_detalles = [{'nombre':subserie.nombre, 'codigo':subserie.codigo} for subserie in subseries_eliminar]

                    subseries_eliminar.delete()
                    
                    # AUDITORIA MAESTRO DETALLE
                    auditoria_data = {
                        "id_usuario" : usuario,
                        "id_modulo" : 27,
                        "cod_permiso": "AC",
                        "subsistema": 'GEST',
                        "dirip": direccion,
                        "descripcion": descripcion,
                        "valores_actualizados_detalles": valores_actualizados_detalles,
                        "valores_creados_detalles": valores_creados_detalles,
                        "valores_eliminados_detalles": valores_eliminados_detalles
                    }
                    Util.save_auditoria_maestro_detalle(auditoria_data)
                    
                    return Response({'success':True, 'detail':'Se ha realizado cambios con las subseries', 'data': data}, status=status.HTTP_201_CREATED)
                else:
                    # VALIDAR QUE NO SE ESTÉN USANDO LAS SUBSERIES A ELIMINAR
                    subseries_eliminar = SubseriesDoc.objects.filter(id_ccd=id_ccd)
                    subseries_eliminar_id = [subserie.id_subserie_doc for subserie in subseries_eliminar]
                    serie_subserie_unidad = SeriesSubseriesUnidadOrg.objects.filter(id_sub_serie_doc__in=subseries_eliminar_id)
                    if serie_subserie_unidad:
                        return Response({'success':False, 'detail':'Una o varias subseries a eliminar ya están asociadas al CCD, por favor eliminar asociaciones primero'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    valores_eliminados_detalles = [{'nombre':subserie.nombre, 'codigo':subserie.codigo} for subserie in subseries_eliminar]
                    
                    subseries_eliminar.delete()
                    
                    # AUDITORIA MAESTRO DETALLE
                    auditoria_data = {
                        "id_usuario" : usuario,
                        "id_modulo" : 27,
                        "cod_permiso": "AC",
                        "subsistema": 'GEST',
                        "dirip": direccion,
                        "descripcion": descripcion,
                        "valores_eliminados_detalles": valores_eliminados_detalles
                    }
                    Util.save_auditoria_maestro_detalle(auditoria_data)

                    return Response({'success':True, 'detail':'Se han eliminado todas las subseries'}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'success':False, 'detail':'El CCD ya está terminado, por lo cual no es posible realizar acciones sobre las subseries'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'success':False, 'detail':'El CCD no existe'}, status=status.HTTP_404_NOT_FOUND)

class GetSubseries(generics.ListAPIView):
    serializer_class = SubseriesDocSerializer
    queryset = SubseriesDoc.objects.all()
    
    def get(self, request, id_ccd):
        ccd = CuadrosClasificacionDocumental.objects.filter(id_ccd=id_ccd).first()
        if ccd:
            subseries = SubseriesDoc.objects.filter(id_ccd=id_ccd)
            serializer = self.serializer_class(subseries, many=True)
            return Response({'success':True, 'detail':serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success':False, 'detail':'Debe consultar por un CCD válido'}, status=status.HTTP_404_NOT_FOUND)
        
class AsignarSeriesYSubseriesAUnidades(generics.UpdateAPIView):
    serializer_class = SeriesSubseriesUnidadOrgSerializer
    
    def put(self, request, id_ccd):
        id_ccd_ingresado = id_ccd
        datos_ingresados = request.data
        if datos_ingresados == []:
            series = SeriesDoc.objects.filter(id_ccd=id_ccd_ingresado).values()
            for i in series:
                instancia = SeriesSubseriesUnidadOrg.objects.filter(id_serie_doc=i['id_serie_doc'])
                instancia.delete()
            return Response({'success':False, "detail" : "Todas las relaciones de serires, subseries y unidades de esta CCD fueron borradas"}, status=status.HTTP_400_BAD_REQUEST)
        fecha_ccd = (CuadrosClasificacionDocumental.objects.filter(id_ccd=id_ccd_ingresado).values().first())
        if fecha_ccd:
            if fecha_ccd['fecha_terminado'] != None:
                return Response({'success':False, "detail" : "No se pueden realizar modificaciones sobre esta CCD, ya está terminado"}, status=status.HTTP_400_BAD_REQUEST)
        series = SeriesDoc.objects.filter(id_ccd=id_ccd_ingresado).values()
        # Validaciones antes de borrar
        series_id = set([i['id_serie_doc'] for i in datos_ingresados])
        filtrados = SeriesDoc.objects.filter(id_ccd=id_ccd_ingresado).filter(id_serie_doc__in=series_id).values()
        series_id_filtrados = set([i['id_serie_doc'] for i in filtrados])
        if len(series_id) != len(series_id_filtrados):
             return Response({'success':False, "detail" : "1. Ingresó una serie documental que no corresponde a la ccd sobre la que se está trabajando"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            pass
        # Guardar y actualizar asignaciones
        total_datos_guardados = []
        datos = []
        for i in datos_ingresados:
            if not isinstance(i['id_unidad_organizacional'], int):
                return Response({'success':False, "detail" : "Unidad organizacional debe ser un número entero"}, status=status.HTTP_400_BAD_REQUEST)
            if not isinstance(i['id_serie_doc'], int):
                return Response({'success':False, "detail" : "Debe ingresar una serie documental válida"}, status=status.HTTP_400_BAD_REQUEST)
            unidad_organizacional = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional=i['id_unidad_organizacional']).first()
            if unidad_organizacional == None:
                return Response({'success':False, "detail" : "No existe esa unidad organizacional"}, status=status.HTTP_400_BAD_REQUEST)
            serie = SeriesDoc.objects.filter(id_serie_doc=i['id_serie_doc']).first()
            if serie == None:
                return Response({'success':False, "detail" : "No existe esa serie documental"}, status=status.HTTP_400_BAD_REQUEST)
            if str(id_ccd_ingresado) != str((((SeriesDoc.objects.filter(id_serie_doc=i['id_serie_doc']).values())[0])['id_ccd_id'])):
                return Response({'success':False, "detail" : "Ingresó una serie documental que no corresponde a la ccd sobre la que se está trabajando"}, status=status.HTTP_400_BAD_REQUEST)
            subseries = i['subseries']
            if subseries == []:
                datos.append({"id_unidad_organizacional" : unidad_organizacional.id_unidad_organizacional, "id_serie_doc" : serie.id_serie_doc, "id_sub_serie_doc" : None})
            for i in subseries:
                if  (not (isinstance(i, int)) or (i == None)):
                    return Response({'success':False, "detail" : "Las subseries documentales deben ser un número entero", "data" : i}, status=status.HTTP_400_BAD_REQUEST)
                subserie = SubseriesDoc.objects.filter(id_subserie_doc=i).first()
                if not subserie:
                        return Response({'success':False, "detail" : "Una de las subseries documentales no existe", "data" : i}, status=status.HTTP_400_BAD_REQUEST)
                datos.append({"id_unidad_organizacional" : unidad_organizacional.id_unidad_organizacional, "id_serie_doc" : serie.id_serie_doc, "id_sub_serie_doc" : subserie.id_subserie_doc})
            # Borrar asignaciones
        for i in series:
            elmentos_a_borrar = SeriesSubseriesUnidadOrg.objects.filter(id_serie_doc=i['id_serie_doc'])
            elmentos_a_borrar.delete()         
        serializer = self.get_serializer(data=datos, many=isinstance(datos,list))
        serializer.is_valid(raise_exception=True)
        serializer.save()
        total_datos_guardados.append(serializer.data)

        return Response({'success':True, "detail" : "Datos guardados con éxito", "data" : total_datos_guardados}, status=status.HTTP_201_CREATED)
    
class GetAsignaciones(generics.ListAPIView):
    serializer_class = SeriesSubseriesUnidadOrgSerializer
    
    def get(self, request, id_ccd):
        dato_consultado = id_ccd
        if dato_consultado == None:
            return Response({'success' : False, "detail" : "Debe ingresar algún valor"}, status=status.HTTP_400_BAD_REQUEST)
        try: 
            int(dato_consultado)
            pass
        except:
            return Response({'success':False, "detail" : "El id de la ccd debe ser un número entero"}, status=status.HTTP_400_BAD_REQUEST)
        ccd = (CuadrosClasificacionDocumental.objects.filter(id_ccd=dato_consultado).values())
        if len(ccd) == 0:
            return Response({'success':False, "detail" : "Esta CCD no existe"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            ccd = ccd[0]
        series_doc = (SeriesDoc.objects.filter(id_ccd=ccd['id_ccd']).values())
        datos_salida = {"ccd" : ccd, "Subseries documentales" : series_doc}
        cont = 0
        cuentame = 0
        lista_serie_en_asignaciones = []
        nuevo=[]
        vector_aux = []
        for serie in series_doc:
            instancia_series_doc = (SeriesDoc.objects.filter(id_serie_doc=serie['id_serie_doc']).first())
            volatil = SeriesSubseriesUnidadOrg.objects.filter(id_serie_doc_id=instancia_series_doc.id_serie_doc).values()
            ordenados = sorted(volatil, key=lambda a : a['id_unidad_organizacional_id'])
            
            for i in ordenados:
                nuevo.append(i)
                if cont < (len(ordenados)-1):
                    cont = cont + 1
                
                aux = ordenados[cont]
                if i['id_unidad_organizacional_id'] != aux['id_unidad_organizacional_id']:
                    cuentame = cuentame + 1
                    vector_aux.append(nuevo)
                    nuevo = []

            if volatil:
                vector_aux.append(nuevo)
                contador = 0
                for i in vector_aux:
                    contador = contador + 1
                    ultimos = []
                    for iterable in i:
                        ultimos.append(iterable['id_sub_serie_doc_id'])
                    datos_salida = {"Unidad documental" + str(((i)[0])['id_unidad_organizacional_id']) : ((i)[0])['id_unidad_organizacional_id'], "Serie documental" + str(((i)[0])['id_serie_doc_id']) : ((i)[0])['id_serie_doc_id'], "Subseries" : ultimos}
                    lista_serie_en_asignaciones.append(datos_salida)
                
            vector_aux =[]
            nuevo = []    
            cont = 0
            
        return Response({'success':True, "detail": lista_serie_en_asignaciones}, status=status.HTTP_201_CREATED)

class ReanudarCuadroClasificacionDocumental(generics.UpdateAPIView):
    serializer_class = CCDActivarSerializer
    queryset = CuadrosClasificacionDocumental

    def put(self, request, pk):
        ccd = CuadrosClasificacionDocumental.objects.filter(id_ccd=pk).first()
        if ccd:
            if ccd.fecha_terminado:
                if ccd.fecha_retiro_produccion:
                    return Response({'success': False, 'detail': 'No se puede reanudar un cuadro de clasificación documental que ya fue retirado de producción'}, status=status.HTTP_403_FORBIDDEN)
                trd = TablaRetencionDocumental.objects.filter(id_ccd=pk).exists()
                if not trd:
                    ccd.fecha_terminado = None
                    ccd.save()
                    return Response({'success': True, 'detail': 'Se reanudó el CCD'}, status=status.HTTP_201_CREATED)
                else:
                    return Response({'success': False, 'detail': 'No puede reanudar el CCD porque se encuentra en un TRD'}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({'success': False, 'detail': 'No puede reanudar un CCD no terminado'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'success': False, 'detail': 'No se encontró ningún CCD con estos parámetros'}, status=status.HTTP_404_NOT_FOUND)    
