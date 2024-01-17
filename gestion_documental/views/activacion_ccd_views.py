from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, PermissionDenied
from gestion_documental.models.tca_models import TablasControlAcceso
from gestion_documental.models.trd_models import TablaRetencionDocumental
from gestion_documental.models.ccd_models import CuadrosClasificacionDocumental, UnidadesSeccionResponsableTemporal
from transversal.models.organigrama_models import Organigramas, UnidadesOrganizacionales
from gestion_documental.serializers.activacion_ccd_serializers import (
    CCDSerializer, 
    CCDPosiblesSerializer, 
    TRDSerializer, 
    TCASerializer,
    CtrlAccesoClasificacionExpCCDSerializer,
    PermisosUndsOrgActualesSerieExpCCDSerializer,
    ConfiguracionTipoExpedienteAgnoSerializer,
    ConsecPorNivelesTipologiasDocAgnoSerializer,
)
from seguridad.utils import Util

from django.db import transaction
from datetime import datetime
import copy

from gestion_documental.models import (
    CuadrosClasificacionDocumental,
    UnidadesSeccionResponsableTemporal,
    UnidadesSeccionPersistenteTemporal,
    AgrupacionesDocumentalesPersistenteTemporal,
    TablasControlAcceso,
    TablaRetencionDocumental,
    ExpedientesDocumentales, 
    DocumentosDeArchivoExpediente,
    PermisosUndsOrgActualesSerieExpCCD,
    ConfiguracionTipoExpedienteAgno,
    ConfigTipologiasDocAgno,
    ConsecPorNivelesTipologiasDocAgno,
    
)

from gestion_documental.views.ctrl_acceso_views import CtrlAccesoClasificacionExpCCD



# TODO: Realizar consulta en la tabla T225UndsSeccionPersisten_Tmp
# TODO: Realizar consultas en las tablas T224CatSeries_UndOrg_CCD, T225UndsSeccionPersisten_Tmp y T226AgrupacionesDocPersisten_Tmp
# TODO: Validar que se haya realizado la homologación de secciones
# TODO: Mostrar mensaje al usuario indicando que debe diligenciar el módulo "1. Homologación de Secciones Persistentes del CCD"
# TODO: Deseleccionar el CCD elegido por el usuario

# TODO: Validar agrupaciones documentales persistentes
# TODO: Mostrar mensaje al usuario indicando las unidades y agrupaciones documentales que deberían ser persistentes
# TODO: Deseleccionar el CCD elegido por el usuario

# TODO: Continuar con el proceso de Activación del CCD
# TODO: Resto del código de activación del CCD


class CCDActualGetView(generics.ListAPIView):
    serializer_class = CCDSerializer
    permission_classes = [IsAuthenticated]

    def get_ccd_actual(self):
        ccd_actual = CuadrosClasificacionDocumental.objects.filter(actual=True).first()
        return ccd_actual
    
    def get(self, request):
        ccd_actual = self.get_ccd_actual()

        if not ccd_actual:
            raise NotFound('No existe un CCD actual')
        
        serializer = self.serializer_class(ccd_actual)
        
        return Response({'success':True, 'detail':'CCD Actual', 'data': serializer.data}, status=status.HTTP_200_OK)


class GetCCDPosiblesActivar(generics.ListAPIView):
    serializer_class = CCDPosiblesSerializer
    permission_classes = [IsAuthenticated]

    def get_ccd_posibles_activar(self, id_organigrama):

        ccd = CuadrosClasificacionDocumental.objects.filter(fecha_retiro_produccion=None, actual=False).exclude(fecha_terminado=None)

        try:
            organigrama = Organigramas.objects.get(id_organigrama=id_organigrama)
        except Organigramas.DoesNotExist:
            raise NotFound('El organigrama ingresado no existe')
        
        if organigrama.fecha_terminado == None or organigrama.fecha_retiro_produccion != None:
            raise PermissionDenied('El organigrama ingresado ya está retirado o no está terminado')
        
        ccd_posibles_activar = ccd.filter(id_organigrama=organigrama.id_organigrama).select_related('tablaretenciondocumental__tablascontrolacceso')
        ccd_posibles = [ccd for ccd in ccd_posibles_activar if ccd.tablaretenciondocumental.tablascontrolacceso is not None]
        
        return ccd_posibles

    def get(self, request):
        id_organigrama_in = request.query_params.get('id_organigrama')
        id_organigrama = id_organigrama_in if id_organigrama_in else Organigramas.objects.filter(actual=True).first().id_organigrama
        ccd_posibles = self.get_ccd_posibles_activar(id_organigrama)
        serializer = self.serializer_class(ccd_posibles, many=True)

        return Response({'success':True, 'detail':'Los CCD posibles que se pueden activar son los siguientes', 'data': serializer.data}, status=status.HTTP_200_OK)
    
class TCACambioActualPut(generics.UpdateAPIView):
    serializer_class = TCASerializer
    permission_classes = [IsAuthenticated]

    def activar_tca(self, tca_seleccionado, data_desactivar, data_activar, data_auditoria):

        previous_activacion_tca = copy.copy(tca_seleccionado)
        tca_actual = TablasControlAcceso.objects.filter(actual=True).first()

        if tca_actual:

            previous_desactivacion_tca = copy.copy(tca_actual)
            serializer = self.serializer_class(tca_actual, data=data_desactivar)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            # Auditoria TCA desactivado
            descripcion = {"NombreTCA":str(tca_actual.nombre),"VersionTCA":str(tca_actual.version)}
            valores_actualizados={'previous':previous_desactivacion_tca, 'current':tca_actual}
            data_auditoria['descripcion'] = descripcion
            data_auditoria['valores_actualizados'] = valores_actualizados
            Util.save_auditoria(data_auditoria)

        serializer = self.serializer_class(tca_seleccionado, data=data_activar)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Auditoria TCA activado
        descripcion = {"NombreTCA":str(tca_seleccionado.nombre),"VersionTCA":str(tca_seleccionado.version)}
        valores_actualizados={'previous':previous_activacion_tca, 'current':tca_seleccionado}
        data_auditoria['descripcion'] = descripcion
        data_auditoria['valores_actualizados'] = valores_actualizados
        Util.save_auditoria(data_auditoria)

        return Response({'success':True, 'detail':'Tabla de control de acceso activado'}, status=status.HTTP_200_OK)

class TRDCambioActualPut(generics.UpdateAPIView):
    serializer_class = TRDSerializer
    permission_classes = [IsAuthenticated]

    def activar_trd(self, trd_seleccionado, data_desactivar, data_activar, data_auditoria):

        previous_activacion_trd = copy.copy(trd_seleccionado)
        trd_actual = TablaRetencionDocumental.objects.filter(actual=True).first()

        if trd_actual:
    
            previous_desactivacion_trd = copy.copy(trd_actual)
            serializer = self.serializer_class(trd_actual, data=data_desactivar)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            # Auditoria TRD desactivado
            descripcion = {"NombreTRD":str(trd_actual.nombre),"VersionTRD":str(trd_actual.version)}
            valores_actualizados={'previous':previous_desactivacion_trd, 'current':trd_actual}
            data_auditoria['descripcion'] = descripcion
            data_auditoria['valores_actualizados'] = valores_actualizados
            Util.save_auditoria(data_auditoria)

        serializer = self.serializer_class(trd_seleccionado, data=data_activar)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        tca_seleccionado = TablasControlAcceso.objects.filter(id_trd=trd_seleccionado.id_trd).first()
        instancia_tca = TCACambioActualPut()
        response_tca = instancia_tca.activar_tca(tca_seleccionado, data_desactivar, data_activar, data_auditoria)

        if response_tca.status_code != status.HTTP_200_OK:
            return response_tca

        # Auditoria TRD activado
        descripcion = {"NombreTRD":str(trd_seleccionado.nombre),"VersionTRD":str(trd_seleccionado.version)}
        valores_actualizados={'previous':previous_activacion_trd, 'current':trd_seleccionado}
        data_auditoria['descripcion'] = descripcion
        data_auditoria['valores_actualizados'] = valores_actualizados
        Util.save_auditoria(data_auditoria)

        return Response({'success':True, 'detail':'Tabla de retencion documental activado'}, status=status.HTTP_200_OK)
        

@transaction.atomic
class CCDCambioActualPut(generics.UpdateAPIView):
    serializer_class = CCDSerializer
    permission_classes = [IsAuthenticated]

    def activar_ccd(self, ccd_seleccionado, id_organigrama, data_desactivar, data_activar, data_auditoria):

        try:
            organigrama_actual = Organigramas.objects.get(id_organigrama=id_organigrama, actual=True)
        except Organigramas.DoesNotExist:
            raise NotFound('El organigrama ingresado no existe o no está activo')
        
        if organigrama_actual.id_organigrama != ccd_seleccionado.id_organigrama:
            raise PermissionDenied('El CCD seleccionado no pertenece al organigrama ingresado')
        
        previous_activacion_ccd = copy.copy(ccd_seleccionado)
        ccd_actual = CuadrosClasificacionDocumental.objects.filter(actual=True).first()

        if ccd_actual:
    
            previous_desactivacion_ccd = copy.copy(ccd_actual)
            serializer = self.serializer_class(ccd_actual, data=data_desactivar)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            # Auditoria CCD desactivado
            descripcion = {"NombreCCD":str(ccd_actual.nombre),"VersionCCD":str(ccd_actual.version)}
            valores_actualizados={'previous':previous_desactivacion_ccd, 'current':ccd_actual}
            data_auditoria['descripcion'] = descripcion
            data_auditoria['valores_actualizados'] = valores_actualizados
            Util.save_auditoria(data_auditoria)

        serializer = self.serializer_class(ccd_seleccionado, data=data_activar)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        del data_activar['justificacion_nueva_version']

        trd_seleccionado = TablaRetencionDocumental.objects.filter(id_ccd=ccd_seleccionado.id_ccd).first()
        instancia_trd = TRDCambioActualPut()
        response_trd = instancia_trd.activar_trd(trd_seleccionado, data_desactivar, data_activar, data_auditoria)

        if response_trd.status_code != status.HTTP_200_OK:
            return response_trd

        # Auditoria CCD activado
        descripcion = {"NombreCCD":str(ccd_seleccionado.nombre),"VersionCCD":str(ccd_seleccionado.version)}
        valores_actualizados={'previous':previous_activacion_ccd, 'current':ccd_seleccionado}
        data_auditoria['descripcion'] = descripcion
        data_auditoria['valores_actualizados'] = valores_actualizados
        Util.save_auditoria(data_auditoria)

        return Response({'success':True, 'detail':'Cuadro de clasificacion docuemntal activado'}, status=status.HTTP_200_OK)


    def put(self, request):
        data = request.data
        ccd_actual = CuadrosClasificacionDocumental.objects.filter(actual=True).first()

        organigrama_actual = Organigramas.objects.filter(actual=True).first()
        if not organigrama_actual:
            raise NotFound('No existe un organigrama actual')
        
        data_auditoria = {
            'id_usuario': request.user.id_usuario,
            'id_modulo': 28,
            'cod_permiso': 'AC',
            'subsistema': 'GEST',
            'dirip': Util.get_client_ip(request)
        }
        
        data_desactivar = {
            'actual': False,
            'fecha_retiro_produccion': datetime.now()
            }
        
        data_activar = {
            'actual': True,
            'fecha_puesta_produccion': datetime.now(),
            'justificacion_nueva_version': data['justificacion']
            }
        
        try:
            ccd_seleccionado = CuadrosClasificacionDocumental.objects.get(id_ccd=data['id_ccd'])
        except CuadrosClasificacionDocumental.DoesNotExist:
            raise NotFound("El CCD seleccionado no existe")
        
        if (ccd_seleccionado.fecha_terminado == None) or (ccd_seleccionado.fecha_puesta_produccion != None):
            raise PermissionDenied("El CCD seleccionado no esta terminado o ya está puesto en producción")
        
        if not ccd_actual:
            response_ccd = self.activar_ccd(ccd_seleccionado, organigrama_actual.id_organigrama, data_desactivar, data_activar, data_auditoria)

        else:
            if ccd_actual.id_ccd == ccd_seleccionado.id_ccd:
                raise PermissionDenied("El CCD seleccionado ya está activo")
            
            instancia_subproceso_1 = ActCCDActualizarControlAcceso()
            instancia_subproceso_2 = ActCCDActualizarControlAccesoAgrupaciones()
            instancia_subproceso_3 = ActCCDActualizarPermisosUnidades()
            instancia_subproceso_4 = ActCCDActualizarConsecutivosActOrgView()

            response_subproceso_1 = instancia_subproceso_1.actualizar_control_acceso(ccd_seleccionado.id_ccd, data_auditoria)
            response_subproceso_2 = instancia_subproceso_2.actualizar_control_acceso_agrupaciones(ccd_seleccionado.id_ccd, data_auditoria)
            response_subproceso_3 = instancia_subproceso_3.actualizar_permisos_unidad_agrupaciones(ccd_seleccionado.id_ccd, data_auditoria)
            response_subproceso_4 = instancia_subproceso_4.actualizar_consecutivos(ccd_seleccionado.id_ccd, data_auditoria)

            response_ccd = self.activar_ccd(ccd_seleccionado, organigrama_actual.id_organigrama, data_desactivar, data_activar, data_auditoria)

            if response_subproceso_1.status_code != status.HTTP_200_OK:
                return response_subproceso_1
            if response_subproceso_2.status_code != status.HTTP_200_OK:
                return response_subproceso_2
            if response_subproceso_3.status_code != status.HTTP_200_OK:
                return response_subproceso_3
            if response_subproceso_4.status_code != status.HTTP_200_OK:
                return response_subproceso_4
            
        if response_ccd.status_code != status.HTTP_200_OK:
            return response_ccd

        return Response({'success':True, 'detail':'Cuadro de clasificacion docuemntal activado'}, status=status.HTTP_200_OK)
    

class ValidacionAgrupacionesPersistentes(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def validacion_agrupacion(self, request):
        ccd_actual = CuadrosClasificacionDocumental.objects.filter(actual=True).first()
        unidades_persistentes = UnidadesSeccionPersistenteTemporal.objects.filter(id_ccd_nuevo=ccd_actual.id_ccd)
        id_unidades_persistentes = [unidad.id_unidad_seccion_temporal for unidad in unidades_persistentes]
        agrupaciones_persistentes = AgrupacionesDocumentalesPersistenteTemporal.objects.filter(id_unidad_seccion_temporal__in=id_unidades_persistentes)
        data_complete = []

        for agrupacion in agrupaciones_persistentes:
            data_complete.append({
                'id_agrupacion': agrupacion.id_agrupacion_doc_persistente_temporal,
                'id_unidad': agrupacion.id_unidad_seccion_temporal,
                'id_cat_serie_unidad_ccd_actual': agrupacion.id_cat_serie_unidad_ccd_actual.id_cat_serie_und,
                'id_cat_serie_unidad_ccd_nueva': agrupacion.id_cat_serie_unidad_ccd_nueva.id_cat_serie_und,
                'nombre_agrupacion': agrupacion.nombre_agrupacion,
                'nombre_serie': agrupacion.id_cat_serie_unidad_ccd_actual.id_cat_serie_und.nombre,
                'nombre_unidad': agrupacion.id_unidad_seccion_temporal.nombre
            })

        return Response({'success':True, 'detail':'Agrupaciones persistentes', 'data': data_complete}, status=status.HTTP_200_OK)

# TODO: Subproceso 1: Activar CCD
#   - Crear registros de CONTROL DE ACCESO para las clasificaciones de PUBLICO, CLASIFICADO y RESERVADO del CCD que se está ACTIVANDO
#   - Consultar registros en la tabla T222CtrlAcceso_ClasificacionExp_CCD donde T222Id_CCD sea igual al ID del CCD que se está DESACTIVANDO y T222Id_CatSerie_UndOrg_CCD sea NULL
# TODO: Para cada registro encontrado, realizar un INSERT en la misma tabla T222 cambiando T222ID_CCD por el ID del CCD que se está ACTIVANDO
#   - Insertar en la tabla T222 replicando los mismos valores, excepto la PK, cambiando T222ID_CCD por el ID del CCD que se está ACTIVANDO
# TODO: Crear un registro de auditoría con la información especificada
#   - Insertar un nuevo registro de auditoría con TzId_Usuario, TzId_Modulo, TzSubsistema, TzCod_PermisoAccion, TzfechaAccion, TzdirIp y Tzdescripcion

class ActCCDActualizarControlAcceso(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CtrlAccesoClasificacionExpCCDSerializer

    def actualizar_control_acceso(self, id_ccd_nuevo, data_auditoria):
        ccd_actual = CuadrosClasificacionDocumental.objects.get(actual=True)
        control_acceso = CtrlAccesoClasificacionExpCCD.objects.filter(id_ccd=ccd_actual.id_ccd, id_cat_serie_und_org_ccd=None)

        datos_control_acceso = self.serializer_class(control_acceso, many=True).data

        for dato in datos_control_acceso:
            dato['id_ccd'] = id_ccd_nuevo
            del dato['id_ctrl_acceso_clasif_exp_ccd']

        serializer = self.serializer_class(data=datos_control_acceso, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'success':True, 'detail':'Control de Acceso generado'}, status=status.HTTP_200_OK)

        # # Auditoria Actualizar Permisos Unidades 
                    
        # descripcion = {"NombreOrganigrama":str(organigrama_actual.nombre),"VersionOrganigrama":str(organigrama_actual.version)}
        # valores_actualizados={'previous':"previous_activacion_organigrama", 'current':"organigrama_seleccionado"}
        # data_auditoria['descripcion'] = descripcion
        # data_auditoria['valores_actualizados'] = valores_actualizados
        # Util.save_auditoria(data_auditoria)




# TODO: Subproceso 2: Activar CCD
#   - Crear registros de CONTROL DE ACCESO para las EXCLUSIONES de AGRUPACIONES DOCUMENTALES del CCD que se está ACTIVANDO
#   - Consultar registros en la tabla T222CtrlAcceso_ClasificacionExp_CCD donde T222Id_CCD sea el del CCD que se está DESACTIVANDO y T222Cod_ClasificacionExp sea NULL

# TODO: Para cada registro de exclusión encontrado, buscar si aparece en la tabla de agrupaciones PERSISTENTES del CCD que se está ACTIVANDO
#   - Consultar registros en las tablas T225UndsSeccionPersisten_Tmp (maestro) y T226AgrupacionesDocPersisten_Tmp (detalle) usando inner join

# TODO: Para cada registro hallado en el paso anterior, insertar la exclusión en la tabla T222CtrlAcceso_ClasificacionExp_CCD para el CCD que se está ACTIVANDO
#   - Insertar registros en la tabla T222 replicando los valores, excepto la PK, cambiando T222ID_CCD por el ID del CCD que se está ACTIVANDO y T222Id_CatSerie_UndOrg_CCD por el ID de la unidad organizacional persistente nueva

# TODO: Crear un registro de auditoría con la información especificada
#   - Insertar un nuevo registro de auditoría con TzId_Usuario, TzId_Modulo, TzSubsistema, TzCod_PermisoAccion, TzfechaAccion, TzdirIp y Tzdescripcion

class ActCCDActualizarControlAccesoAgrupaciones(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CtrlAccesoClasificacionExpCCDSerializer

    def actualizar_control_acceso_agrupaciones(self, id_ccd_nuevo, data_auditoria):
        ccd_actual = CuadrosClasificacionDocumental.objects.get(actual=True)
        control_accesos = CtrlAccesoClasificacionExpCCD.objects.filter(id_ccd=ccd_actual.id_ccd, cod_clasificacion_exp=None)
        unidades_peristentes = UnidadesSeccionPersistenteTemporal.objects.filter(id_ccd_nuevo=id_ccd_nuevo)
        id_unidades_peristentes = [unidad.id_unidad_seccion_temporal for unidad in unidades_peristentes]
        agrupaciones_persistentes = AgrupacionesDocumentalesPersistenteTemporal.objects.filter(id_unidad_seccion_temporal__in=id_unidades_peristentes)
        data_complete = []

        for control in control_accesos:
            dato = self.serializer_class(control).data
            for agrupacion in agrupaciones_persistentes:
                if control.id_cat_serie_und_org_ccd.id_cat_serie_und == agrupacion.id_cat_serie_unidad_ccd_actual.id_cat_serie_und:
                    dato['id_ccd'] = id_ccd_nuevo
                    dato['id_cat_serie_und_org_ccd'] = agrupacion.id_cat_serie_unidad_ccd_nueva.id_cat_serie_und
                    del dato['id_ctrl_acceso_clasif_exp_ccd']
                    data_complete.append(dato)

        serializer = self.serializer_class(data=data_complete, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'success':True, 'detail':'Control de Acceso agrupaciones generado'}, status=status.HTTP_200_OK)

# TODO: Subproceso 3: Activar CCD
# TODO: Buscar las Series de Agrupaciones Documentales Persistentes del CCD Nuevo
#   - Consultar registros en las tablas T225UndsSeccionPersisten_Tmp (maestro) y T226AgrupacionesDocPersisten_Tmp (detalle) donde T225IdUndSeccionPersiste_Tmp = T226Id_UndSeccionPersiste_Tmp y T225Id_CCDNuevo = IdCCD a ACTIVAR

# TODO: Para cada registro encontrado, buscar los registros en la tabla T221Permisos_UndsOrgActuales_SerieExped_CCD
#   - Consultar registros en la tabla T221Permisos_UndsOrgActuales_SerieExped_CCD donde T221Id_CatSerie_UndOrg_CCD = T226Id_CatSerie_UndOrg_CCDActual (campo hallado en el párrafo b)

# TODO: Realizar un INSERT en la tabla T221Permisos_UndsOrgActuales_SerieExped_CCD para el CCD que se está ACTIVANDO basado en los registros encontrados
#   - Para cada registro encontrado en el segundo paso:
#     - Insertar un nuevo registro en la tabla T221Permisos_UndsOrgActuales_SerieExped_CCD replicando todos los valores, excepto la PK y el campo T221Id_CatSerie_UndOrg_CCD, el cual se debe cambiar por el valor del campo T226Id_CatSerie_UndOrg_CCDNueva (hallado en el párrafo b)

# TODO: Crear un registro de auditoría con la información especificada
#   - Insertar un nuevo registro de auditoría con TzId_Usuario, TzId_Modulo, TzSubsistema, TzCod_PermisoAccion, TzfechaAccion, TzdirIp y Tzdescripcion

    
class ActCCDActualizarPermisosUnidades(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PermisosUndsOrgActualesSerieExpCCDSerializer

    def actualizar_permisos_unidad_agrupaciones(self, id_ccd_nuevo, data_auditoria):
        permisos_serie = PermisosUndsOrgActualesSerieExpCCD.objects.all()
        unidades_peristentes = UnidadesSeccionPersistenteTemporal.objects.filter(id_ccd_nuevo=id_ccd_nuevo)
        id_unidades_peristentes = [unidad.id_unidad_seccion_temporal for unidad in unidades_peristentes]
        agrupaciones_persistentes = AgrupacionesDocumentalesPersistenteTemporal.objects.filter(id_unidad_seccion_temporal__in=id_unidades_peristentes)
        data_complete = []

        for permiso in permisos_serie:
            dato = self.serializer_class(permiso).data
            for agrupacion in agrupaciones_persistentes:
                if permiso.id_cat_serie_und_org_ccd.id_cat_serie_und == agrupacion.id_cat_serie_unidad_ccd_actual.id_cat_serie_und:
                    dato['id_cat_serie_und_org_ccd'] = agrupacion.id_cat_serie_unidad_ccd_nueva.id_cat_serie_und
                    del dato['id_permisos_und_org_actual_serie_exp_ccd']
                    data_complete.append(dato)

        serializer = self.serializer_class(data=data_complete, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'success':True, 'detail':'Permisos unidad serie Actualizado'}, status=status.HTTP_200_OK)

        # # Auditoria Actualizar Permisos Unidades 
                    
        # descripcion = {"NombreOrganigrama":str(organigrama_actual.nombre),"VersionOrganigrama":str(organigrama_actual.version)}
        # valores_actualizados={'previous':"previous_activacion_organigrama", 'current':"organigrama_seleccionado"}
        # data_auditoria['descripcion'] = descripcion
        # data_auditoria['valores_actualizados'] = valores_actualizados
        # Util.save_auditoria(data_auditoria)

# TODO: Subproceso 4: Activar CCD
# TODO: Buscar las Series de Agrupaciones Documentales Persistentes del CCD Nuevo
#   - Consultar registros en las tablas T225UndsSeccionPersisten_Tmp (maestro) y T226AgrupacionesDocPersisten_Tmp (detalle) donde T225IdUndSeccionPersiste_Tmp = T226Id_UndSeccionPersiste_Tmp y T225Id_CCDNuevo = IdCCD a ACTIVAR

# TODO: Para cada registro encontrado, buscar los registros en la tabla T245ConfigTiposExpedienteAgno
#   - Consultar registros en la tabla T245ConfigTiposExpedienteAgno donde T245Id_CatSerie_UndOrg_CCD = T226Id_CatSerie_UndOrg_CCDActual (campo hallado en el párrafo b) y T245AgnoExpediente = (al año actual o al año inmediatamente posterior al actual: actual+1)

# TODO: Realizar un INSERT en la tabla T245ConfigTiposExpedienteAgno para el CCD que se está ACTIVANDO basado en los registros encontrados
#   - Para cada registro encontrado en el segundo paso:
#     - Insertar un nuevo registro en la tabla T245ConfigTiposExpedienteAgno replicando todos los valores, excepto la PK y el campo T245Id_CatSerie_UndOrg_CCD, el cual se debe cambiar por el valor del campo T226Id_CatSerie_UndOrg_CCDNueva (hallado en el párrafo b)

# TODO: Crear un registro de auditoría con la información especificada
#   - Insertar un nuevo registro de auditoría con TzId_Usuario, TzId_Modulo, TzSubsistema, TzCod_PermisoAccion, TzfechaAccion, TzdirIp y Tzdescripcion

# TODO: Borrar todos los registros existentes en las tablas temporales T225UndsSeccionPersisten_TMP, T226AgrupacionesDocPersisten_TMP y T227UndsSeccionResponsables_TMP

class ActCCDActualizarConsecutivosActOrgView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ConfiguracionTipoExpedienteAgnoSerializer

    def actualizar_consecutivos(self, id_ccd_nuevo, data_auditoria):
        unidades_peristentes = UnidadesSeccionPersistenteTemporal.objects.filter(id_ccd_nuevo=id_ccd_nuevo)
        id_unidades_peristentes = [unidad.id_unidad_seccion_temporal for unidad in unidades_peristentes]
        agrupaciones_persistentes = AgrupacionesDocumentalesPersistenteTemporal.objects.filter(id_unidad_seccion_temporal__in=id_unidades_peristentes)
        current_year = datetime.now().year
        configuraciones_expedientes = ConfiguracionTipoExpedienteAgno.objects.filter(agno_expediente__in=[current_year, current_year + 1])

        data_complete = []

        for configuracion in configuraciones_expedientes:
            dato = self.serializer_class(configuracion).data
            for agrupacion in agrupaciones_persistentes:
                if configuracion.id_cat_serie_undorg_ccd.id_cat_serie_und == agrupacion.id_cat_serie_unidad_ccd_actual.id_cat_serie_und:
                    dato['id_cat_serie_und_org_ccd'] = agrupacion.id_cat_serie_unidad_ccd_nueva.id_cat_serie_und
                    del dato['id_config_tipo_expediente_agno']
                    data_complete.append(dato)

        serializer = self.serializer_class(data=data_complete, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({'success':True, 'detail':'Permisos unidad serie Actualizado'}, status=status.HTTP_200_OK)

        # # Auditoria Actualizar Permisos Unidades 
                    
        # descripcion = {"NombreOrganigrama":str(organigrama_actual.nombre),"VersionOrganigrama":str(organigrama_actual.version)}
        # valores_actualizados={'previous':"previous_activacion_organigrama", 'current':"organigrama_seleccionado"}
        # data_auditoria['descripcion'] = descripcion
        # data_auditoria['valores_actualizados'] = valores_actualizados
        # Util.save_auditoria(data_auditoria)