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
from gestion_documental.models.ccd_models import CuadrosClasificacionDocumental
from gestion_documental.models.tca_models import TablasControlAcceso
from gestion_documental.models.trd_models import TablaRetencionDocumental

from transversal.serializers.activacion_organigrama_serializers import (
    OrganigramaCambioActualSerializer,
)

from transversal.serializers.activacion_organigrama_serializers import (
    OrganigramaSerializer,
    
)

# TODO: Implementar el formulario "Cambio de Organigrama Actual" para la activación de un nuevo organigrama.

# TODO: En el módulo de ACTIVACIÓN DEL ORGANIGRAMA, verificar si existe un Cuadro de Clasificación Documental (CCD) ACTUAL.

# TODO: Al activar el nuevo organigrama, actualizar los campos T017actual y T017fechaPuestaEnProduccion en la tabla T017Organigramas.
# TODO: Si el escenario es "SI Existe CCD ACTUAL", activar también el CCD, TRD y TCA correspondientes.
# TODO: Desactivar las versiones anteriores de CCD, TRD y TCA, actualizando los campos T206fechaRetiroDeProduccion, T206actual en la tabla T206CuadrosClasificacionDoc y campos similares en las tablas T212TablasRetencionDoc y T216TablasControlAcceso.
# TODO: En el campo T206justificacionNuevaVersion del registro del CCD que se está activando, asignar el valor "ACTIVACIÓN AUTOMÁTICA DESDE EL PROCESO DE 'CAMBIO DE ORGANIGRAMA ACTUAL'".
# TODO: Permitir la creación de una nueva versión del organigrama en caso de futuras modificaciones, permitiendo la opción de clonar un organigrama existente y estableciendo los campos T017fechaTerminado, T017fechaPuestaEnProduccion, T017fechaRetiroDeProduccion, T017Actual y T017rutaResolucion según sea necesario.

# TODO: Implementar la funcionalidad para que el usuario escriba una justificación para la activación del organigrama (campo T017justiifcacionNuevaVersion) en el formulario "Cambio de Organigrama Actual".

# TODO: Tomar la fecha del sistema y asignarla a los campos T017fechaPuestaEnProduccion y T017actual del registro correspondiente en la tabla T017Organigramas.

# TODO: En caso de existir un organigrama actual a desactivar, actualizar la fecha del sistema en el campo T017fechaRetiroDeProduccion y establecer T017actual en False en el registro de la tabla T017Organigramas correspondiente al organigrama actual.

# TODO: Si la activación involucra CCD, TRD y TCA (escenario 2), poner T017actual=True y T017fechaPuestaEnProduccion=FechaDelSistema en las tablas T206CuadrosClasificacionDoc, T212TablasRetencionDoc y T216TablasControlAcceso.

# TODO: Desactivar las versiones anteriores de CCD, TRD y TCA:
#     - Actualizar los campos TxxfechaRetiroDeProduccion=FechaDelSistema y Txxactual en False en los registros de las tablas T206CuadrosClasificacionDoc, T212TablasRetencionDoc y T216TablasControlAcceso.

# TODO: Asignar el valor "ACTIVACIÓN AUTOMÁTICA DESDE EL PROCESO DE 'CAMBIO DE ORGANIGRAMA ACTUAL'" al campo T206justificacionNuevaVersion en la tabla T206CuadrosClasificacionDoc del registro del CCD que se está activando.

# TODO: Asegurar que a partir del momento en que el nuevo organigrama se establezca como el actual, esté disponible para su uso en el sistema, y prohibir cambios en él hasta que se realice un nuevo proceso de cambio de organigrama.

# TODO: Implementar la funcionalidad para crear una nueva versión del organigrama en caso de modificaciones futuras:
#     - Ofrecer la opción de crear desde cero o clonar un organigrama existente.
#     - Si se elige clonar, generar una nueva versión con campos T017fechaTerminado vacío, T017fechaPuestaEnProduccion y T017fechaRetiroDeProduccion vacíos, T017Actual en False y T017rutaResolucion vacío.


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
                id_organigrama_anterior = organigrama_anterior[0]
                if organigrama_actual.id_organigrama != id_organigrama_anterior:
                    temporal_all.delete()
                    
                organigrama_nuevo = list(temporal_all.values_list('id_unidad_org_nueva__id_organigrama__id_organigrama', flat=True).distinct())
                # id_organigrama_nuevo = organigrama_nuevo[0]
                if organigrama_seleccionado.id_organigrama not in organigrama_nuevo:
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
            algo = self.activar_organigrama(organigrama_seleccionado, data_desactivar, data_activar, data_auditoria)
        
        else:
            data_activar_org = data_activar
            data_activar_org['justificacion_nueva_version'] = data['justificacion']
            algo = self.activar_organigrama(organigrama_seleccionado, data_desactivar, data_activar_org, data_auditoria)

    

# TODO: Implementar validaciones adicionales previas al proceso de Activación del Organigrama.

# TODO: Validar la existencia de un CCD ACTIVO antes de ejecutar las validaciones.
# - Consultar en la tabla T206CuadrosClasificacionDoc para verificar si hay algún registro con T206actual = True.

# TODO: Verificar que se hayan completado los módulos en el siguiente orden:
# 1. Homologación de Secciones Persistentes del CCD.
#    - Asegurarse de que el usuario haya marcado correctamente las secciones persistentes del CCD actual en el módulo correspondiente.
# 2. Asignación de Secciones Responsables del CCD.
#    - Confirmar que se hayan asignado responsables para las secciones no persistentes en el nuevo CCD.
# 3. Delegación de Oficinas Responsables de Expedientes del CCD.
#    - Validar que no queden unidades organizacionales sin asignar en el proceso de delegación.

# TODO: Realizar las siguientes validaciones al ingresar al módulo de Activación del Organigrama:
# 1. Validar que no exista ninguna unidad organizacional del CCD ACTUAL sin delegación de responsable en el CCD NUEVO.
#    - Realizar consultas en las tablas T019UnidadesOrganizacionales y T227UndsSeccionResponsables_Tmp.
#    - Mostrar un mensaje de error detallando las unidades organizacionales sin delegación.
# 2. Verificar la correcta identificación de las Agrupaciones Documentales persistentes del CCD ACTUAL en el CCD NUEVO.
#    - Revisar la identificación en las tablas T224CatSeries_UndOrg_CCD, T225UndsSeccionPersisten_Tmp y T226AgrupacionesDocPersisten_Tmp.
#    - Generar un mensaje de error indicando las Agrupaciones Documentales no identificadas correctamente.

# TODO: Mostrar mensajes de error y deseleccionar el CCD elegido si las validaciones anteriores no se cumplen.
# - Mensaje de error si hay unidades sin delegación en el nuevo CCD.
# - Mensaje de error si hay Agrupaciones Documentales persistentes no identificadas correctamente.

# TODO: Combinar las consultas de unidades activas del organigrama actual y sus registros de delegación en una sola instrucción de base de datos.

# TODO: Ejecutar los siguientes subprocesos adicionales después de las validaciones y procesos actuales de Activación de Organigrama.

# TODO: Subproceso 1 - Cambiar unidades organizacionales del tipo sección o subsección que administran Agrupaciones Documentales.
# - Consultar la tabla temporal T227UndsSeccionResponsables_Tmp para obtener las asignaciones de unidades entre el CCD DESACTIVANDO y el CCD ACTIVANDO.
# - Actualizar la tabla T019UnidadesOrganizacionales de acuerdo con la información obtenida de T227.
# - Agregar comentarios detallados para cada subproceso adicional que se deba realizar después de las validaciones y procesos actuales.

# TODO: Subproceso 2 - Cambiar unidades organizacionales responsables de expedientes y documentos en todo el sistema.
# - Consultar la tabla temporal T227UndsSeccionResponsables_Tmp para obtener las asignaciones de unidades entre el CCD DESACTIVANDO y el CCD ACTIVANDO.
# - Actualizar la tabla T236ExpedientesDocumentales y T237DocumentosDeArchivo_Expediente según las asignaciones obtenidas.

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
