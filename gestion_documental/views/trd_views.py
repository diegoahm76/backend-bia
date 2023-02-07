from rest_framework import status
from django.db.models import Q
import copy
from datetime import datetime
from rest_framework import generics
from rest_framework.response import Response
from seguridad.utils import Util
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, permission_classes
from gestion_documental.serializers.trd_serializers import (
    TipologiasDocumentalesSerializer,
    TRDSerializer,
    TRDPostSerializer,
    TRDPutSerializer,
    TRDFinalizarSerializer,
    FormatosTiposMedioSerializer,
    FormatosTiposMedioPostSerializer,
    SeriesSubSeriesUnidadesOrgTRDSerializer,
    SeriesSubSeriesUnidadesOrgTRDPutSerializer,
    TipologiasDocumentalesPutSerializer,
    GetSeriesSubSUnidadOrgTRDSerializer
)
from gestion_documental.serializers.ccd_serializers import (
    CCDSerializer
)

from gestion_documental.models.ccd_models import (
    SeriesSubseriesUnidadOrg,
    CuadrosClasificacionDocumental,
    SeriesDoc
)
from almacen.models.organigrama_models import (
    Organigramas
)
from gestion_documental.models.trd_models import (
    TablaRetencionDocumental,
    TipologiasDocumentales,
    SeriesSubSUnidadOrgTRDTipologias,
    FormatosTiposMedio,
    SeriesSubSUnidadOrgTRD,
    FormatosTiposMedioTipoDoc,
    HistoricosSerieSubSeriesUnidadOrgTRD,
)

class UpdateTipologiasDocumentales(generics.UpdateAPIView):
    serializer_class = TipologiasDocumentalesPutSerializer
    queryset = TipologiasDocumentales.objects.all()
    permission_classes = [IsAuthenticated]

    def put(self, request, id_trd):
        data = request.data
        trd = TablaRetencionDocumental.objects.filter(id_trd=id_trd).first()
        confirm = request.query_params.get('confirm')
        usuario = request.user.id_usuario
        descripcion = {"nombre": str(trd.nombre), "version": str(trd.version)}
        direccion = Util.get_client_ip(request)
        if trd:
            if (not trd.fecha_terminado and not trd.fecha_retiro_produccion) or (trd.actual and trd.fecha_puesta_produccion and not trd.fecha_retiro_produccion):
                if data:
                    # VALIDAR QUE EL ID_TRD SEA EL MISMO
                    trd_list = [tipologia['id_trd'] for tipologia in data]
                    if len(set(trd_list)) != 1:
                        return Response({'success':False, 'detail':'Debe validar que las tipologias pertenezcan a un mismo TRD'}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        if trd_list[0] != int(id_trd):
                            return Response({'success':False, 'detail':'El id trd de la petición debe ser igual al enviado en url'}, status=status.HTTP_400_BAD_REQUEST)

                    # VALIDAR QUE LOS CODIGOS SEAN UNICOS
                    codigos_list = [tipologia['codigo'] for tipologia in data]
                    if len(codigos_list) != len(set(codigos_list)):
                        return Response({'success':False, 'detail':'Debe validar que los códigos de las tipologias sean únicos'}, status=status.HTTP_400_BAD_REQUEST)

                    # VALIDAR QUE LOS NOMBRES SEAN UNICOS
                    nombres_list = [tipologia['nombre'] for tipologia in data]
                    if len(nombres_list) != len(set(nombres_list)):
                        return Response({'success':False, 'detail':'Debe validar que los nombres de las tipologias sean únicos'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    # VALIDAR QUE LOS FORMATOS NO ESTÉN VACÍOS
                    formatos_list = [tipologia['formatos'] for tipologia in data]
                    formatos_empty = any(sublist == [] for sublist in formatos_list)
                    if formatos_empty:
                        return Response({'success':False, 'detail':'Debe asignar formatos para el tipo de medio de cada tipologia'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    # VALIDAR QUE LOS FORMATOS EXISTAN
                    formatos_actuales = FormatosTiposMedio.objects.filter(activo=True)
                    formatos_actuales_list = [formato.id_formato_tipo_medio for formato in formatos_actuales]
                    formatos_flat_list = set([item for sublist in formatos_list for item in sublist])
                    if not formatos_flat_list.issubset(formatos_actuales_list):
                        return Response({'success':False, 'detail':'Debe asignar formatos que existan'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    # VALIDAR QUE LOS FORMATOS PERTENEZCAN AL TIPO MEDIO INDICADO
                    for tipologia in data:
                        if tipologia['cod_tipo_medio_doc'] == 'E' or tipologia['cod_tipo_medio_doc'] == 'F':
                            formatos_actuales = FormatosTiposMedio.objects.filter(cod_tipo_medio_doc=tipologia['cod_tipo_medio_doc'])
                            formatos_actuales_list = [formato.id_formato_tipo_medio for formato in formatos_actuales]
                            if not set(tipologia['formatos']).issubset(formatos_actuales_list):
                                return Response({'success':False, 'detail':'Debe asignar formatos que correspondan al tipo medio elegido'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    # CREAR TIPOLOGIAS
                    valores_creados_detalles = []
                    
                    tipologias_create = list(filter(lambda tipologia: tipologia['id_tipologia_documental'] == None, data))
                    tipologias_id_create = []
                    if tipologias_create:
                        # CREAR RELACIONES CON FORMATOS
                        for tipologia in tipologias_create:
                            serializer = self.serializer_class(data=tipologia)
                            serializer.is_valid(raise_exception=True)
                            serializador = serializer.save()
                            tipologias_id_create.append(serializador.id_tipologia_documental)
                            for formato in tipologia['formatos']:
                                formato_instance = FormatosTiposMedio.objects.filter(id_formato_tipo_medio=formato).first()
                                FormatosTiposMedioTipoDoc.objects.create(
                                    id_tipologia_doc=serializador,
                                    id_formato_tipo_medio=formato_instance
                                )
                            valores_creados_detalles.append({'nombre':tipologia['nombre'], 'codigo':tipologia['codigo']})
                        
                        # CAMBIOS POR CONFIRMAR TRUE SI ES TRD ACTUAL
                        if trd.actual:
                            trd.cambios_por_confirmar = True
                            trd.save()

                    # ACTUALIZAR TIPOLOGIAS
                    valores_actualizados_detalles = []
                    
                    tipologias_update = list(filter(lambda tipologia: tipologia['id_tipologia_documental'] != None, data))
                    if tipologias_update:
                        for tipologia in tipologias_update:
                            tipologia_existe = TipologiasDocumentales.objects.filter(id_tipologia_documental=tipologia['id_tipologia_documental']).first()
                            previous_tipologia = copy.copy(tipologia_existe)
                            if tipologia_existe:
                                if tipologia_existe.cod_tipo_medio_doc != tipologia['cod_tipo_medio_doc']:
                                    formato_tipologia_existe = FormatosTiposMedioTipoDoc.objects.filter(id_tipologia_doc=tipologia['id_tipologia_documental'])
                                    formato_tipologia_existe.delete()
                                
                                if not trd.actual:    
                                    serializer = self.serializer_class(tipologia_existe, data=tipologia)
                                    serializer.is_valid(raise_exception=True)
                                    serializador = serializer.save()
                                
                                # ACTUALIZAR FORMATOS
                                for formato in tipologia['formatos']:
                                    formato_tipologia_existe = FormatosTiposMedioTipoDoc.objects.filter(id_tipologia_doc=tipologia['id_tipologia_documental'], id_formato_tipo_medio=formato)
                                    tipologia_actualizada = TipologiasDocumentales.objects.filter(id_tipologia_documental=tipologia['id_tipologia_documental']).first()
                                    if not formato_tipologia_existe:
                                        formato_instance = FormatosTiposMedio.objects.filter(id_formato_tipo_medio=formato).first()
                                        FormatosTiposMedioTipoDoc.objects.create(
                                            id_tipologia_doc=tipologia_actualizada,
                                            id_formato_tipo_medio=formato_instance
                                        )
                                    formato_tipologia_eliminar = FormatosTiposMedioTipoDoc.objects.filter(id_tipologia_doc=tipologia['id_tipologia_documental']).exclude(id_formato_tipo_medio__in=tipologia['formatos'])
                                    formato_tipologia_eliminar.delete()
                                
                                descripcion_tipologia = {'nombre':previous_tipologia.nombre, 'codigo':previous_tipologia.codigo}
                                valores_actualizados_detalles.append({'descripcion':descripcion_tipologia, 'previous':previous_tipologia, 'current':tipologia_existe})

                    # ELIMINAR TIPOLOGIAS
                    lista_tipologia_id = [tipologia['id_tipologia_documental'] for tipologia in tipologias_update]
                    lista_tipologia_id.extend(tipologias_id_create)
                    tipologias_eliminar = TipologiasDocumentales.objects.filter(id_trd=id_trd).exclude(id_tipologia_documental__in=lista_tipologia_id)
                    
                    if tipologias_eliminar and trd.actual:
                        return Response({'success':False, 'detail':'No puede eliminar tipologias para una TRD actual. Intente desactivar'}, status=status.HTTP_403_FORBIDDEN)
                    
                    # VALIDAR QUE NO SE ESTÉN USANDO LAS TIPOLOGIAS A ELIMINAR
                    tipologias_eliminar_id = [tipologia.id_tipologia_documental for tipologia in tipologias_eliminar]
                    serie_subserie_unidad_tipologia = SeriesSubSUnidadOrgTRDTipologias.objects.filter(id_tipologia_doc__in=tipologias_eliminar_id)
                    if serie_subserie_unidad_tipologia:
                        if confirm == 'true':
                            serie_subserie_unidad_tipologia.delete()
                        else:
                            return Response({'success':False, 'detail':'Una o varias tipologias a eliminar ya están asociadas al TRD', 'data':serie_subserie_unidad_tipologia.values()}, status=status.HTTP_403_FORBIDDEN)
                    
                    valores_eliminados_detalles = [{'nombre':tipologia.nombre, 'codigo':tipologia.codigo} for tipologia in tipologias_eliminar]
                    
                    tipologias_eliminar.delete()
                    
                    # AUDITORIA MAESTRO DETALLE
                    auditoria_data = {
                        "id_usuario" : usuario,
                        "id_modulo" : 29,
                        "cod_permiso": "AC",
                        "subsistema": 'GEST',
                        "dirip": direccion,
                        "descripcion": descripcion,
                        "valores_creados_detalles": valores_creados_detalles,
                        "valores_actualizados_detalles": valores_actualizados_detalles,
                        "valores_eliminados_detalles": valores_eliminados_detalles
                    }
                    Util.save_auditoria_maestro_detalle(auditoria_data)

                    return Response({'success':True, 'detail':'Se ha realizado cambios con las tipologias'}, status=status.HTTP_201_CREATED)
                else:
                    # VALIDAR QUE NO SE ESTÉN USANDO LAS TIPOLOGIAS A ELIMINAR
                    tipologias_eliminar = TipologiasDocumentales.objects.filter(id_trd=id_trd)
                    
                    if tipologias_eliminar and trd.actual:
                        return Response({'success':False, 'detail':'No puede eliminar tipologias para una TRD actual. Intente desactivar'})
                    
                    tipologias_eliminar_id = [tipologia.id_tipologia_documental for tipologia in tipologias_eliminar]
                    serie_subserie_unidad_tipologia = SeriesSubSUnidadOrgTRDTipologias.objects.filter(id_tipologia_doc__in=tipologias_eliminar_id)
                    if serie_subserie_unidad_tipologia:
                        if confirm == 'true':
                            serie_subserie_unidad_tipologia.delete()
                        else:
                            return Response({'success':False, 'detail':'Una o varias tipologias a eliminar ya están asociadas al TRD', 'data':serie_subserie_unidad_tipologia.values()}, status=status.HTTP_403_FORBIDDEN)

                    valores_eliminados_detalles = [{'nombre':tipologia.nombre, 'codigo':tipologia.codigo} for tipologia in tipologias_eliminar]
                    
                    tipologias_eliminar.delete()
                    
                    # AUDITORIA MAESTRO DETALLE
                    auditoria_data = {
                        "id_usuario" : usuario,
                        "id_modulo" : 29,
                        "cod_permiso": "AC",
                        "subsistema": 'GEST',
                        "dirip": direccion,
                        "descripcion": descripcion,
                        "valores_eliminados_detalles": valores_eliminados_detalles
                    }
                    Util.save_auditoria_maestro_detalle(auditoria_data)

                    return Response({'success':True, 'detail':'Se han eliminado todas las tipologias'}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'success':False, 'detail':'El TRD ya está terminado o fue retirado de producción, por lo cual no es posible realizar acciones sobre las tipologias'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'success':False, 'detail':'El TRD no existe'}, status=status.HTTP_404_NOT_FOUND)

class GetTipologiasDocumentales(generics.ListAPIView):
    serializer_class = TipologiasDocumentalesSerializer
    queryset = TipologiasDocumentales.objects.all()

    def get(self, request, id_trd):
        trd = TablaRetencionDocumental.objects.filter(id_trd=id_trd).first()
        if trd:
            tipologias = TipologiasDocumentales.objects.filter(id_trd=id_trd, activo=True).values()
            if not tipologias:
                return Response({'success':True, 'detail':'No se encontraron tipologías para el organigrama', 'data':tipologias}, status=status.HTTP_200_OK)
            for tipologia in tipologias:
                formatos_tipologias = FormatosTiposMedioTipoDoc.objects.filter(id_tipologia_doc=tipologia['id_tipologia_documental'])
                formatos_tipologias_list = [formato_tipologia.id_formato_tipo_medio.id_formato_tipo_medio for formato_tipologia in formatos_tipologias]
                formatos = FormatosTiposMedio.objects.filter(id_formato_tipo_medio__in=formatos_tipologias_list).values()
                tipologia['formatos'] = formatos
                
            return Response({'success':True, 'detail':'Se encontraron las siguientes tipologías para el organigrama', 'data':tipologias}, status=status.HTTP_200_OK)
        else:
            return Response({'success':False, 'detail':'Debe consultar por un TRD válido'}, status=status.HTTP_404_NOT_FOUND)


#Series SubSeries Unidades Organizacionales TRD
class CreateSerieSubSeriesUnidadesOrgTRD(generics.CreateAPIView):
    serializer_class = SeriesSubSeriesUnidadesOrgTRDSerializer
    queryset = SeriesSubSUnidadOrgTRD.objects.all()

    def post(self, request, id_trd):
        data_entrante = request.data
        trd = TablaRetencionDocumental.objects.filter(id_trd=id_trd).first()
        tipologias = request.data.get('tipologias')

        if trd:
            serializador = self.serializer_class(data=data_entrante, many=False)
            serializador.is_valid(raise_exception=True)

            id_trd_validated = serializador.validated_data.get('id_trd')
            id_serie_subserie_unidad = serializador.validated_data.get('id_serie_subserie_doc')
            cod_disposicion_final = serializador.validated_data.get('cod_disposicion_final')
            digitalizacion_dis_final = serializador.validated_data.get('digitalizacion_dis_final')
            tiempo_retencion_ag = serializador.validated_data.get('tiempo_retencion_ag')
            tiempo_retencion_ac = serializador.validated_data.get('tiempo_retencion_ac')
            descripcion_procedimiento = serializador.validated_data.get('descripcion_procedimiento')

            #VALIDACION DE NO ASIGNAR UNA SERIE SUBSERIE UNIDAD TRD A OTRA TRD
            if int(id_trd) != id_trd_validated.id_trd:
                return Response({'success': False, 'detail': 'El id_trd enviado debe ser el mismo que el ingresado en la url'}, status=status.HTTP_400_BAD_REQUEST)

            #VALIDACION ENVIO VACIO DE LA INFORMACION
            if not cod_disposicion_final and not digitalizacion_dis_final and not tiempo_retencion_ag and not tiempo_retencion_ac and not descripcion_procedimiento:
                serializador.save()
                return Response({'success': True, 'detail': 'Creación exitosa', 'data': serializador.data}, status=status.HTTP_201_CREATED)

            #VALIDACION ENVIO COMPLETO DE LA INFORMACION
            elif cod_disposicion_final and digitalizacion_dis_final and tiempo_retencion_ag and tiempo_retencion_ac and descripcion_procedimiento != None:
                tipologias_instance = TipologiasDocumentales.objects.filter(id_tipologia_documental__in=tipologias, id_trd=id_trd)
                if len(tipologias) != tipologias_instance.count():
                    return Response({'success': False, 'detail': 'Todas las tipologias seleccionadas deben existir y deben estar relacionadas a la TRD elegida'}, status=status.HTTP_400_BAD_REQUEST)

                #VALIDAR QUE SE ELIJA UNA SERIE SUBSERIE UNIDAD VALIDA, SEGÚN LA TRD ELEGIDA
                serie_subserie_unidad = []
                serie_subserie_unidad.append(id_serie_subserie_unidad.id_serie_subserie_doc)
                series_trd = list(SeriesDoc.objects.filter(id_ccd=trd.id_ccd))
                series_id = [serie.id_serie_doc for serie in series_trd]
                series_subseries_unidades_org_ccd = SeriesSubseriesUnidadOrg.objects.filter(id_serie_doc__in=series_id)
                series_subseries_unidades_org_ccd_id = [serie.id_serie_subserie_doc for serie in series_subseries_unidades_org_ccd]
                if not set(serie_subserie_unidad).issubset(set(series_subseries_unidades_org_ccd_id)):
                    return Response({'success': False, 'detail': 'Debe elegir una serie subserie unidad asociada al ccd que tiene la trd enviada en la url'}, status=status.HTTP_400_BAD_REQUEST)

                serializado = serializador.save()

                #CREACIÓN DE LA SERIE SUBSERIE UNIDAD TRD TIPOLOGIA
                for tipologia in tipologias_instance:
                    SeriesSubSUnidadOrgTRDTipologias.objects.create(
                        id_serie_subserie_unidadorg_trd = serializado,
                        id_tipologia_doc = tipologia
                    )
                return Response({'success': True, 'detail': 'Creación exitosa', 'data': serializador.data}, status=status.HTTP_201_CREATED)
            else:
                return Response({'success': False, 'detail': 'Debe enviar todas las especificaciones diligenciadas o todas las especificaciones vacias'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'success': False, 'detail': 'No existe ninguna Tabla de Retención Documental con el parámetro ingresado'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def uploadDocument(request, id_serie_subserie_uniorg_trd):
    ssuorg_trd = SeriesSubSUnidadOrgTRD.objects.filter(id_serie_subs_unidadorg_trd=id_serie_subserie_uniorg_trd).first()
    if ssuorg_trd:
        if ssuorg_trd.id_trd.actual:
            ssuorg_trd.ruta_archivo_cambio = request.FILES.get('document')
            ssuorg_trd.save()
            return Response({'success': True, 'detail': 'Documento cargado correctamente'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'success': False, 'detail': 'El documento solo debe ser subido cuando se realizan cambios a una trd actual'}, status=status.HTTP_403_FORBIDDEN)
    else:
        return Response({'success': False, 'detail': 'No se encontró ninguna ssuorg-trd con el parámetro ingresado'}, status=status.HTTP_404_NOT_FOUND)

    

class UpdateSerieSubSeriesUnidadesOrgTRD(generics.CreateAPIView):
    serializer_class = SeriesSubSeriesUnidadesOrgTRDPutSerializer
    queryset = SeriesSubSUnidadOrgTRD.objects.all()
    permission_classes = [IsAuthenticated]

    def put(self, request, id_serie_subs_unidadorg_trd):
        data_entrante = request.data
        persona_usuario_logeado = request.user.persona
        serie_subs_unidadorg_trd = SeriesSubSUnidadOrgTRD.objects.filter(id_serie_subs_unidadorg_trd=id_serie_subs_unidadorg_trd).first()
        tipologias = request.data.get('tipologias')
        previous_serie_subs_unidad_org_trd = copy.copy(serie_subs_unidadorg_trd)

        if serie_subs_unidadorg_trd:
            #SI LA TRD NO ES ACTUAL Y NO TIENE FECHA RETIRO PRODUCCIÓN ACTUALIZA SERIE SUBSERIE SIN HISTORICO
            if serie_subs_unidadorg_trd.id_trd.actual == False and serie_subs_unidadorg_trd.id_trd.fecha_retiro_produccion == None:
                serializador = self.serializer_class(serie_subs_unidadorg_trd, data=data_entrante, many=False)
                serializador.is_valid(raise_exception=True)

                cod_disposicion_final = serializador.validated_data.get('cod_disposicion_final')
                digitalizacion_dis_final = serializador.validated_data.get('digitalizacion_dis_final')
                tiempo_retencion_ag = serializador.validated_data.get('tiempo_retencion_ag')
                tiempo_retencion_ac = serializador.validated_data.get('tiempo_retencion_ac')
                descripcion_procedimiento = serializador.validated_data.get('descripcion_procedimiento')

                #SI ENVIAN TODAS LAS ESPECIFICACIONES VACIAS
                if not cod_disposicion_final and not digitalizacion_dis_final and not tiempo_retencion_ag and not tiempo_retencion_ac and not descripcion_procedimiento and not tipologias:
                    serializador.save()

                    #ELIMINA TODAS LAS TIPOLOGIAS ASOCIADAS A ESA SSU-TRD
                    series_unidades_tipologias = SeriesSubSUnidadOrgTRDTipologias.objects.filter(id_serie_subserie_unidadorg_trd=id_serie_subs_unidadorg_trd)
                    series_unidades_tipologias.delete()
                    return Response({'success': True, 'detail': 'Actualización exitosa', 'data': serializador.data}, status=status.HTTP_201_CREATED)

                #SI ENVIAN TODAS LAS ESPECIFICACIONES DILIGENCIADAS
                elif cod_disposicion_final and digitalizacion_dis_final and tiempo_retencion_ag and tiempo_retencion_ac and descripcion_procedimiento and tipologias:
                    tipologias_instance = TipologiasDocumentales.objects.filter(id_tipologia_documental__in=tipologias, id_trd=serie_subs_unidadorg_trd.id_trd.id_trd)

                    #VALIDACION SI ENVIAN TIPOLOGIAS QUE NO SON DE LA MISMA TRD O QUE NO EXISTEN
                    if len(tipologias) != tipologias_instance.count():
                        return Response({'success': False, 'detail': 'Todas las tipologias seleccionadas deben existir y deben estar relacionadas a la TRD elegida'}, status=status.HTTP_400_BAD_REQUEST)

                    #ELIMINA TODAS LAS TIPOLOGIAS QUE NO HAYA ENVIADO AL MOMENTO DE ACTUALIZAR
                    serie_subserie_unidad_tipologias = SeriesSubSUnidadOrgTRDTipologias.objects.filter(Q(id_serie_subserie_unidadorg_trd=id_serie_subs_unidadorg_trd) & ~Q(id_tipologia_doc__in=tipologias))
                    serie_subserie_unidad_tipologias.delete()

                    serializado = serializador.save()
                    
                    #VERIFICA QUE NO EXISTA EN SSUTRD-TIPOLOGIAS Y CREA LA CONEXIÓN
                    for tipologia in tipologias:
                        serie_tipologia_instance = SeriesSubSUnidadOrgTRDTipologias.objects.filter(id_serie_subserie_unidadorg_trd=id_serie_subs_unidadorg_trd, id_tipologia_doc=tipologia)
                        tipologia_instance_create = TipologiasDocumentales.objects.filter(id_tipologia_documental=tipologia).first()
                        if not serie_tipologia_instance:
                            SeriesSubSUnidadOrgTRDTipologias.objects.create(
                                id_serie_subserie_unidadorg_trd = serie_subs_unidadorg_trd,
                                id_tipologia_doc = tipologia_instance_create
                            )
                    return Response({'success': True, 'detail': 'Actualización exitosa', 'data': serializador.data}, status=status.HTTP_201_CREATED)

                else:
                    return Response({'success': False, 'detail': 'Debe enviar todas las especificaciones y tipologias diligenciadas o todas las especificaciones y tipologias vacias'}, status=status.HTTP_400_BAD_REQUEST)
            
            # SI LA TRD A MODIFICAR ES LA ACTUAL, GENERA HISTORICOS Y ASIGNA NUEVAS TIPOLOGIAS
            elif serie_subs_unidadorg_trd.id_trd.actual == True:
                serializador = self.serializer_class(serie_subs_unidadorg_trd, data=data_entrante, many=False)
                serializador.is_valid(raise_exception=True)

                cod_disposicion_final = serializador.validated_data.get('cod_disposicion_final')
                digitalizacion_dis_final = serializador.validated_data.get('digitalizacion_dis_final')
                tiempo_retencion_ag = serializador.validated_data.get('tiempo_retencion_ag')
                tiempo_retencion_ac = serializador.validated_data.get('tiempo_retencion_ac')
                descripcion_procedimiento = serializador.validated_data.get('descripcion_procedimiento')
                justificacion_cambio = serializador.validated_data.get('justificacion_cambio')

                #SI ENVIAN TODA LA INFORMACIÓN DILIGENCIADA
                if cod_disposicion_final and digitalizacion_dis_final == True or digitalizacion_dis_final == False and tiempo_retencion_ag and tiempo_retencion_ac and descripcion_procedimiento and justificacion_cambio:
                    tipologias_instance = TipologiasDocumentales.objects.filter(id_tipologia_documental__in=tipologias, id_trd=serie_subs_unidadorg_trd.id_trd.id_trd)
                    tipologias_instance_list = [tipologia.id_tipologia_documental for tipologia in tipologias_instance]
                    
                    #VALIDA QUE LAS TIPOLOGIAS SELECCIONADAS TENGAN LA MISMA TRD COMO PADRE
                    if tipologias and not tipologias_instance_list:
                        return Response({'success': False, 'detail': 'La tipologia seleccionada no hace parte de las disponibles'}, status=status.HTTP_400_BAD_REQUEST)
                    if not set(tipologias).issubset(set(tipologias_instance_list)):
                        return Response({'success': False, 'detail': 'Alguna de las tipologias seleccionadas no hacen parte de las disponibles'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    #VALIDA QUE LA TIPOLOGIA SELECCIONADA ESTÉ ACTIVA
                    for tipologia in tipologias_instance:
                        if tipologia.activo == False:
                            return Response({'success': False, 'detail': 'Todas las tipologias seleccionadas deben estar activas para poder asignarlas'}, status=status.HTTP_400_BAD_REQUEST)

                    #GUARDA LA INFORMACIÓN ENVIADA  
                    serializado = serializador.save()

                    #CREA LA CONEXIÓN EN LA TABLA SSUTRD-TIPOLOGIA SI NO EXISTE
                    for tipologia in tipologias_instance:
                        tipologia_existente = SeriesSubSUnidadOrgTRDTipologias.objects.filter(Q(id_serie_subserie_unidadorg_trd=serie_subs_unidadorg_trd.id_serie_subs_unidadorg_trd) & Q(id_tipologia_doc=tipologia.id_tipologia_documental)).first()
                        if not tipologia_existente:
                            SeriesSubSUnidadOrgTRDTipologias.objects.create(
                                id_serie_subserie_unidadorg_trd = serie_subs_unidadorg_trd,
                                id_tipologia_doc = tipologia
                            )

                    #CREA EL HISTORICO
                    HistoricosSerieSubSeriesUnidadOrgTRD.objects.create(
                        id_serie_subs_unidadorg_trd = previous_serie_subs_unidad_org_trd,
                        cod_disposicion_final = previous_serie_subs_unidad_org_trd.cod_disposicion_final,
                        digitalizacion_disp_final = previous_serie_subs_unidad_org_trd.digitalizacion_dis_final,
                        tiempo_retencion_ag = previous_serie_subs_unidad_org_trd.tiempo_retencion_ag,
                        tiempo_retencion_ac = previous_serie_subs_unidad_org_trd.tiempo_retencion_ac,
                        descripcion_procedimiento = previous_serie_subs_unidad_org_trd.descripcion_procedimiento,
                        justificacion = previous_serie_subs_unidad_org_trd.justificacion_cambio,
                        ruta_archivo = previous_serie_subs_unidad_org_trd.ruta_archivo_cambio,
                        id_persona_cambia = persona_usuario_logeado
                    )

                    return Response({'success': True, 'detail': 'Actualización exitosa de la TRD Actual', 'data': serializador.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response({'success': False, 'detail': 'Para modificar una trd actual se debe completar toda la información'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'success': False, 'detail': 'No existe ninguna Serie Subserie Unidad TRD con el parámetro ingresado'}, status=status.HTTP_404_NOT_FOUND)


class DeleteSerieSubserieUnidadTRD(generics.RetrieveDestroyAPIView):
    serializer_class = GetSeriesSubSUnidadOrgTRDSerializer
    queryset = SeriesSubSUnidadOrgTRD.objects.all()

    def delete(self, request, id_ssuorg_trd):
        serie_ss_uniorg_trd = SeriesSubSUnidadOrgTRD.objects.filter(id_serie_subs_unidadorg_trd=id_ssuorg_trd).first()
        if serie_ss_uniorg_trd:
            if serie_ss_uniorg_trd.id_trd.actual == True:
                return Response({'success': False, 'detail': 'No se pueden realizar acciones sobre las Series'}, status=status.HTTP_403_FORBIDDEN)
            serie_ss_uniorg_trd_tipologias = SeriesSubSUnidadOrgTRDTipologias.objects.filter(id_serie_subserie_unidadorg_trd=serie_ss_uniorg_trd)
            serie_ss_uniorg_trd_tipologias.delete()
            serie_ss_uniorg_trd.delete()
            return Response({'success': True, 'detail': 'Eliminado exitosamente'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'success': False, 'detail': 'No se encontró ninguna Serie Subserie Unidad TRD con el parámetro ingresado'}, status.HTTP_404_NOT_FOUND)



#Tabla de Retencion Documental

class GetTablaRetencionDocumental(generics.ListAPIView):
    serializer_class = TRDSerializer
    queryset = TablaRetencionDocumental.objects.all()

class GetTablaRetencionDocumentalTerminados(generics.ListAPIView):
    serializer_class = TRDSerializer
    queryset = TablaRetencionDocumental.objects.filter(~Q(fecha_terminado = None) & Q(fecha_retiro_produccion=None))

class PostTablaRetencionDocumental(generics.CreateAPIView):
    serializer_class = TRDPostSerializer
    queryset = TablaRetencionDocumental
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            pass
        except:
            return Response({'success': False, 'detail': 'Valide la información ingresada, el id_ccd es requerido, el nombre y la versión son requeridos y deben ser únicos'}, status=status.HTTP_400_BAD_REQUEST)

        #Validación de seleccionar solo ccd terminados
        ccd = serializer.validated_data.get('id_ccd')
        ccd_instance = CuadrosClasificacionDocumental.objects.filter(id_ccd=ccd.id_ccd).first()
        if ccd_instance:
            if ccd_instance.fecha_terminado == None:
                return Response({'success': False, 'detail': 'No se pueden seleccionar Cuadros de Clasificación Documental que no estén terminados'}, status=status.HTTP_403_FORBIDDEN)

            serializado = serializer.save()

            #Auditoria Crear Tabla de Retención Documental
            usuario = request.user.id_usuario
            descripcion = {"Nombre": str(serializado.nombre), "Versión": str(serializado.version)}
            direccion=Util.get_client_ip(request)
            auditoria_data = {
                "id_usuario" : usuario,
                "id_modulo" : 29,
                "cod_permiso": "CR",
                "subsistema": 'GEST',
                "dirip": direccion,
                "descripcion": descripcion,
            }
            Util.save_auditoria(auditoria_data)

            return Response({'success': True, 'detail': 'TRD creada exitosamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({'success': False, 'detail': 'No existe un Cuadro de Clasificación Documental con el id_ccd enviado'}, status=status.HTTP_400_BAD_REQUEST)

class UpdateTablaRetencionDocumental(generics.RetrieveUpdateAPIView):
    serializer_class = TRDPutSerializer
    queryset = TablaRetencionDocumental.objects.all()
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            trd = TablaRetencionDocumental.objects.get(id_trd=pk)
            previoud_trd = copy.copy(trd)
            pass
        except:
            return Response({'success': False, 'detail': 'No existe ninguna Tabla de Retención Documental con los parámetros ingresados'}, status=status.HTTP_404_NOT_FOUND)

        if trd.fecha_terminado:
            return Response({'success': False,'detail': 'No se puede actualizar una TRD terminada'}, status=status.HTTP_403_FORBIDDEN)

        serializer = self.serializer_class(trd, data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            pass
        except:
            return Response({'success': False, 'detail': 'Validar data enviada, el nombre y la versión son requeridos y deben ser únicos'}, status=status.HTTP_400_BAD_REQUEST)
        serializer.save()

        # AUDITORIA DE UPDATE DE CCD
        user_logeado = request.user.id_usuario
        dirip = Util.get_client_ip(request)
        descripcion = {'nombre':str(previoud_trd.nombre), 'version':str(previoud_trd.version)}
        valores_actualizados={'previous':previoud_trd, 'current':trd}
        auditoria_data = {
            'id_usuario': user_logeado,
            'id_modulo': 29,
            'cod_permiso': 'AC',
            'subsistema': 'GEST',
            'dirip': dirip,
            'descripcion': descripcion,
            'valores_actualizados': valores_actualizados
        }
        Util.save_auditoria(auditoria_data)

        return Response({'success': True, 'detail': 'Tabla de Retención Documental actualizado exitosamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)
    
class GetFormatosTiposMedioByParams(generics.ListAPIView):
    serializer_class = FormatosTiposMedioSerializer
    queryset = FormatosTiposMedio.objects.all()

    def get(self, request):
        cod_tipo_medio = request.query_params.get('cod-tipo-medio')
        nombre = request.query_params.get('nombre')

        if cod_tipo_medio == '':
            cod_tipo_medio = None
        if nombre == '':
            nombre = None

        if not cod_tipo_medio and not nombre:
            return Response({'success':False, 'detail':'Debe ingresar los parámetros de búsqueda'}, status=status.HTTP_404_NOT_FOUND)

        if cod_tipo_medio and nombre:
            formatos_tipos_medio = FormatosTiposMedio.objects.filter(cod_tipo_medio_doc=cod_tipo_medio, nombre__icontains=nombre, activo=True)
            serializador = self.serializer_class(formatos_tipos_medio, many=True)
            if formatos_tipos_medio:
                return Response({'success':True, 'detail':serializador.data}, status=status.HTTP_200_OK)
            else:
                return Response({'success':False, 'detail':'No se encontró ningún resultado'}, status=status.HTTP_404_NOT_FOUND)

        if cod_tipo_medio and not nombre:
            formatos_tipos_medio = FormatosTiposMedio.objects.filter(cod_tipo_medio_doc=cod_tipo_medio, activo=True)
            serializador = self.serializer_class(formatos_tipos_medio, many=True)
            if formatos_tipos_medio:
                return Response({'success':True, 'detail':serializador.data}, status=status.HTTP_200_OK)
            else:
                return Response({'success':False, 'detail':'No se encontró ningún resultado'}, status=status.HTTP_404_NOT_FOUND)

        if not cod_tipo_medio and nombre:
            formatos_tipos_medio = FormatosTiposMedio.objects.filter(nombre__icontains=nombre, activo=True)
            serializador = self.serializer_class(formatos_tipos_medio, many=True)
            if formatos_tipos_medio:
                return Response({'success':True, 'detail':serializador.data}, status=status.HTTP_200_OK)
            else:
                return Response({'success':False, 'detail':'No se encontró ningún resultado'}, status=status.HTTP_404_NOT_FOUND)

class GetFormatosTiposMedioByCodTipoMedio(generics.ListAPIView):
    serializer_class = FormatosTiposMedioSerializer
    queryset = FormatosTiposMedio.objects.all()

    def get(self, request, cod_tipo_medio_doc):
        if cod_tipo_medio_doc == 'H':
            formatos_tipos_medio = FormatosTiposMedio.objects.filter(activo=True)
        else:
            formatos_tipos_medio = FormatosTiposMedio.objects.filter(cod_tipo_medio_doc=cod_tipo_medio_doc, activo=True)

        serializador = self.serializer_class(formatos_tipos_medio, many=True)
        if serializador:
            return Response({'success':True, 'detail':'Se encontró la siguiente información', 'data':serializador.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success':False, 'detail':'No se encontró ningún resultado'}, status=status.HTTP_404_NOT_FOUND)

class RegisterFormatosTiposMedio(generics.CreateAPIView):
    serializer_class =  FormatosTiposMedioPostSerializer
    queryset = FormatosTiposMedio.objects.all()

    def post(self, request):
        data = request.data
        serializador = self.serializer_class(data=data)
        serializador.is_valid(raise_exception=True)
        serializador.save()
        return Response({'success':True, 'detail':'Se creado el Formato Tipo Medio'}, status=status.HTTP_201_CREATED)

class UpdateFormatosTiposMedio(generics.RetrieveUpdateAPIView):
    serializer_class = FormatosTiposMedioPostSerializer
    queryset = FormatosTiposMedio.objects.all()

    def put(self, request, pk):
        formato_tipo_medio = FormatosTiposMedio.objects.filter(id_formato_tipo_medio=pk).first()

        if formato_tipo_medio:
            if not formato_tipo_medio.registro_precargado:
                if formato_tipo_medio.item_ya_usado:
                    return Response({'success':False, 'detail':'Este formato tipo medio ya está siendo usado, por lo cual no es actualizable'}, status=status.HTTP_403_FORBIDDEN)

                serializer = self.serializer_class(formato_tipo_medio, data=request.data, many=False)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response({'success':True, 'detail':'Registro actualizado exitosamente'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'success': False, 'detail': 'No puede actualizar un formato tipo medio precargado'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'success': False, 'detail': 'No existe el formato tipo medio'}, status=status.HTTP_404_NOT_FOUND)

class DeleteFormatosTiposMedio(generics.DestroyAPIView):
    serializer_class = FormatosTiposMedioPostSerializer
    queryset = FormatosTiposMedio.objects.all()

    def delete(self, request, pk):
        formato_tipo_medio = FormatosTiposMedio.objects.filter(id_formato_tipo_medio=pk).first()
        if formato_tipo_medio:
            pass
            if not formato_tipo_medio.registro_precargado:
                if formato_tipo_medio.item_ya_usado:
                    return Response({'success':False, 'detail':'Este formato tipo medio ya está siendo usado, no se pudo eliminar'}, status=status.HTTP_403_FORBIDDEN)

                formato_tipo_medio.delete()
                return Response({'success': True, 'detail': 'Este formato tipo medio ha sido eliminado exitosamente'}, status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({'success': False, 'detail': 'No puedes eliminar un formato tipo medio precargado'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'success': False, 'detail':'No existe el formato tipo medio'}, status=status.HTTP_404_NOT_FOUND)

class CambiosPorConfirmar(generics.UpdateAPIView):
    serializer_class = SeriesSubSeriesUnidadesOrgTRDPutSerializer
    queryset = SeriesSubSUnidadOrgTRDTipologias.objects.all()

    def put(self, request, id_trd):
        confirm = request.query_params.get('confirm')
        trd = TablaRetencionDocumental.objects.filter(id_trd=id_trd).first()
        if trd:
            if trd.actual:
                if trd.cambios_por_confirmar:
                    series_sub_unidades_trd = SeriesSubSUnidadOrgTRD.objects.filter(id_trd=id_trd)
                    series_sub_unidades_trd_list = [serie_sub_unidad_trd.id_serie_subs_unidadorg_trd for serie_sub_unidad_trd in series_sub_unidades_trd]
                    formatos_tipo_medio = SeriesSubSUnidadOrgTRDTipologias.objects.filter(id_serie_subserie_unidadorg_trd__in=series_sub_unidades_trd_list)
                    tipologias_list = [formato_tipo_medio.id_tipologia_doc.id_tipologia_documental for formato_tipo_medio in formatos_tipo_medio]
                    tipologias_trd = TipologiasDocumentales.objects.filter(id_trd=id_trd)
                    tipologias_trd_list = [tipologia.id_tipologia_documental for tipologia in tipologias_trd]

                    if not set(tipologias_trd_list).issubset(tipologias_list):
                        tipologias_faltan = TipologiasDocumentales.objects.filter(id_trd=id_trd).exclude(id_tipologia_documental__in=tipologias_list)
                        if confirm == 'true':
                            tipologias_faltan.delete()
                            trd.cambios_por_confirmar = False
                            trd.save()
                            return Response({'success': True, 'detail': 'Se han eliminado las tipologias no usadas y se confirmaron cambios'}, status=status.HTTP_200_OK)
                        else:
                            return Response({'success': False, 'detail': 'Tiene tipologias pendientes por usar', 'data':tipologias_faltan.values()}, status=status.HTTP_403_FORBIDDEN)
                    else:
                        trd.cambios_por_confirmar = False
                        trd.save()
                        return Response({'success': True, 'detail': 'Está usando todas las tipologias, se han confirmado cambios'}, status=status.HTTP_200_OK)
                else:
                    return Response({'success': False, 'detail': 'No tiene cambios por confirmar'}, status=status.HTTP_403_FORBIDDEN)
            else:
                return Response({'success':False, 'detail':'No puede realizar esta acción porque no es el TRD actual'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'success':False, 'detail':'El TRD no existe'}, status=status.HTTP_404_NOT_FOUND)

class GetSeriesSubSUnidadOrgTRD(generics.ListAPIView):
    serializer_class = GetSeriesSubSUnidadOrgTRDSerializer
    queryset = SeriesSubSUnidadOrgTRD.objects.all()
    
    def get(self, request, pk):
        id_trd_a_consultar1 = pk
        series_subseries_unidad_org_trd = SeriesSubSUnidadOrgTRD.objects.filter(id_trd = id_trd_a_consultar1).values()
        if not series_subseries_unidad_org_trd:
            return Response({'success': False, 'detail': 'No se encontró la TRD'}, status=status.HTTP_403_FORBIDDEN)
        
        ids_serie_subs_unidad_org_trd = [i['id_serie_subs_unidadorg_trd'] for i in series_subseries_unidad_org_trd]
        #print(ids_serie_subs_unidad_org_trd)
        result = []
        for i in ids_serie_subs_unidad_org_trd:
            main_detail = SeriesSubSUnidadOrgTRDTipologias.objects.filter(id_serie_subserie_unidadorg_trd = i).values().first()
            detalle_serie_subs_unidad_org_trd = SeriesSubSUnidadOrgTRD.objects.filter(id_serie_subs_unidadorg_trd = main_detail['id_serie_subserie_unidadorg_trd_id']).values().first()
            detalle_tipologias = TipologiasDocumentales.objects.filter(id_tipologia_documental = main_detail['id_tipologia_doc_id']).values().first()
            main_detail['id_serie_subserie_unidadorg_trd_id'] = detalle_serie_subs_unidad_org_trd
            main_detail['id_tipologia_doc_id'] = detalle_tipologias
            result.append(main_detail)
            
            
        return Response({'success': True, 'Tabla': result}, status=status.HTTP_204_NO_CONTENT)

class GetSeriesSubSUnidadOrgTRDByPk(generics.ListAPIView):
    serializer_class = GetSeriesSubSUnidadOrgTRDSerializer
    queryset = SeriesSubSUnidadOrgTRD.objects.all()
    
    def get(self, request, pk):
        pk_a_consultar1 = pk
        serie_subseries_unidad_org = SeriesSubSUnidadOrgTRD.objects.filter(id_serie_subs_unidadorg_trd = pk_a_consultar1).values()
        if not serie_subseries_unidad_org:
            return Response({'success': False, 'detail': 'No se encontró información relacionada a ese id'}, status=status.HTTP_403_FORBIDDEN)
        
        ids_serie_subs_unidad_org_trd = [i['id_serie_subs_unidadorg_trd'] for i in serie_subseries_unidad_org]
        #print(ids_serie_subs_unidad_org_trd)
        result = []
        for i in ids_serie_subs_unidad_org_trd:
            main_detail = SeriesSubSUnidadOrgTRDTipologias.objects.filter(id_serie_subserie_unidadorg_trd = i).values().first()
            detalle_serie_subs_unidad_org_trd = SeriesSubSUnidadOrgTRD.objects.filter(id_serie_subs_unidadorg_trd = main_detail['id_serie_subserie_unidadorg_trd_id']).values().first()
            detalle_tipologias = TipologiasDocumentales.objects.filter(id_tipologia_documental = main_detail['id_tipologia_doc_id']).values().first()
            main_detail['id_serie_subserie_unidadorg_trd_id'] = detalle_serie_subs_unidad_org_trd
            main_detail['id_tipologia_doc_id'] = detalle_tipologias
            result.append(main_detail)
            
            
        return Response({'success': True, 'Tabla': result}, status=status.HTTP_204_NO_CONTENT)

class DesactivarTipologiaActual(generics.UpdateAPIView):
    serializer_class = TipologiasDocumentalesPutSerializer
    queryset = TipologiasDocumentales.objects.all()
    permission_classes = [IsAuthenticated]

    def put(self, request, id_tipologia):
        persona = request.user.persona
        tipologia = TipologiasDocumentales.objects.filter(id_tipologia_documental=id_tipologia).first()
        justificacion = request.data.get('justificacion_desactivacion')
        if tipologia:
            trd = TablaRetencionDocumental.objects.filter(id_trd=tipologia.id_trd.id_trd).first()
            if trd.actual:
                if not tipologia.activo:
                    return Response({'success':False, 'detail':'La tipologia ya se encuentra desactivada'}, status=status.HTTP_403_FORBIDDEN)
                if not justificacion:
                    return Response({'success':False, 'detail':'Debe ingresar la justificación para desactivar la tipología'}, status=status.HTTP_400_BAD_REQUEST)
                
                tipologia.activo = False
                tipologia.fecha_desactivacion = datetime.now()
                tipologia.justificacion_desactivacion = justificacion
                tipologia.id_persona_desactiva = persona
                tipologia.save()
                return Response({'success': True, 'detail': 'Se ha desactivado la tipologia indicada'}, status=status.HTTP_200_OK)
            else:
                return Response({'success':False, 'detail':'No puede realizar esta acción porque no es el TRD actual'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'success':False, 'detail':'La tipologia ingresada no existe'}, status=status.HTTP_404_NOT_FOUND)

class finalizarTRD(generics.RetrieveUpdateAPIView):
    serializer_class = TRDFinalizarSerializer
    queryset = TablaRetencionDocumental.objects.all()
    
    def put(self, request, pk):
        trd_ingresada = pk
        confirm = request.query_params.get("confirm")
        trd = TablaRetencionDocumental.objects.filter(id_trd = trd_ingresada).first()
        series = SeriesDoc.objects.filter(id_ccd = trd.id_ccd).values()
        id_series_totales = [i['id_serie_doc'] for i in series]
        series_subseries_unidades_totales = SeriesSubseriesUnidadOrg.objects.filter(id_serie_doc__in = id_series_totales).values()
        id_series_subseries_unidades_totales = [i['id_serie_subserie_doc'] for i in series_subseries_unidades_totales]
        series_subseries_unidades_usadas = SeriesSubSUnidadOrgTRD.objects.filter(id_trd = trd_ingresada).values()
        id_series_subseries_unidades_usadas = [i['id_serie_subserie_doc_id'] for i in series_subseries_unidades_usadas]
        id_series_subseries_unidades_no_usadas = [i for i in id_series_subseries_unidades_totales if i not in id_series_subseries_unidades_usadas]
        if len(id_series_subseries_unidades_no_usadas) >= 1:
            instancia_id_series_subseries_unidades_no_usadas = SeriesSubseriesUnidadOrg.objects.filter(id_serie_subserie_doc__in = id_series_subseries_unidades_no_usadas).values()
            return Response({'success': False, 'detail': 'Hay combinaciones de series, subseries y unidades que no se están usando', 'Combinaciones no usadas' : instancia_id_series_subseries_unidades_no_usadas}, status=status.HTTP_403_FORBIDDEN)
        if trd.fecha_terminado == None:
            series_subseries_unidad_org_trd = SeriesSubSUnidadOrgTRD.objects.filter(id_trd = trd_ingresada).values()
            for i in series_subseries_unidad_org_trd:
                if i['cod_disposicion_final'] != None and i['digitalizacion_dis_final'] != None and i['tiempo_retencion_ag'] != None and i['tiempo_retencion_ac'] != None:
                    consulta = SeriesSubSUnidadOrgTRDTipologias.objects.filter(id_serie_subserie_unidadorg_trd = i['id_serie_subs_unidadorg_trd']).first()
                    if not consulta:
                        return Response({'success': False, 'detail': 'La relación ' + str(i['id_serie_subs_unidadorg_trd']) +  ' debe tener una tipología asignada'}, status=status.HTTP_403_FORBIDDEN)    
            ids_series_subseries_unidad_org_trd = [i['id_serie_subs_unidadorg_trd'] for i in series_subseries_unidad_org_trd]
            series_subseries_unidad_org_trd_tipologias = SeriesSubSUnidadOrgTRDTipologias.objects.filter(id_serie_subserie_unidadorg_trd__in = ids_series_subseries_unidad_org_trd).values()
            id_tipologias_usadas = [i['id_tipologia_doc_id'] for i in series_subseries_unidad_org_trd_tipologias]
            tipologias_sin_usar_instance = TipologiasDocumentales.objects.filter(~Q(id_tipologia_documental__in = id_tipologias_usadas))
            if confirm == 'true':
                tipologias_sin_usar_instance.delete()
            if (tipologias_sin_usar_instance.values()):
                return Response({'success': False, 'detail': 'Hay tipologias documentales sin usar', 'Tipologías sin usar' : tipologias_sin_usar_instance.values()}, status=status.HTTP_403_FORBIDDEN)
            trd.fecha_terminado = datetime.now()
            trd.save()
        else:
            return Response({'success': False, 'detail': 'Esta TRD ya está finalizada'}, status=status.HTTP_403_FORBIDDEN)
        return Response({'success': True, 'detail': 'TRD finalizada con éxito'}, status=status.HTTP_200_OK)
        
        
        
        
        
         
