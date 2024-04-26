import copy
from datetime import datetime
from io import BytesIO
from django.conf import settings
from django.db import transaction
from rest_framework import generics,status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from gestion_documental.choices.tipo_archivo_choices import tipo_archivo_CHOICES
from gestion_documental.models.bandeja_tareas_models import AdicionalesDeTareas, ReasignacionesTareas, TareasAsignadas
from gestion_documental.models.conf__tipos_exp_models import ConfiguracionTipoExpedienteAgno
from gestion_documental.models.configuracion_tiempos_respuesta_models import ConfiguracionTiemposRespuesta
from gestion_documental.models.expedientes_models import ExpedientesDocumentales, IndicesElectronicosExp
from gestion_documental.models.radicados_models import PQRSDF, Anexos, Anexos_PQR, AsignacionOtros, AsignacionPQR, AsignacionTramites, BandejaTareasPersona, ComplementosUsu_PQR, Estados_PQR, MetadatosAnexosTmp, Otros, RespuestaPQR, SolicitudAlUsuarioSobrePQRSDF, TareaBandejaTareasPersona
from gestion_documental.models.trd_models import CatSeriesUnidadOrgCCDTRD, TipologiasDoc
from gestion_documental.serializers.bandeja_tareas_tramites_serializers import AnexosTramitesGetSerializer, ComplementosUsu_TramiteGetByIdSerializer, DetalleTramitesComplementosUsu_PQRGetSerializer, MetadatosAnexosTramitesTmpSerializerGet, ReasignacionesTareasTramitesCreateSerializer, ReasignacionesTareasgetTramitesByIdSerializer, SolicitudesTramitesDetalleGetSerializer, TareasAsignadasGetTramiteJustificacionSerializer, TareasAsignadasTramiteUpdateSerializer, TareasAsignadasTramitesGetSerializer

from gestion_documental.serializers.expedientes_serializers import AperturaExpedienteComplejoSerializer, AperturaExpedienteSimpleSerializer
from gestion_documental.serializers.ventanilla_pqrs_serializers import AnexoArchivosDigitalesSerializer, Anexos_PQRAnexosGetSerializer, AnexosCreateSerializer, Estados_PQRPostSerializer, MetadatosAnexosTmpCreateSerializer, MetadatosAnexosTmpGetSerializer, PQRSDFGetSerializer, SolicitudAlUsuarioSobrePQRSDFCreateSerializer
from gestion_documental.utils import UtilsGestor
from gestion_documental.views.archivos_digitales_views import ArchivosDgitalesCreate
from gestion_documental.views.bandeja_tareas_views import TareaBandejaTareasPersonaCreate, TareaBandejaTareasPersonaUpdate, TareasAsignadasCreate
from gestion_documental.views.conf__tipos_exp_views import ConfiguracionTipoExpedienteAgnoGetConsect
from seguridad.utils import Util
from transversal.models.lideres_models import LideresUnidadesOrg
from transversal.models.organigrama_models import UnidadesOrganizacionales
from tramites.models.tramites_models import SolicitudesTramites

from transversal.models.personas_models import Personas
from rest_framework.exceptions import ValidationError,NotFound

from docxtpl import DocxTemplate

from django.core.files.uploadedfile import InMemoryUploadedFile



class ActaInicioCreate(generics.CreateAPIView):



    @transaction.atomic
    def create(self, request):
        fecha_actual =datetime.now()
        data_in = request.data



        dato=self.acta_inicio(data_in)
        memoria = self.document_to_inmemory_uploadedfile(dato)
        data_archivos =[]
        vista_archivos = ArchivosDgitalesCreate()
        ruta = "home,BIA,Otros,RecursoHidrico,Avances"

        respuesta_archivo = vista_archivos.crear_archivo({"ruta":ruta,'es_Doc_elec_archivo':False},memoria)
        data_archivo = respuesta_archivo.data['data']
        if respuesta_archivo.status_code != status.HTTP_201_CREATED:
            return respuesta_archivo
        
        
        print(dato)

        return Response({'succes': True, 'detail':'Se crearon los siguientes registros', 'data':data_archivo, }, status=status.HTTP_200_OK)



    def document_to_inmemory_uploadedfile(self,doc):
        # Guardar el documento en un búfer de memoria
        buffer = BytesIO()
        doc.save(buffer)
        
        # Crear un objeto InMemoryUploadedFile
        file = InMemoryUploadedFile(
            buffer,  # El búfer de memoria que contiene los datos
            None,    # El campo de archivo (no es relevante en este contexto)
            'output.docx',  # El nombre del archivo
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # El tipo MIME del archivo
            buffer.tell(),  # El tamaño del archivo en bytes
            None     # El conjunto de caracteres (no es relevante en este contexto)
        )
        
        return file
    def acta_inicio(self,data):


        context = data

        pathToTemplate = str(settings.BASE_DIR) + '/gestion_documental/templates/auto_plantilla.docx'
        outputPath = str(settings.BASE_DIR) + '/gestion_documental/templates/output.docx'

        doc = DocxTemplate(pathToTemplate)
        doc.render(context)
        #doc.save(outputPath)

        return doc


class TareasAsignadasGetTramitesByPersona(generics.ListAPIView):
    serializer_class = TareasAsignadasTramitesGetSerializer
    queryset = TareaBandejaTareasPersona.objects.all()
    permission_classes = [IsAuthenticated]

    
    def get(self, request,id):
        filter={}
       
        bandeja_tareas= BandejaTareasPersona.objects.filter(id_persona=id).first()

        if not bandeja_tareas:
            raise NotFound('No se encontro la bandeja de tareas')
        id_bandeja = bandeja_tareas.id_bandeja_tareas_persona
        #Buscamos la asignacion de tareas de la bandeja de tareas


       
        # if not tareas_asignadas:
        #     raise NotFound('No se encontro tareas asignadas')
        

        filter['id_bandeja_tareas_persona']= id_bandeja
        filter['id_tarea_asignada__cod_tipo_tarea'] = 'Rtra' 

        for key, value in request.query_params.items():

            if key == 'estado_asignacion':
                if value != '':
                    if value =='None':
                          filter['id_tarea_asignada__cod_estado_asignacion__isnull'] = True
                    else:
                        filter['id_tarea_asignada__cod_estado_asignacion'] = value
            if key == 'estado_tarea':
                if value != '':
                    filter['id_tarea_asignada__cod_estado_solicitud'] = value
            if key == 'fecha_inicio':
                if value != '':
                    
                    filter['id_tarea_asignada__fecha_asignacion__gte'] = datetime.strptime(value, '%Y-%m-%d').date()
            if key == 'fecha_fin':
                if value != '':
                    filter['id_tarea_asignada__fecha_asignacion__lte'] = datetime.strptime(value, '%Y-%m-%d').date()

            if key == 'requerimiento':
                if value != '':
                    filter['id_tarea_asignada__requerimientos_pendientes_respuesta'] = value
        #id_tarea_asignada
                    
        print(filter)
        #.filter(**filter).order_by('fecha_radicado')
        tareas_asignadas = self.get_queryset().filter(**filter).order_by('id_tarea_asignada__fecha_asignacion')
        #tareas_asignadas = TareaBandejaTareasPersona.objects.filter(id_bandeja_tareas_persona=id_bandeja)
        tareas = [tarea.id_tarea_asignada for tarea in tareas_asignadas]
       

        serializer = self.serializer_class(tareas, many=True)

        
        radicado_value = request.query_params.get('radicado')
        data_validada =[]
        data_validada = serializer.data
        if radicado_value != '':
            data_validada = [item for item in serializer.data if radicado_value in item.get('radicado', '')]
        else :
            data_validada = serializer.data
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':data_validada,}, status=status.HTTP_200_OK)



class DetalleSolicitudesTramitesGet(generics.ListAPIView):

    serializer_class = SolicitudesTramitesDetalleGetSerializer
    queryset = SolicitudesTramites.objects.all()


    def get(self, request, id):

        instance = self.get_queryset().filter(id_solicitud_tramite=id).first()
        if not instance:
            raise NotFound('No se encontro el otro')
        serializer = self.serializer_class(instance)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)


class TramitesInfoAnexosGet(generics.ListAPIView):
    serializer_class = AnexosTramitesGetSerializer
    queryset =SolicitudesTramites.objects.all()
    permission_classes = [IsAuthenticated]


    def get (self, request,pk):
        data=[]
        instance =self.queryset.filter(id_solicitud_tramite=pk).first()


        if not instance:
                raise NotFound("No existen registros")
        anexos_pqrs = Anexos_PQR.objects.filter(id_tramite=instance)
        for x in anexos_pqrs:
            info_anexo =x.id_anexo
            data_anexo = self.serializer_class(info_anexo)
            data.append(data_anexo.data)
        
        
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':data,}, status=status.HTTP_200_OK)
    



class TareasAsignadasTramitesRechazarUpdate(generics.UpdateAPIView):
    serializer_class = TareasAsignadasTramiteUpdateSerializer
    queryset = TareasAsignadas.objects.all()
    permission_classes = [IsAuthenticated]
    vista_asignacion = TareaBandejaTareasPersonaUpdate()

    def put(self,request,pk):
        
        
        data_in = request.data
        instance = TareasAsignadas.objects.filter(id_tarea_asignada=pk).first()
        
        
        if not instance:
            raise NotFound("No se existe un registro con este codigo.")
        
        if instance.cod_tipo_tarea != 'Rtra':
            raise ValidationError("No se puede rechazar una tarea sino es otro")
        data_in['cod_estado_asignacion'] = 'Re'

        id_tarea =instance.id_tarea_asignada
        data_asignacion={}

 
        data_asignacion['fecha_leida'] = datetime.now()
        data_asignacion['leida'] = True
        respuesta_asignacion_tarea = self.vista_asignacion.actualizacion_asignacion_tarea(data_asignacion,id_tarea)
       
        if respuesta_asignacion_tarea.status_code != status.HTTP_200_OK:
            return respuesta_asignacion_tarea
        
        data_asignacion = respuesta_asignacion_tarea.data['data']
        instance_previous=copy.copy(instance)
        print(data_in)
        serializer = self.serializer_class(instance,data=data_in, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        #EN CASO DE SER UN REGISTRO FRUTO DE DE UNA REASIGNACION EL PROCESO 
        id_asignacion = instance.id_asignacion
        if not id_asignacion:
            
            tarea = instance
            if tarea.id_asignacion:
                    id_asignacion = tarea.id_asignacion

            else:#QUIERE DECIR QUE ESTA TAREA FUE REASIGNADA
                while not  tarea.id_asignacion:
                    tarea = tarea.id_tarea_asignada_padre_inmediata
                   
                    if tarea.id_asignacion:
                
                        break
                id_asignacion = tarea.id_asignacion
                reasignacion = ReasignacionesTareas.objects.filter(id_tarea_asignada = tarea.id_tarea_asignada, cod_estado_reasignacion='Ep').first()
                if reasignacion:
                    reasignacion.cod_estado_reasignacion = 'Re'
                    reasignacion.justificacion_reasignacion_rechazada = data_in['justificacion_rechazo']
                    reasignacion.save()
        else:
            print(id_asignacion)
            asignacion = AsignacionTramites.objects.filter(id_asignacion_tramite=id_asignacion,cod_estado_asignacion__isnull=True).first()
                # raise ValidationError(asignacion.id_pqrsdf)
            if not asignacion:
                raise NotFound("No se encontro la asignacion")
            asignacion.cod_estado_asignacion = 'Re'
            asignacion.justificacion_rechazo = data_in['justificacion_rechazo']
            asignacion.save()

        
        return Response({'success':True,'detail':"Se actualizo la actividad Correctamente.","data":serializer.data,'data_asignacion':data_asignacion},status=status.HTTP_200_OK)


class CrearExpedienteTramite(generics.CreateAPIView):
    serializer_class = AperturaExpedienteSimpleSerializer
    serializer_class_complejo = AperturaExpedienteComplejoSerializer
    permission_classes = [IsAuthenticated]


    

    def create(self, request):
        data = request.data

        data_expediente = {}
        
        # Crear codigo expediente
        tripleta_trd = CatSeriesUnidadOrgCCDTRD.objects.filter(id_cat_serie_und=data['id_cat_serie_und_org_ccd_trd_prop']).first()
        
        if not tripleta_trd:
            raise ValidationError('Debe enviar el id de la tripleta de TRD seleccionada')
        #PENDIENTE EL AÑO
        configuracion_expediente = ConfiguracionTipoExpedienteAgno.objects.filter(id_cat_serie_undorg_ccd = tripleta_trd.id_catserie_unidadorg).first()

        if not configuracion_expediente:
            raise ValidationError('No se encontró la configuración de expediente para la tripleta de TRD seleccionada')
        
        cod_unidad = tripleta_trd.id_cat_serie_und.id_unidad_organizacional.codigo
        cod_serie = tripleta_trd.id_cat_serie_und.id_catalogo_serie.id_serie_doc.codigo
        cod_subserie = tripleta_trd.id_cat_serie_und.id_catalogo_serie.id_subserie_doc.codigo if tripleta_trd.id_cat_serie_und.id_catalogo_serie.id_subserie_doc else None
        
        codigo_exp_und_serie_subserie = cod_unidad + '.' + cod_serie + '.' + cod_subserie if cod_subserie else cod_unidad + '.' + cod_serie
        
        
        current_date = datetime.now()
        
        
        data_expediente['codigo_exp_und_serie_subserie'] = codigo_exp_und_serie_subserie
        data_expediente['codigo_exp_Agno'] = current_date.year
        
        # OBTENER CONSECUTIVO ACTUAL
        codigo_exp_consec_por_agno = None
        
        if configuracion_expediente.cod_tipo_expediente == 'C':
            # LLAMAR CLASE PARA GENERAR CONSECUTIVO
            fecha_actual = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            clase_consec = ConfiguracionTipoExpedienteAgnoGetConsect()
            codigo_exp_consec_por_agno = clase_consec.generar_radicado(
                tripleta_trd.id_catserie_unidadorg,
                request.user.persona.id_persona,
                fecha_actual
            )
            codigo_exp_consec_por_agno = codigo_exp_consec_por_agno.data.get('data').get('consecutivo_actual')
        else:
            expediente = ExpedientesDocumentales.objects.filter(id_cat_serie_und_org_ccd_trd_prop=tripleta_trd.id_catserie_unidadorg, codigo_exp_Agno=current_date.year).first()
        
            if expediente:
                raise ValidationError('Ya existe un expediente simple para este año en la Serie-Subserie-Unidad seleccionada')
            
        data_expediente['titulo_expediente'] = f"Expediente Tramite {codigo_exp_und_serie_subserie} {current_date.year}"
        data_expediente['descripcion_expediente'] = f"Expediente Tramite para la unidad {codigo_exp_und_serie_subserie} y el año {current_date.year}"
        data_expediente['palabras_clave_expediente'] = f"Expediente|Tramite|{codigo_exp_und_serie_subserie}|{current_date.year}"
        data_expediente['id_cat_serie_und_org_ccd_trd_prop'] = tripleta_trd.id_catserie_unidadorg
        data_expediente['id_trd_origen'] = tripleta_trd.id_trd.id_trd
        data_expediente['id_und_seccion_propietaria_serie'] = tripleta_trd.id_cat_serie_und.id_unidad_organizacional.id_unidad_organizacional
        data_expediente['id_serie_origen'] = tripleta_trd.id_cat_serie_und.id_catalogo_serie.id_serie_doc.id_serie_doc
        data_expediente['id_subserie_origen'] = tripleta_trd.id_cat_serie_und.id_catalogo_serie.id_subserie_doc.id_subserie_doc if tripleta_trd.id_cat_serie_und.id_catalogo_serie.id_subserie_doc else None
        data_expediente['codigo_exp_consec_por_agno'] = codigo_exp_consec_por_agno
        data_expediente['estado'] = 'A'
        data_expediente['fecha_apertura_expediente'] = current_date
        data_expediente['fecha_folio_inicial'] = current_date
        data_expediente['cod_etapa_de_archivo_actual_exped'] = 'G'
        data_expediente['tiene_carpeta_fisica'] = False
        data_expediente['ubicacion_fisica_esta_actualizada'] = False
        data_expediente['creado_automaticamente'] = True
        data_expediente['cod_tipo_expediente'] = configuracion_expediente.cod_tipo_expediente
        data_expediente['id_unidad_org_oficina_respon_original'] = data['id_unidad_org_oficina_respon_original']
        data_expediente['id_und_org_oficina_respon_actual'] = data['id_unidad_org_oficina_respon_original']


        request.data['cod_tipo_expediente'] = configuracion_expediente.cod_tipo_expediente
        request.data['codigo_exp_und_serie_subserie'] = codigo_exp_und_serie_subserie

        
        if configuracion_expediente.cod_tipo_expediente == 'S':
            serializer = self.serializer_class(data=data_expediente, context = {'request':request})
            serializer.is_valid(raise_exception=True)
            expediente_creado = serializer.save()
        elif configuracion_expediente.cod_tipo_expediente == 'C':
            serializer = self.serializer_class_complejo(data=data_expediente, context = {'request':request})
            serializer.is_valid(raise_exception=True)
            expediente_creado = serializer.save()
        

        
        # CREAR INDICE - PENDIENTE VALIDAR SI ES CORRECTO REALIZARLO ASÍ
        IndicesElectronicosExp.objects.create(
            id_expediente_doc = expediente_creado,
            fecha_indice_electronico = current_date,
            abierto = True
        )
        
        # AUDITORIA
        usuario = request.user.id_usuario
        descripcion = {
            "CodigoExpUndSerieSubserie": str(codigo_exp_und_serie_subserie),
            "CodigoExpAgno": str(serializer.data.get('codigo_exp_Agno')),
        }
        if codigo_exp_consec_por_agno:
            descripcion['CodigoExpConsecPorAgno'] = str(codigo_exp_consec_por_agno)
        
        direccion = Util.get_client_ip(request)
        auditoria_data = {
            "id_modulo" : 188,
            "cod_permiso": "CR",
            "subsistema": 'GEST',
            "dirip": direccion,
            "descripcion": descripcion,
        }
        Util.save_auditoria(auditoria_data)
            
        return Response({'success':True, 'detail':'Apertura realizada de manera exitosa', 'data':serializer.data}, status=status.HTTP_201_CREATED)


class TareasAsignadasAceptarTramiteUpdate(generics.UpdateAPIView):
    serializer_class = TareasAsignadasTramiteUpdateSerializer
    queryset = TareasAsignadas.objects.all()
    permission_classes = [IsAuthenticated]
    vista_asignacion = TareaBandejaTareasPersonaUpdate()
    @transaction.atomic
    def put(self,request,pk):
        
        #ACTUALIZA T315
        data_in = request.data
        instance = TareasAsignadas.objects.filter(id_tarea_asignada=pk).first()
        
        if not instance:
            raise NotFound("No se existe un registro con este codigo.")
        data_in['cod_estado_asignacion'] = 'Ac'
        data_in['cod_estado_solicitud'] = 'Ep'
        id_tarea =instance.id_tarea_asignada
        data_asignacion={}

 
        data_asignacion['fecha_leida'] = datetime.now()
        data_asignacion['leida'] = True
        respuesta_asignacion_tarea = self.vista_asignacion.actualizacion_asignacion_tarea(data_asignacion,id_tarea)
       
        if respuesta_asignacion_tarea.status_code != status.HTTP_200_OK:
            return respuesta_asignacion_tarea
        
        data_asignacion = respuesta_asignacion_tarea.data['data']
        instance_previous=copy.copy(instance)

        serializer = self.serializer_class(instance,data=data_in, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        #cambio de estado en asignacion en la t268
        id_asignacion = instance.id_asignacion
        print(id_asignacion)
        #VALIDACION ENTREGA 116

        if not id_asignacion:
            print('NO SE ENCONTRO ASIGNACION')
            print('TAREA PADRE ES ' +str(instance.id_tarea_asignada_padre_inmediata))
            tarea = instance
            if tarea.id_asignacion:
                    id_asignacion = tarea.id_asignacion

            else:#QUIERE DECIR QUE ESTA TAREA FUE REASIGNADA
                while not  tarea.id_asignacion:
                    tarea = tarea.id_tarea_asignada_padre_inmediata
                    print(tarea.id_asignacion)
                    if tarea.id_asignacion:
                        id_asignacion = tarea.id_asignacion
                        #print(id_asignacion)
                        tarea.cod_estado_solicitud = 'De'
                        tarea.save()
                        #raise ValidationError(str(tarea))
                        break
                
                ##CAMBIAMOS EL ESTADO DE LA TAREA PADRE A DELEGADA


                reasignacion = ReasignacionesTareas.objects.filter(id_tarea_asignada = tarea.id_tarea_asignada, cod_estado_reasignacion='Ep').first()
                if reasignacion:
                    reasignacion.cod_estado_reasignacion = 'Ac'
                    reasignacion.save()

        else:
            print(id_asignacion)
            asignacion = AsignacionTramites.objects.filter(id_asignacion_tramite=id_asignacion,cod_estado_asignacion__isnull=True).first()
            #asignacion = AsignacionOtros.objects.filter(id_asignacion_otros=id_asignacion,cod_estado_asignacion__isnull=True).first()
            #asignacion = AsignacionPQR.objects.filter(id_asignacion_pqr=id_asignacion,cod_estado_asignacion__isnull=True).first()
        
    
            if not asignacion:
                raise NotFound("No se encontro la asignacion")
            asignacion.cod_estado_asignacion = 'Ac'
            asignacion.save()


             #APERTURA DEL EXPEDIENTE

            vista_creadora_expediente = CrearExpedienteTramite()
            request.data['id_cat_serie_und_org_ccd_trd_prop'] = asignacion.id_catalogo_serie_subserie
            request.data['id_unidad_org_oficina_respon_original'] = asignacion.id_und_org_seccion_asignada.id_unidad_organizacional
            request.data['id_und_org_oficina_respon_actual'] = asignacion.id_und_org_seccion_asignada.id_unidad_organizacional
            request.data['id_persona_titular_exp_complejo'] = asignacion.id_solicitud_tramite.id_persona_titular
            respuesta = vista_creadora_expediente.create(request)

            print(respuesta.data)
            #raise ValidationError("HAAA")
            respuesta_expediente = respuesta.data['data']

            id_expediente = respuesta_expediente['id_expediente_documental']
            expediente = ExpedientesDocumentales.objects.filter(id_expediente_documental=id_expediente).first()
            if not expediente:
                raise NotFound("No se encontro el expediente")
           
            data_auto = {}

            data_auto['n_auto'] = 1


            crear = ActaInicioCreate()

            data_acto= {}
            request.data['n_auto'] = 'Auto 1'
            request.data['n_expediente'] = respuesta_expediente['codigo_exp_consec_por_agno']
           
            archivo_acto = crear.create(request)

            print(archivo_acto)
            raise ValidationError("HAAA")
            tramite = asignacion.id_solicitud_tramite
            tramite.id_expediente = expediente
            tramite.fecha_expediente = respuesta_expediente['fecha_apertura_expediente']
            tramite.save()

            


            
           

        return Response({'success':True,'detail':"Se acepto el tramite correctamente.","data":serializer.data,'data_asignacion':data_asignacion,'data_expediente':{**respuesta_expediente}},status=status.HTTP_200_OK)
    


class ReasignacionesTareasTramitesCreate(generics.CreateAPIView):
    serializer_class = ReasignacionesTareasTramitesCreateSerializer
    queryset = ReasignacionesTareas.objects.all()
    vista_tareas = TareasAsignadasCreate()
    permission_classes = [IsAuthenticated]
    def post(self, request):


        data_in = request.data
        data_in['fecha_reasignacion'] = datetime.now()
        data_in['cod_estado_reasignacion'] = 'Ep'

        tarea = TareasAsignadas.objects.filter(id_tarea_asignada=data_in['id_tarea_asignada']).first()
        if not tarea:
            raise NotFound("No existen registros de tareas")
        
        if tarea.cod_estado_asignacion == 'Re':
            raise ValidationError("Esta tarea fue Rechazada ")
        tarea.cod_estado_solicitud = 'De'

        reasignadas = ReasignacionesTareas.objects.filter(id_tarea_asignada=tarea.id_tarea_asignada, cod_estado_reasignacion='Ep').first()

        if reasignadas:
            raise ValidationError("La tarea tiene una reasignacion pendiente por responder.")
        tarea.save()
        serializer = self.serializer_class(data=data_in)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        ##CREAR NUEVO REGISTRO DE REASIGNACION DE TAREA T316
        data_tarea = {}
        data_tarea['cod_tipo_tarea'] = tarea.cod_tipo_tarea
        data_tarea['id_asignacion'] = None
        data_tarea['fecha_asignacion'] = datetime.now()
        data_tarea['cod_estado_solicitud'] = 'Ep'
        data_tarea['id_tarea_asignada_padre_inmediata'] = tarea.id_tarea_asignada
        data_tarea['comentario_asignacion'] = data_in['comentario_reasignacion']
        respuesta_tareas = self.vista_tareas.crear_asignacion_tarea(data_tarea)
        if respuesta_tareas.status_code != status.HTTP_201_CREATED:
            return respuesta_tareas

        data_tarea_respuesta =respuesta_tareas.data['data']

        #ASIGNO LA NUEVA TAREA A LA BANDEJA DE LA PERSONA 
        vista_asignar_tarea =TareaBandejaTareasPersonaCreate()
        data_tarea_bandeja_asignacion = {}
        data_tarea_bandeja_asignacion['id_persona'] = data_in['id_persona_a_quien_se_reasigna']
        data_tarea_bandeja_asignacion['id_tarea_asignada'] = data_tarea_respuesta['id_tarea_asignada']
        data_tarea_bandeja_asignacion['es_responsable_ppal'] = False
        respuesta_relacion = vista_asignar_tarea.crear_tarea(data_tarea_bandeja_asignacion)
        if respuesta_relacion.status_code != status.HTTP_201_CREATED:
            return respuesta_relacion

   
        return Response({'succes': True, 'detail':'Se crearon los siguientes registros', 'data':serializer.data,'data_tarea_respuesta':data_tarea_respuesta}, status=status.HTTP_200_OK)
    


class ReasignacionesTramitesTareasgetById(generics.ListAPIView):
    serializer_class = ReasignacionesTareasgetTramitesByIdSerializer
    queryset = ReasignacionesTareas.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self, request,pk):
        instance = self.get_queryset().filter(id_tarea_asignada=pk)
        if not instance:
            raise NotFound("No existen registros")
        serializer = self.serializer_class(instance,many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data}, status=status.HTTP_200_OK)

    
class TramitesAnexoMetaDataGet(generics.ListAPIView):
    serializer_class = MetadatosAnexosTramitesTmpSerializerGet
    queryset =Anexos.objects.all()
    permission_classes = [IsAuthenticated]


    def get (self, request,pk):
      
        instance =Anexos.objects.filter(id_anexo=pk).first()

        if not instance:
                raise NotFound("No existen registros")
        
        meta_data = MetadatosAnexosTmp.objects.filter(id_anexo=instance.id_anexo).first()
        if not meta_data:
            raise NotFound("No existen registros")
   
        serializer= self.serializer_class(meta_data)

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':{'id_anexo':instance.id_anexo,**serializer.data},}, status=status.HTTP_200_OK)
    


class TareasAsignadasTramitesJusTarea(generics.UpdateAPIView):

    serializer_class = TareasAsignadasGetTramiteJustificacionSerializer
    queryset = TareasAsignadas.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self, request,pk):
        
        tarea = TareasAsignadas.objects.filter(id_tarea_asignada=pk).first()
        
        if not tarea:
            raise NotFound('No se encontro la tarea')
        if  tarea.cod_estado_asignacion == 'Ac':
            raise NotFound('Esta tarea fue aceptada')
        
        serializer = self.serializer_class(tarea)
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros', 'data': serializer.data,}, status=status.HTTP_200_OK)



#Respuesta requerimientos hechos por el usuario 
    #T266SolicitudAlUsuarioSobrePQRSDF

class RequerimientosTramite(generics.ListAPIView):
    queryset = SolicitudAlUsuarioSobrePQRSDF.objects.all()
    serializer_class = ComplementosUsu_TramiteGetByIdSerializer
    permission_classes = [IsAuthenticated]

    def get (self,request,pk):
        #BUSCAMOS LA ID DEL TRAMITE 7266
        #instance = self.get_queryset().filter(id_solicitud_tramite=pk)
        complementos_tareas= AdicionalesDeTareas.objects.filter(id_tarea_asignada=pk)
#        print(complementos_tareas.first().id_complemento_usu_pqr)
        if not complementos_tareas:
            raise NotFound('No se encontraron registros')

        ids=list(complementos_tareas.values_list('id_complemento_usu_pqr', flat=True))


        
        complementos =  ComplementosUsu_PQR.objects.filter(idComplementoUsu_PQR__in=ids)

        serializer = self.serializer_class(complementos, many=True)

        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros', 'data': serializer.data, }, status=status.HTTP_200_OK)



class RespuestaTramitesInfoAnexosGet(generics.ListAPIView):
    serializer_class = AnexosTramitesGetSerializer
    queryset = ComplementosUsu_PQR.objects.all()
    permission_classes = [IsAuthenticated]


    def get (self, request,pk):
        data=[]
        instance =self.queryset.filter(idComplementoUsu_PQR=pk).first()


        if not instance:
                raise NotFound("No existen registros")
        anexos_pqrs = Anexos_PQR.objects.filter(id_complemento_usu_PQR=instance)
        for x in anexos_pqrs:
            info_anexo =x.id_anexo
            data_anexo = self.serializer_class(info_anexo)
            data.append(data_anexo.data)
        
        
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':data,}, status=status.HTTP_200_OK)
    
    
class ComplementoTramitesAnexoDocumentoDigitalGet(generics.ListAPIView):
    serializer_class = AnexoArchivosDigitalesSerializer
    queryset =Anexos.objects.all()
    permission_classes = [IsAuthenticated]


    def get (self, request,pk):
      
        instance =Anexos.objects.filter(id_anexo=pk).first()

        if not instance:
                raise NotFound("No existen registros")
        
        meta_data = MetadatosAnexosTmp.objects.filter(id_anexo=instance.id_anexo).first()
        if not meta_data:
            raise NotFound("No existen registros")
        archivo = meta_data.id_archivo_sistema
        serializer= self.serializer_class(archivo)

        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':{'id_anexo':instance.id_anexo,**serializer.data},}, status=status.HTTP_200_OK)
    


class DetalleRespuestaTramitesByIdGet(generics.ListAPIView):
    serializer_class = DetalleTramitesComplementosUsu_PQRGetSerializer
    queryset = ComplementosUsu_PQR.objects.all()
    permission_classes = [IsAuthenticated]


    def get (self, request,pk):
        data=[]
        instance =self.queryset.filter(idComplementoUsu_PQR=pk).first()


        if not instance:
                raise NotFound("No existen registros")

        serializer = self.serializer_class(instance)        
        
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)
    