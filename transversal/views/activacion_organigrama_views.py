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
    CCDActiveSerializer,
    OrganigramaCambioDeOrganigramaActualSerializer,
)

from transversal.serializers.organigrama_serializers import (
    NewUserOrganigramaSerializer,
)

# TODO: Implementar el formulario "Cambio de Organigrama Actual" para la activación de un nuevo organigrama.

# TODO: En el módulo de ACTIVACIÓN DEL ORGANIGRAMA, verificar si existe un Cuadro de Clasificación Documental (CCD) ACTUAL.

# TODO: Manejar los dos escenarios dependiendo de la existencia del CCD ACTUAL:
#     - NO Existe CCD ACTUAL:
#         - Cargar un listado de Organigramas terminados sin fecha de puesta en producción (T017fechaTerminado<>"" y T017fechaPuestaEnProduccion="", tabla T017Organigramas).
#         - Permitir al usuario seleccionar el organigrama a activar.
#     - SI Existe CCD ACTUAL:
#         - Cargar un listado de Organigramas terminados sin fecha de puesta en producción y ya usados en al menos un CCD terminado (T017fechaTerminado<>"" y T017fechaPuestaDeProduccion="", tabla T017Organigramas; campos T206Id_Organigrama, T206fechaTerminado<>"" de la tabla T206CuadrosClasificacionDoc).
#         - Permitir al usuario seleccionar el organigrama a activar.
#         - Cargar automáticamente y mostrar en forma NO editable el TRD unido al CCD y el TCA unido al TRD, siempre que el TCA esté terminado (campo T216fechaTerminado<>"" de la tabla T216TablasControlAcceso).
#         - Validar la existencia del TRD y el TCA correspondientes; mostrar un mensaje informativo si no se encuentran.

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


class GetCCDTerminadoByORG(generics.ListAPIView):
    serializer_class = CCDActiveSerializer
    queryset = CuadrosClasificacionDocumental.objects.filter(~Q(fecha_terminado = None) & Q(fecha_puesta_produccion=None))

    def get(self, request, id_organigrama):
        organigrama = Organigramas.objects.filter(id_organigrama = id_organigrama).first()
        if not organigrama:
            return Response({'success': False, 'detail': 'El organigrama ingresado no existe'}, status=status.HTTP_404_NOT_FOUND)

        if organigrama.fecha_terminado == None or organigrama.fecha_retiro_produccion != None or organigrama.fecha_puesta_produccion!=None:
            return Response({'success': False, 'detail': 'El organigrama ingresado ya está retirado, no está terminado o ya está en producción'}, status=status.HTTP_403_FORBIDDEN)
        ccds = self.queryset.all().filter(id_organigrama = organigrama.id_organigrama)
        
        lista=[]
        if ccds:
            for t in ccds:
                tca = TablasControlAcceso.objects.filter(id_trd__id_ccd=t).first()
                if tca:
                    list.append(t)
                    
        if not ccds:
            return Response({'success': False, 'detail': 'No existe CCD terminado basado en el organigrama seleccionado'}, status=status.HTTP_403_FORBIDDEN)
        serializador = self.serializer_class(lista,many=True)
        serializer_data = serializador.data
    
        return Response({'success': True, 'detail': 'CCD', 'data': serializador.data},status=status.HTTP_200_OK)


class ObtenerOrganigramaActual(generics.ListAPIView):
    serializer_class = NewUserOrganigramaSerializer
    queryset = Organigramas.objects.all()
    
    def get (self,request):
        
        organigrama_actual = self.queryset.all().filter(actual = True).first()
        
        if organigrama_actual:
            serializador = self.serializer_class(organigrama_actual)
            
            return Response({'success':True,'detail':'Busqueda exitosa','data':serializador.data},status=status.HTTP_200_OK)
        return Response({'success':True,'detail':'Busqueda exitosa, no existe organigrama actual'},status=status.HTTP_200_OK)


class ObtenerOrganigramasPosibles(generics.ListAPIView):
    serializer_class = NewUserOrganigramaSerializer
    queryset = Organigramas.objects.filter(actual=False, fecha_retiro_produccion=None).exclude(fecha_terminado=None)
    
    def get (self,request):
        serializador = self.serializer_class(self.queryset.all(), many=True)
        
        return Response({'success':True,'detail':'Los organigramas posibles para activar son los siguientes','data':serializador.data},status=status.HTTP_200_OK)


class CambioDeOrganigramaActual(generics.UpdateAPIView):
    serializer_class = OrganigramaCambioDeOrganigramaActualSerializer
    queryset = Organigramas.objects.exclude(fecha_terminado=None)
    queryset2 = CuadrosClasificacionDocumental.objects.all()
    
    def put(self,request):
        data = request.data
        user_logeado = request.user.id_usuario
        dirip = Util.get_client_ip(request)
        organigrama_seleccionado = self.queryset.filter(id_organigrama=data['organigrama'], fecha_retiro_produccion=None).first()
        organigrama_actual = self.queryset.filter(actual=True).first()
        ccd_actual = self.queryset2.filter(actual=True).first()
        
        if not organigrama_seleccionado:
            raise ValidationError('El organigrama elegido no se encuentra terminado o ha sido retirado de producción')
        elif organigrama_seleccionado.actual:
            raise ValidationError('No puede activar un organigrama que ya se encuentra activado')
        
        tca_actual = TablasControlAcceso.objects.filter(id_trd__id_ccd=ccd_actual).first()
        previous_activacion_organigrama = copy.copy(organigrama_seleccionado)
        
        temporal_all = TemporalPersonasUnidad.objects.all()
        
        if not ccd_actual:
            organigrama_seleccionado.justificacion_nueva_version = data['justificacion']
            organigrama_seleccionado.actual = True
            organigrama_seleccionado.fecha_puesta_produccion = datetime.now()
            
            if organigrama_actual:
                previous_desactivacion_organigrama = copy.copy(organigrama_actual)
                organigrama_actual.fecha_retiro_produccion = datetime.now()
                organigrama_actual.actual = False
                organigrama_actual.save()
                
                if temporal_all:
                    organigrama_anterior = list(temporal_all.values_list('id_unidad_org_anterior__id_organigrama__id_organigrama', flat=True).distinct())
                    id_organigrama_anterior = organigrama_anterior[0]
                    if organigrama_actual.id_organigrama != id_organigrama_anterior:
                        temporal_all.delete()
                
                # Auditoria Organigrama desactivado
                descripcion = {"NombreOrganigrama":str(organigrama_actual.nombre),"VersionOrganigrama":str(organigrama_actual.version)}
                valores_actualizados={'previous':previous_desactivacion_organigrama, 'current':organigrama_actual}
                auditoria_data = {'id_usuario': user_logeado,'id_modulo': 15,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
                Util.save_auditoria(auditoria_data)
            
            organigrama_seleccionado.save()
            if temporal_all:
                organigrama_nuevo = list(temporal_all.values_list('id_unidad_org_nueva__id_organigrama__id_organigrama', flat=True).distinct())
                id_organigrama_nuevo = organigrama_nuevo[0]
                if organigrama_seleccionado.id_organigrama != id_organigrama_nuevo:
                    temporal_all.delete()

            # Auditoria Organigrama activado
            descripcion = {"NombreOrganigrama":str(organigrama_seleccionado.nombre),"VersionOrganigrama":str(organigrama_seleccionado.version)}
            valores_actualizados={'previous':previous_activacion_organigrama, 'current':organigrama_seleccionado}
            auditoria_data = {'id_usuario': user_logeado,'id_modulo': 15,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
            Util.save_auditoria(auditoria_data)
        else:
            if not data.get('id_ccd'):
                raise ValidationError('Debe seleccionar un CCD')
            
            #CCD SELECCIONADO
            ccd_seleccionado = self.queryset2.filter(id_ccd=data.get('id_ccd'), id_organigrama=organigrama_seleccionado.id_organigrama).first()
            if not ccd_seleccionado:
                raise ValidationError('Debe seleccionar un CCD que pertenezca al organigrama que desea activar')
            
            if not ccd_seleccionado.fecha_terminado or ccd_seleccionado.fecha_retiro_produccion:
                raise ValidationError('El CCD seleccionado no se encuentra terminado o ha sido retirado de producción')
                
            tca = TablasControlAcceso.objects.filter(id_trd__id_ccd=ccd_seleccionado.id_ccd).first()

            previous_activacion_ccd = copy.copy(tca.id_trd.id_ccd)
            previous_activacion_trd = copy.copy(tca.id_trd)
            previous_activacion_tca = copy.copy(tca)

            previous_desactivacion_organigrama = copy.copy(tca_actual.id_trd.id_ccd.id_organigrama)
            previous_desactivacion_ccd = copy.copy(tca_actual.id_trd.id_ccd)
            previous_desactivacion_trd = copy.copy(tca_actual.id_trd)
            previous_desactivacion_tca = copy.copy(tca_actual)
            
            #ACTIVACION ORG
            
            organigrama_seleccionado.justificacion_nueva_version = data['justificacion']
            organigrama_seleccionado.actual = True
            organigrama_seleccionado.fecha_puesta_produccion = datetime.now()
            
            #ACTIVACION CCD
            
            tca.id_trd.id_ccd.actual = True
            tca.id_trd.id_ccd.fecha_puesta_produccion = datetime.now()
            tca.id_trd.id_ccd.justificacion = data['justificacion']
            
            #ACTIVACION TRD
            
            tca.id_trd.actual = True
            tca.id_trd.fecha_puesta_produccion = datetime.now()
            
            #ACTIVACION TCA
            
            tca.actual = True
            tca.fecha_puesta_produccion = datetime.now()
            
            #DESACTIVACION INSTRUMENTOS ARCHIVISTICOS ACTUALES
            
            tca_actual = TablasControlAcceso.objects.filter(id_trd__id_ccd=ccd_actual).first()
            
            #DESACTIVACION ORGANIGRAMA
            
            tca_actual.id_trd.id_ccd.id_organigrama.actual = False
            tca_actual.id_trd.id_ccd.id_organigrama.fecha_retiro_produccion = datetime.now()
            
            #DESACTIVACION CCD
            
            tca_actual.id_trd.id_ccd.actual = False
            tca_actual.id_trd.id_ccd.fecha_retiro_produccion = datetime.now()
    
            #DESACTIVACION TRD
            
            tca_actual.id_trd.actual = False
            tca_actual.id_trd.fecha_retiro_produccion = datetime.now()
            
            #DESACTIVACION TCA
            
            tca_actual.actual = False
            tca_actual.fecha_retiro_produccion = datetime.now()
            
            #GUARDADO ACTIVACION
            organigrama_seleccionado.save()
            tca.id_trd.id_ccd.save()
            tca.id_trd.save()
            tca.save()
            
            #GUARDADO DESACTIVACION
            tca_actual.id_trd.id_ccd.id_organigrama.save()
            tca_actual.id_trd.id_ccd.save()
            tca_actual.id_trd.save()
            tca_actual.save()
            
            if temporal_all:
                organigrama_anterior = list(temporal_all.values_list('id_unidad_org_anterior__id_organigrama__id_organigrama', flat=True).distinct())
                id_organigrama_anterior = organigrama_anterior[0]
                if tca_actual.id_trd.id_ccd.id_organigrama.id_organigrama != id_organigrama_anterior:
                    temporal_all.delete()
                    
                organigrama_nuevo = list(temporal_all.values_list('id_unidad_org_nueva__id_organigrama__id_organigrama', flat=True).distinct())
                id_organigrama_nuevo = organigrama_nuevo[0]
                if organigrama_seleccionado.id_organigrama != id_organigrama_nuevo:
                    temporal_all.delete()
            
            
            # Auditoria Organigrama desactivado
            descripcion = {"NombreOrganigrama":str(tca_actual.id_trd.id_ccd.id_organigrama.nombre),"VersionOrganigrama":str(tca_actual.id_trd.id_ccd.id_organigrama.version)}
            valores_actualizados={'previous':previous_desactivacion_organigrama, 'current':tca_actual.id_trd.id_ccd.id_organigrama}
            auditoria_data = {'id_usuario': user_logeado,'id_modulo': 15,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
            Util.save_auditoria(auditoria_data)
            
            # Auditoria Organigrama activado
            descripcion = {"NombreOrganigrama":str(organigrama_seleccionado.nombre),"VersionOrganigrama":str(organigrama_seleccionado.version)}
            valores_actualizados={'previous':previous_activacion_organigrama, 'current':organigrama_seleccionado}
            auditoria_data = {'id_usuario': user_logeado,'id_modulo': 15,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
            Util.save_auditoria(auditoria_data)

            # Auditoria CCD desactivado
            descripcion = {"NombreCCD":str(tca_actual.id_trd.id_ccd.nombre),"VersionCCD":str(tca_actual.id_trd.id_ccd.version)}
            valores_actualizados={'previous':previous_desactivacion_ccd, 'current':tca_actual.id_trd.id_ccd}
            auditoria_data = {'id_usuario': user_logeado,'id_modulo': 27,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
            Util.save_auditoria(auditoria_data)

            # Auditoria CCD activado
            descripcion = {"NombreCCD":str(tca.id_trd.id_ccd.nombre),"VersionCCD":str(tca.id_trd.id_ccd.version)}
            valores_actualizados={'previous':previous_activacion_ccd, 'current':tca.id_trd.id_ccd}
            auditoria_data = {'id_usuario': user_logeado,'id_modulo': 27,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
            Util.save_auditoria(auditoria_data)

            # Auditoria TRD desactivado
            descripcion = {"NombreTRD":str(tca_actual.id_trd.nombre),"VersionTRD":str(tca_actual.id_trd.version)}
            valores_actualizados={'previous':previous_desactivacion_trd, 'current':tca_actual.id_trd}
            auditoria_data = {'id_usuario': user_logeado,'id_modulo': 29,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
            Util.save_auditoria(auditoria_data)

            # Auditoria TRD activado
            descripcion = {"NombreTRD":str(tca.id_trd.nombre),"VersionTRD":str(tca.id_trd.version)}
            valores_actualizados={'previous':previous_activacion_trd, 'current':tca.id_trd}
            auditoria_data = {'id_usuario': user_logeado,'id_modulo': 29,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
            Util.save_auditoria(auditoria_data)

            # Auditoria TCA desactivado
            descripcion = {"NombreTCA":str(tca_actual.nombre),"VersionTCA":str(tca_actual.version)}
            valores_actualizados={'previous':previous_desactivacion_tca, 'current':tca_actual}
            auditoria_data = {'id_usuario': user_logeado,'id_modulo': 31,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
            Util.save_auditoria(auditoria_data)

            # Auditoria TCA activado
            descripcion = {"NombreTCA":str(tca.nombre),"VersionTCA":str(tca.version)}
            valores_actualizados={'previous':previous_activacion_tca, 'current':tca}
            auditoria_data = {'id_usuario': user_logeado,'id_modulo': 31,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
            Util.save_auditoria(auditoria_data)
            
        #unidades de personas desactivar
        if organigrama_actual:
            unidades_utilizadas=UnidadesOrganizacionales.objects.filter(id_organigrama=organigrama_actual.id_organigrama)
            unidades_list=[id.id_unidad_organizacional for id in unidades_utilizadas]
            persona_organigrama_a_remplazar=Personas.objects.filter(id_unidad_organizacional_actual__in=unidades_list)
            for persona in persona_organigrama_a_remplazar:
                persona.es_unidad_organizacional_actual=False
                persona.save()
            
        return Response({'success':True, 'detail':'Se ha activado correctamente el organigrama'}, status=status.HTTP_201_CREATED)




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
