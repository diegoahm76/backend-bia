from rest_framework import status, generics, views
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied

from django.db.models import Q, F
from datetime import datetime
from django.db import transaction
import copy

from transversal.models.organigrama_models import (
    Organigramas,
    UnidadesOrganizacionales,
    NivelesOrganigrama,
    TemporalPersonasUnidad
    )

from seguridad.models import User
from seguridad.utils import Util
from transversal.models.personas_models import Personas
from gestion_documental.models.ccd_models import CuadrosClasificacionDocumental, UnidadesSeccionResponsableTemporal
from gestion_documental.models.tca_models import TablasControlAcceso
from gestion_documental.models.trd_models import TablaRetencionDocumental
from gestion_documental.views.ccd_views import BusquedaCCDHomologacionView

from gestion_documental.views.activacion_ccd_views import CCDCambioActualPut


from transversal.serializers.activacion_organigrama_serializers import (
    OrganigramaCambioActualSerializer,
    UnidadesOrganizacionalesSerializer
)

from transversal.serializers.activacion_organigrama_serializers import (
    OrganigramaSerializer,
    UnidadesDelegacionSerializer
    
)


class OrganigramaActualGetView(generics.ListAPIView):
    serializer_class = OrganigramaSerializer
    permission_classes = [IsAuthenticated]

    def get_organigrama_actual(self):
        organigrama_actual = Organigramas.objects.filter(actual=True).first()
        return organigrama_actual
    
    def get (self,request):
        organigrama_actual = self.get_organigrama_actual()

        if not organigrama_actual:
            return Response({'success':True,'detail':'Busqueda exitosa, no existe organigrama actual'},status=status.HTTP_200_OK)
        
        serializer = self.serializer_class(organigrama_actual)
        return Response({'success':True, 'detail':'Organigrama Actual', 'data': serializer.data}, status=status.HTTP_200_OK)
    

class OrganigramasPosiblesGetListView(generics.ListAPIView):
    serializer_class = OrganigramaSerializer
    permission_classes = [IsAuthenticated]

    def get_organigramas_posibles(self):
        organigramas_posibles = Organigramas.objects.filter(actual=False, fecha_retiro_produccion=None).exclude(fecha_terminado=None)
        return organigramas_posibles
    
    def get (self,request):
        organigramas_posibles = self.get_organigramas_posibles()
        serializer = self.serializer_class(organigramas_posibles, many=True)
        return Response({'success':True, 'detail':'Los organigramas posibles para activar son los siguientes', 'data': serializer.data}, status=status.HTTP_200_OK)


@transaction.atomic
class OrganigramaCambioActualPutView(generics.UpdateAPIView):
    serializer_class = OrganigramaCambioActualSerializer
    permission_classes = [IsAuthenticated]

    def activar_organigrama(self, organigrama_seleccionado, data_desactivar, data_activar, data_auditoria):

        previous_activacion_organigrama = copy.copy(organigrama_seleccionado)
        organigrama_actual = Organigramas.objects.filter(actual=True).first()
        
        if organigrama_actual:
            temporal_all = TemporalPersonasUnidad.objects.all()
            previous_desactivacion_organigrama = copy.copy(organigrama_actual)
            serializer = self.serializer_class(organigrama_actual, data=data_desactivar)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            if temporal_all:
                organigrama_anterior = list(temporal_all.values_list('id_unidad_org_anterior__id_organigrama__id_organigrama', flat=True).distinct())
                organigrama_nuevo = list(temporal_all.values_list('id_unidad_org_nueva__id_organigrama__id_organigrama', flat=True).distinct())
                id_organigrama_anterior = organigrama_anterior[0] 

                if (organigrama_seleccionado.id_organigrama not in organigrama_nuevo) or (organigrama_actual.id_organigrama != id_organigrama_anterior):
                    temporal_all.delete()

            # Auditoria Organigrama desactivado
            descripcion = {"NombreOrganigrama":str(organigrama_actual.nombre),"VersionOrganigrama":str(organigrama_actual.version)}
            valores_actualizados={'previous':previous_desactivacion_organigrama, 'current':organigrama_actual}
            data_auditoria['descripcion'] = descripcion
            data_auditoria['valores_actualizados'] = valores_actualizados
            Util.save_auditoria(data_auditoria)

        serializer = self.serializer_class(organigrama_seleccionado, data=data_activar)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Auditoria Organigrama activado
        descripcion = {"NombreOrganigrama":str(organigrama_seleccionado.nombre),"VersionOrganigrama":str(organigrama_seleccionado.version)}
        valores_actualizados={'previous':previous_activacion_organigrama, 'current':organigrama_seleccionado}
        data_auditoria['descripcion'] = descripcion
        data_auditoria['valores_actualizados'] = valores_actualizados
        Util.save_auditoria(data_auditoria)

        return Response({'success':True, 'detail':'Organigrama Activado'}, status=status.HTTP_200_OK)


    def put(self, request):
        data = request.data
        ccd_actual = CuadrosClasificacionDocumental.objects.filter(actual=True).first()
        response_org = None
        
        data_auditoria = {
            'id_usuario': request.user.id_usuario,
            'id_modulo': 16,
            'cod_permiso': 'AC',
            'subsistema': 'TRSV',
            'dirip': Util.get_client_ip(request)
        }
        
        data_desactivar = {
            'actual': False,
            'fecha_retiro_produccion': datetime.now()
            }
        
        data_activar = {
            'actual': True,
            'fecha_puesta_produccion': datetime.now()
            }
        
        try:
            organigrama_seleccionado = Organigramas.objects.get(id_organigrama=data['id_organigrama'])
        except Organigramas.DoesNotExist:
            raise NotFound("El organigrama seleccionado no existe")
        
        if not ccd_actual:

            data_activar['justificacion_nueva_version'] = data['justificacion']
            response_org = self.activar_organigrama(organigrama_seleccionado, data_desactivar, data_activar, data_auditoria)
        
        else:
            if not data.get('id_ccd'):
                raise ValidationError('Debe seleccionar un CCD')
            
            try:
                ccd_seleccionado = CuadrosClasificacionDocumental.objects.get(id_ccd=data['id_ccd'], id_organigrama=organigrama_seleccionado.id_organigrama)
            except CuadrosClasificacionDocumental.DoesNotExist:
                raise NotFound("El CCD seleccionado no existe")
            
            if ccd_seleccionado.fecha_terminado == None or ccd_seleccionado.fecha_retiro_produccion != None:
                raise ValidationError('El CCD seleccionado no se encuentra terminado o ha sido retirado de producción')
            
            instancia_validacion = ValidacionUnidadesDelegacionActualView()
            validar_delegacion = instancia_validacion.validar_delegacion(ccd_seleccionado)

            if validar_delegacion == []:

                data_activar['justificacion_nueva_version'] = data['justificacion']
                response_org = self.activar_organigrama(organigrama_seleccionado, data_desactivar, data_activar, data_auditoria)

                # Activar CCD
                data_activar_ccd = data_activar
                data_activar_ccd['justificacion_nueva_version'] = "ACTIVACIÓN AUTOMÁTICA DESDE EL PROCESO DE 'CAMBIO DE ORGANIGRAMA ACTUAL'"
                ccd_activar = CCDCambioActualPut()
                response_ccd = ccd_activar.activar_ccd(ccd_seleccionado, organigrama_seleccionado.id_organigrama, data_desactivar, data_activar, data_auditoria)

                if response_ccd.status_code != status.HTTP_200_OK:
                    return response_ccd
            
            else:
                return Response({'success':False, 'detail':'Existen Unidades Organizacionales del CCD Actual sin delegación de responsable en el CCD a Activar', 'data':validar_delegacion}, status=status.HTTP_403_FORBIDDEN)
                
        if response_org.status_code != status.HTTP_200_OK:
            return response_org

        return Response({'success':True, 'detail':'Organigrama Activado'}, status=status.HTTP_200_OK)
    


# TODO: Realizar las siguientes validaciones al ingresar al módulo de Activación del Organigrama:
# 1. Validar que no exista ninguna unidad organizacional del CCD ACTUAL sin delegación de responsable en el CCD NUEVO.
#    - Realizar consultas en las tablas T019UnidadesOrganizacionales y T227UndsSeccionResponsables_Tmp.
#    - Mostrar un mensaje de error detallando las unidades organizacionales sin delegación.
# 2. Verificar la correcta identificación de las Agrupaciones Documentales persistentes del CCD ACTUAL en el CCD NUEVO.
#    - Revisar la identificación en las tablas T224CatSeries_UndOrg_CCD, T225UndsSeccionPersisten_Tmp y T226AgrupacionesDocPersisten_Tmp.
#    - Generar un mensaje de error indicando las Agrupaciones Documentales no identificadas correctamente.
    
class ValidacionUnidadesDelegacionActualView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UnidadesDelegacionSerializer

    def validar_delegacion(self, id_ccd_nuevo):
        ccd_filro = BusquedaCCDHomologacionView().get_validacion_ccd()

        try:
            ccd_nuevo = ccd_filro.get(id_ccd=id_ccd_nuevo)
        except CuadrosClasificacionDocumental.DoesNotExist:
            raise NotFound('CCD no encontrado o no cumple con TRD y TCA terminados')
        
        try:
            ccd_actual = CuadrosClasificacionDocumental.objects.get(actual=True)
        except CuadrosClasificacionDocumental.DoesNotExist:
            raise NotFound('CCD no se encuentra como actual')

        unidades_responsables = UnidadesSeccionResponsableTemporal.objects.filter(id_ccd_nuevo=ccd_nuevo.id_ccd)
        ids_unidad_ccd_actual = [unidad.id_unidad_seccion_actual.id_unidad_organizacional for unidad in unidades_responsables]        
        
        unidades_organizacionales_actual = UnidadesOrganizacionales.objects.filter(id_organigrama=ccd_actual.id_organigrama.id_organigrama).exclude(id_unidad_organizacional__in=ids_unidad_ccd_actual)
        
        serializer = self.serializer_class(unidades_organizacionales_actual, many=True)

        return serializer.data

# TODO: Mostrar mensajes de error y deseleccionar el CCD elegido si las validaciones anteriores no se cumplen.
# - Mensaje de error si hay Agrupaciones Documentales persistentes no identificadas correctamente.

# TODO: Combinar las consultas de unidades activas del organigrama actual y sus registros de delegación en una sola instrucción de base de datos.

# TODO: Ejecutar los siguientes subprocesos adicionales después de las validaciones y procesos actuales de Activación de Organigrama.

# TODO: Subproceso 1 - Cambiar unidades organizacionales del tipo sección o subsección que administran Agrupaciones Documentales.
# - Consultar la tabla temporal T227UndsSeccionResponsables_Tmp para obtener las asignaciones de unidades entre el CCD DESACTIVANDO y el CCD ACTIVANDO.
# - Actualizar la tabla T019UnidadesOrganizacionales de acuerdo con la información obtenida de T227.
# - Agregar comentarios detallados para cada subproceso adicional que se deba realizar después de las validaciones y procesos actuales.
    
class ActualizarUnidadesSeccionResponsable(views.APIView):
    permission_classes = [IsAuthenticated]
    
    def actualizar_agrupacion_documental(self, id_ccd_nuevo, data_auditoria):
        unidades_responsables = UnidadesSeccionResponsableTemporal.objects.filter(id_ccd_nuevo=id_ccd_nuevo, id_unidad_seccion_actual_padre=F('id_unidad_seccion_actual'))
        unidades = UnidadesOrganizacionales.objects.filter(id_unidad_org_actual_admin_series__in=[unidad.id_unidad_seccion_actual.id_unidad_organizacional for unidad in unidades_responsables])

        for unidad in unidades:
            for unidad_responsable in unidades_responsables:
                if unidad.id_unidad_org_actual_admin_series == unidad_responsable.id_unidad_seccion_actual:
                    unidad.id_unidad_org_actual_admin_series = unidad_responsable.id_unidad_seccion_nueva
                    unidad.save()
        
        
        # # Auditoria Actualizar Unidades Seccion Responsable
        # descripcion = {"NombreOrganigrama":str(organigrama_actual.nombre),"VersionOrganigrama":str(organigrama_actual.version)}
        # valores_actualizados={'previous':"previous_activacion_organigrama", 'current':"organigrama_seleccionado"}
        # data_auditoria['descripcion'] = descripcion
        # data_auditoria['valores_actualizados'] = valores_actualizados
        # Util.save_auditoria(data_auditoria)

# TODO: Subproceso 2 - Cambiar unidades organizacionales responsables de expedientes y documentos en todo el sistema.
# - Consultar la tabla temporal T227UndsSeccionResponsables_Tmp para obtener las asignaciones de unidades entre el CCD DESACTIVANDO y el CCD ACTIVANDO.
# - Actualizar la tabla T236ExpedientesDocumentales y T237DocumentosDeArchivo_Expediente según las asignaciones obtenidas.
                    
class ActualizarExpedientesDocumentos(views.APIView):
    permission_classes = [IsAuthenticated]
    
    def actualizar_expedientes_documentos(self, id_ccd_nuevo, data_auditoria):
        unidades_responsables = UnidadesSeccionResponsableTemporal.objects.filter(id_ccd_nuevo=id_ccd_nuevo, id_unidad_seccion_actual_padre=F('id_unidad_seccion_actual'))
        unidades = UnidadesOrganizacionales.objects.filter(id_unidad_org_actual_admin_series__in=[unidad.id_unidad_seccion_actual.id_unidad_organizacional for unidad in unidades_responsables])

# TODO: Subproceso 3 - Cambiar unidades organizacionales con permisos sobre Agrupaciones Documentales en todos los CCD
# - Consultar la tabla temporal T227UndsSeccionResponsables_Tmp para obtener las asignaciones de unidades entre el CCD DESACTIVANDO y el CCD ACTIVANDO.
# - Actualizar la tabla T221Permisos_UndsOrgActuales_SerieExped_CCD según las asignaciones obtenidas.

# TODO: Subproceso 4 - Cambiar unidades organizacionales en la configuración de ALERTAS EXISTENTES en el sistema.
# - Consultar la tabla temporal T227UndsSeccionResponsables_Tmp para obtener las asignaciones de unidades entre el CCD DESACTIVANDO y el CCD ACTIVANDO.
# - Actualizar la tabla T042PersonasAAlertar_ClaseAlerta y T043AlertasProgramadas según las asignaciones obtenidas.

# TODO: Subproceso 5 - Crear registros de CONTROL DE ACCESO para las clasificaciones del CCD que se está ACTIVANDO.
# - Consultar la tabla T222CtrlAcceso_ClasificacionExp_CCD para obtener los registros correspondientes al CCD DESACTIVANDO.
# - Insertar nuevos registros en la tabla T222CtrlAcceso_ClasificacionExp_CCD para el CCD ACTIVANDO, utilizando la información obtenida en la consulta.

# TODO: Subproceso 6 - Crear registros de CONTROL DE ACCESO para las exclusiones de Agrupaciones Documentales del CCD que se está ACTIVANDO.
# - Consultar la tabla T222CtrlAcceso_ClasificacionExp_CCD para obtener los registros correspondientes al CCD DESACTIVANDO y con exclusiones de Agrupaciones Documentales.
# - Para cada registro hallado, verificar si la Agrupación Documental está marcada como PERSISTENTE en el CCD ACTUAL.
# - Realizar las consultas necesarias para determinar las Agrupaciones Documentales PERSISTENTES en el CCD NUEVO.
# - Insertar nuevos registros en la tabla T222CtrlAcceso_ClasificacionExp_CCD para el CCD ACTIVANDO, utilizando la información obtenida en las consultas.

# TODO: Subproceso 7 - Crear registros de PERMISOS de las unidades organizacionales nuevas sobre las SERIES DE AGRUPACIONES DOCUMENTALES persistentes del CCD NUEVO.
# - Consultar las Series de Agrupaciones Documentales PERSISTENTES en el CCD NUEVO (tabla T226AgrupacionesDocPersisten_Tmp).
# - Para cada Serie de Agrupación Documental PERSISTENTE encontrada, buscar los registros de permisos correspondientes en T221Permisos_UndsOrgActuales_SerieExped_CCD.
# - Realizar consultas en la tabla T221Permisos_UndsOrgActuales_SerieExped_CCD para obtener los permisos actuales de las unidades organizacionales sobre las Series de Agrupaciones Documentales en el CCD que se está DESACTIVANDO.
# - Para cada registro de permisos obtenido, realizar un INSERT en T221Permisos_UndsOrgActuales_SerieExped_CCD para el CCD NUEVO, replicando los valores excepto el campo T221Id_CatSerie_UndOrg_CCD, el cual se debe cambiar por el valor de la Serie de Agrupación Documental PERSISTENTE en el CCD NUEVO.

# TODO: Subproceso 8 - Crear registros de CONSECUTIVOS de AGRUPACIONES DOCUMENTALES para las Series persistentes en el CCD NUEVO.
# - Consultar las Series de Agrupaciones Documentales PERSISTENTES en el CCD NUEVO (tabla T226AgrupacionesDocPersisten_Tmp).
# - Para cada Serie de Agrupación Documental PERSISTENTE encontrada, buscar los registros de consecutivos correspondientes en T245ConfigTiposExpedienteAgno.
# - Realizar consultas en la tabla T245ConfigTiposExpedienteAgno para obtener los consecutivos actuales de las agrupaciones documentales en el CCD que se está DESACTIVANDO.
# - Para cada registro de consecutivos obtenido, realizar un INSERT en T245ConfigTiposExpedienteAgno para el CCD NUEVO, replicando los valores excepto la PK y el campo T245Id_CatSerie_UndOrg_CCD, el cual se debe cambiar por el valor de la Serie de Agrupación Documental al que este persistió en el CCD NUEVO.

# TODO: Subproceso 9 - Crear registros de CONSECUTIVOS de TIPOLOGÍAS DOCUMENTALES para Unidades Organizacionales del tipo Sección/Subsección marcadas como PERSISTENTES en el CCD NUEVO.
# - Consultar las Unidades Organizacionales del tipo Sección/Subsección PERSISTENTES en el CCD NUEVO (tabla T225UndsSeccionPersisten_Tmp).
# - Para cada Unidad Organizacional del tipo Sección/Subsección PERSISTENTE encontrada, buscar los registros de consecutivos correspondientes en las tablas T246ConfigTipologiasDocAgno y T247ConsecPorNiveles_TipologiasDocAgno.
# - Realizar consultas en las tablas T246ConfigTipologiasDocAgno y T247ConsecPorNiveles_TipologiasDocAgno para obtener los consecutivos actuales de las tipologías documentales en el CCD que se está DESACTIVANDO.
# - Para cada registro de consecutivos obtenido, realizar un INSERT en T247ConsecPorNiveles_TipologiasDocAgno para el CCD NUEVO, replicando los valores excepto la PK y el campo T247Id_UnidadOrganizacional, el cual se debe cambiar por el valor de la Unidad Organizacional a la que esta persistió, es decir por el campo T225Id_UndSeccionNueva (hallado en el párrafo “b”), tampoco se replica el del campo T247Id_TRD, pues aquí debe ir la de la TRD nueva a activar.

# TODO: Subproceso 10 - Agregar la NUEVA unidad organizacional sugerida de los colaboradores de la entidad al módulo de TRASLADO MASIVO DE UNIDADES ORGANIZACIONALES.
# -  Asegurarse de ejecutar este subproceso después de las instrucciones del módulo de ACTIVACIÓN DE ORGANIGRAMA, en el apartado “Durante la activación de un nuevo organigrama”.
# -  Buscar todas las personas asociadas a una unidad organizacional del organigrama actual y la unidad del nuevo organigrama delegada para dicha unidad organizacional.
# -  Insertar registros en la tabla T026TemporalPersonasUnidad con los datos obtenidos, es decir, T010IdPersona, T227Id_UndSeccionActual, T227Id_UndSeccionNueva.
# -  Evitar sobre-escribir registros existentes en T026 si ya hay uno para la misma persona.

# TODO: Generar registros de auditoría para cada subproceso adicional.
# - Incluir información detallada como el usuario, módulo, fecha, dirección IP, descripción y valores actualizados.
# - Utilizar información específica de cada subproceso para personalizar la descripción y valores actualizados.

# TODO: Procesos para realizar
# - Revisar y mejorar la generación de mensajes para hacerlos más informativos y comprensibles para el usuario.
# - Borrar todos los registros existentes en las tablas temporales T225UndsSeccionPersisten_Tmp, T226AgrupacionesDocPersisten_Tmp y T227UndsSeccionResponsables_Tmp.
