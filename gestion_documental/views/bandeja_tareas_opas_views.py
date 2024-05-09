import copy
from datetime import datetime, date, timedelta

from io import BytesIO
import json
from django.conf import settings
from django.db.models import Q
from django.forms import model_to_dict
import os
from django.db import transaction
from django.shortcuts import render
from rest_framework import generics,status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from gestion_documental.models.bandeja_tareas_models import AdicionalesDeTareas, ReasignacionesTareas, TareasAsignadas
from gestion_documental.models.ccd_models import CatalogosSeriesUnidad
from gestion_documental.models.conf__tipos_exp_models import ConfiguracionTipoExpedienteAgno
from gestion_documental.models.expedientes_models import ExpedientesDocumentales, IndicesElectronicosExp
from gestion_documental.serializers.expedientes_serializers import AperturaExpedienteComplejoSerializer, AperturaExpedienteSimpleSerializer
from gestion_documental.views.conf__tipos_exp_views import ConfiguracionTipoExpedienteAgnoGetConsect
from gestion_documental.views.pqr_views import RadicadoCreate
from gestion_documental.models.configuracion_tiempos_respuesta_models import ConfiguracionTiemposRespuesta
from gestion_documental.models.radicados_models import  AsignacionTramites, BandejaTareasPersona, SolicitudAlUsuarioSobrePQRSDF, TareaBandejaTareasPersona
from rest_framework.exceptions import ValidationError,NotFound
from gestion_documental.models.trd_models import CatSeriesUnidadOrgCCDTRD, TipologiasDoc
from gestion_documental.serializers.bandeja_tareas_opas_serializer import  ActosAdministrativosCreateSerializer, AdicionalesDeTareasopaGetByTareaSerializer, Anexos_TramitresAnexosGetSerializer, AnexosRespuestaRequerimientosGetSerializer, AnexosTramiteCreateSerializer, OpaTramiteDetalleGetBandejaTareasSerializer, OpaTramiteTitularGetBandejaTareasSerializer, RequerimientoSobreOPACreateSerializer, RequerimientoSobreOPATramiteGetSerializer, RequerimientosOpaTramiteCreateserializer, RespuestaOPAGetSerializer, RespuestaOpaTramiteCreateserializer, RespuestaRequerimientoOPACreateserializer, RespuestasOPAGetSeralizer, SolicitudesTramitesOpaDetalleSerializer, TareasAsignadasOpasGetSerializer, TareasAsignadasOpasUpdateSerializer,Anexos_RequerimientoCreateSerializer,RequerimientoSobreOPAGetSerializer
from gestion_documental.views.archivos_digitales_views import ArchivosDgitalesCreate
from gestion_documental.views.bandeja_tareas_views import AnexosCreate, Estados_PQRCreate, MetadatosAnexosTmpCreate, TareaBandejaTareasPersonaUpdate
from tramites.models.tramites_models import AnexosTramite, PermisosAmbSolicitudesTramite, Requerimientos, RespuestaOPA, RespuestasRequerimientos, SolicitudesTramites, TiposActosAdministrativos
from gestion_documental.choices.tipo_archivo_choices import tipo_archivo_CHOICES
from gestion_documental.utils import UtilsGestor
from seguridad.utils import Util

from docxtpl import DocxTemplate

from django.core.files.uploadedfile import InMemoryUploadedFile

class TareasAsignadasGetOpasByPersona(generics.ListAPIView):
    serializer_class = TareasAsignadasOpasGetSerializer
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
        filter['id_tarea_asignada__cod_tipo_tarea'] = 'ROpa' 

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




class DetalleOpaGetbyId(generics.ListAPIView):
    serializer_class = SolicitudesTramitesOpaDetalleSerializer
    queryset = PermisosAmbSolicitudesTramite.objects.all()
    permission_classes = [IsAuthenticated]

    
    def get(self, request,id):
        instance =self.queryset.filter(id_solicitud_tramite=id,id_permiso_ambiental__cod_tipo_permiso_ambiental='OP').first()

        if not instance:
            raise NotFound("No existen Opa asociada a esta id.")
        

        serializador = self.serializer_class(instance)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializador.data,}, status=status.HTTP_200_OK)

class CrearExpedienteOPA(generics.CreateAPIView):
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
            
        data_expediente['titulo_expediente'] = f"Expediente OPA {codigo_exp_und_serie_subserie} {current_date.year}"
        data_expediente['descripcion_expediente'] = f"Expediente OPA para la unidad {codigo_exp_und_serie_subserie} y el año {current_date.year}"
        data_expediente['palabras_clave_expediente'] = f"Expediente|OPA|{codigo_exp_und_serie_subserie}|{current_date.year}"
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
class TareasAsignadasAceptarOpaUpdate(generics.UpdateAPIView):
    serializer_class = TareasAsignadasOpasUpdateSerializer
    actos_administrativo = ActosAdministrativosCreateSerializer
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
                    
                    if tarea.id_asignacion:
                        id_asignacion = tarea.id_asignacion
                       
                        tarea.cod_estado_solicitud = 'De'
                        tarea.save()
                       
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

            vista_creadora_expediente = CrearExpedienteOPA()
            request.data['id_cat_serie_und_org_ccd_trd_prop'] = asignacion.id_catalogo_serie_subserie
            request.data['id_unidad_org_oficina_respon_original'] = asignacion.id_und_org_seccion_asignada.id_unidad_organizacional
            request.data['id_und_org_oficina_respon_actual'] = asignacion.id_und_org_seccion_asignada.id_unidad_organizacional
            request.data['id_persona_titular_exp_complejo'] = asignacion.id_solicitud_tramite.id_persona_titular
            respuesta = vista_creadora_expediente.create(request)
            respuesta = respuesta.data['data']

            id_expediente = respuesta['id_expediente_documental']
            expediente = ExpedientesDocumentales.objects.filter(id_expediente_documental=id_expediente).first()
            if not expediente:
                raise NotFound("No se encontro el expediente")
           

           #hola
           #TiposActosAdministrativos
            tipo_acto = TiposActosAdministrativos.objects.filter(id_tipo_acto_administrativo=1).first()
            ActaInicioCreate

            expediente.id_tipo_acto = tipo_acto
            tramite = asignacion.id_solicitud_tramite
            tramite.id_expediente = expediente
            tramite.fecha_expediente = respuesta['fecha_apertura_expediente']
            tramite.save()
           



        return Response({'success':True,'detail':"Se acepto la tarea correctamente.","data":serializer.data,'data_asignacion':data_asignacion},status=status.HTTP_200_OK)
    


class TareasAsignadasOpasRechazarUpdate(generics.UpdateAPIView):
    serializer_class = TareasAsignadasOpasUpdateSerializer
    queryset = TareasAsignadas.objects.all()
    permission_classes = [IsAuthenticated]
    vista_asignacion = TareaBandejaTareasPersonaUpdate()
    @transaction.atomic
    def put(self,request,pk):
        
        data_in = request.data
        instance = TareasAsignadas.objects.filter(id_tarea_asignada=pk).first()
        
        if not instance:
            raise NotFound("No se existe un registro con este codigo.")
        
        if instance.cod_tipo_tarea != 'ROpa':
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
        #print(data_in)
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
            #print(id_asignacion)
            asignacion = AsignacionTramites.objects.filter(id_asignacion_tramite=id_asignacion,cod_estado_asignacion__isnull=True).first()
                # raise ValidationError(asignacion.id_pqrsdf)
            if not asignacion:
                raise NotFound("No se encontro la asignacion")
            asignacion.cod_estado_asignacion = 'Re'
            asignacion.justificacion_rechazo = data_in['justificacion_rechazo']
            asignacion.save()
       
        
        return Response({'success':True,'detail':"Se actualizo la actividad Correctamente.","data":serializer.data,'data_asignacion':data_asignacion},status=status.HTTP_200_OK)

#REQUERIMIENTO SOBRE OPA 
    

class OpaPersonaTitularGet(generics.ListAPIView):
    serializer_class = OpaTramiteTitularGetBandejaTareasSerializer
    queryset = SolicitudesTramites.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self,request,tra):
        
        instance = self.get_queryset().filter(id_solicitud_tramite=tra).first()

        

        if not instance:
            raise NotFound("No existen registros")
        persona_titular = instance.id_persona_titular 
        serializer = self.serializer_class(persona_titular)

        
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data}, status=status.HTTP_200_OK)

class OpaTramiteDetalleGet(generics.ListAPIView):
    serializer_class = OpaTramiteDetalleGetBandejaTareasSerializer
    queryset = SolicitudesTramites.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self, request, tra):

        instance = self.get_queryset().filter(id_solicitud_tramite=tra).first()


        if not instance:
            raise NotFound("No existen registros")
        serializer = self.serializer_class(instance)


        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data}, status=status.HTTP_200_OK)
    






class RequerimientoSobreOPACreate(generics.CreateAPIView):
    serializer_class = RequerimientoSobreOPACreateSerializer
    serializer_class_anexo_pqr = Anexos_RequerimientoCreateSerializer
    queryset = SolicitudAlUsuarioSobrePQRSDF.objects.all()
    vista_estados = Estados_PQRCreate()
    vista_anexos = AnexosCreate()
    vista_archivos = ArchivosDgitalesCreate()
    vista_meta_dato = MetadatosAnexosTmpCreate()
    permission_classes = [IsAuthenticated]
    @transaction.atomic
    def post(self, request):
        fecha_actual =datetime.now()
        solicitud_usu_PQRSDF = request.data.get('solicitud_usu_PQRSDF')
        persona = request.user.persona
        categoria = tipo_archivo_CHOICES
        id_unidad = None
        data_anexos =[]
        #DATOS PARA AUDITORIA MATESTRO DETALLE
        valores_creados_detalles=[]
       
       
        data_archivos=[]
        if persona.id_unidad_organizacional_actual:
            id_unidad = persona.id_unidad_organizacional_actual.id_unidad_organizacional
        if not solicitud_usu_PQRSDF:
            raise ValidationError("Se requiere informacion del Requerimiento")
        
        archivos = request.FILES.getlist('archivo')
        anexos = request.data.getlist('anexo')

        
        archivos_blancos = len(anexos)-len(archivos)
        contador = 0 #cuenta los anexos que tienen archivos digitales
        json_anexos =[]
        for anexo in anexos:
            json_anexo = json.loads(anexo)
            json_anexos.append(json_anexo)

        data_in = json.loads(solicitud_usu_PQRSDF)

        #for archivo in archivos:
        for archivo in archivos:
            if  archivo:
                ruta = "home,BIA,Otros,OPAS,Complementos"
                respuesta_archivo = self.vista_archivos.crear_archivo({"ruta":ruta,'es_Doc_elec_archivo':False},archivo)
                data_archivo = respuesta_archivo.data['data']
                if respuesta_archivo.status_code != status.HTTP_201_CREATED:
                    return respuesta_archivo
                #print(respuesta_archivo.data['data'])
                data_archivos.append(respuesta_archivo.data['data'])
                contador = contador+1
        for i in range(archivos_blancos):
            anexo_temporal = json_anexos[contador]
            meta_dato = anexo_temporal['meta_data']
            info_archivo = {}
            info_archivo['Nombre del Anexo'] = anexo_temporal['nombre_anexo']
            info_archivo['Asunto'] = meta_dato['asunto']
            info_archivo['descripcion'] = meta_dato['descripcion']
            
            for x in categoria:
                if x[0] == meta_dato['cod_categoria_archivo']:
                    info_archivo['Categoria de Archivo'] = x[1]

            if meta_dato['id_tipologia_doc']:
                tipologia = TipologiasDoc.objects.filter(id_tipologia_documental= meta_dato['id_tipologia_doc']).first()
                if tipologia:
                    info_archivo['Tipologia Documental'] =tipologia.nombre
              
            else:
               info_archivo['Tipologia Documental'] = meta_dato['tipologia_no_creada_TRD']
            #info_archivo['Medio_de_Almacenamiento'] = anexo_temporal['medio_almacenamiento']
            
            arch_blanco =  UtilsGestor.generar_archivo_blanco(info_archivo)
            data_archivos.append(arch_blanco.data['data'])
            i= i+1
            contador = contador+1
        total_folios =0
        for anexo,archivo in zip(json_anexos,data_archivos):
            #print( archivo['id_archivo_digital'])
            #print(anexo)
            #print(anexo['meta_data'])
            respuesta_anexo = self.vista_anexos.crear_anexo(anexo)
            if respuesta_anexo.status_code != status.HTTP_200_OK:
                return respuesta_anexo
            
            ##AUDITORIA DETALLE
            valores_creados_detalles.append({"NombreAnexo":anexo['nombre_anexo']})
            data_anexo = respuesta_anexo.data['data']
            meta_dato = anexo['meta_data']
            meta_dato['id_anexo']= data_anexo['id_anexo']
            meta_dato['id_archivo_sistema'] = archivo['id_archivo_digital']
            meta_dato['nro_folios_documento'] = data_anexo['numero_folios']
            respuest_meta_dato = self.vista_meta_dato.crear_meta_data(meta_dato)
            if respuest_meta_dato.status_code != status.HTTP_200_OK:
                return respuest_meta_dato
            #print(respuest_meta_dato.data['data'])
            data_anexos.append({**data_anexo,"meta_data":respuest_meta_dato.data['data'],'archivo':archivo})
            if data_anexo['numero_folios']:
                total_folios = total_folios + data_anexo['numero_folios']
 
        # raise ValidationError("SIU")
        data_in['fecha_solicitud'] =fecha_actual
        data_in['cod_tipo_oficio'] ='R'
        data_in['id_persona_solicita'] = request.user.persona.id_persona
        data_in['id_und_org_oficina_solicita'] = id_unidad
        data_in['id_estado_actual_solicitud'] = 1 # 254 Estado guardado
        data_in['fecha_ini_estado_actual'] = fecha_actual
        data_in['cantidad_anexos'] =len(data_anexos)
        data_in['nro_folios_totales'] = total_folios

        #Tiempo que tiene un usuario para responder una Solicitud de Complementación o Solicitud de Requerimientos. tabla T271
        tiempo_respuesta = ConfiguracionTiemposRespuesta.objects.filter(nombre_configuracion='Tiempo que tiene un usuario para responder una Solicitud de Complementación o Solicitud de Requerimientos.').first()

        if not tiempo_respuesta:
            raise ValidationError("No se encontro el tiempo de respuesta comuniquese con un administrador"
                                  )
        data_in['dias_para_respuesta'] =tiempo_respuesta.tiempo_respuesta_en_dias


        
        serializer = self.serializer_class(data=data_in)
        serializer.is_valid(raise_exception=True)
        intance =serializer.save()
         
        #CREA UN ESTADO NUEVO DE PQR T255
        data_estado = {}
        data_estado['solicitud_usu_sobre_PQR'] = intance.id_solicitud_al_usuario_sobre_pqrsdf
        data_estado['estado_solicitud'] = 1 # 254 Estado guardado
        data_estado['persona_genera_estado'] = persona.id_persona
        data_estado['fecha_iniEstado'] = fecha_actual
        data_estado['id_tramite'] = data_in['id_solicitud_tramite']
        respuesta_estado = self.vista_estados.crear_estado(data_estado)
        data_respuesta_estado_asociado = respuesta_estado.data['data']
        ##CREAR LA RELACION ENTRE EL ANEXO Y EL COMPLEMENTO T259
        relacion_pqr=[]
        for anexo in data_anexos:
            data_relacion ={}
            data_relacion['id_anexo'] = anexo['id_anexo']
            data_relacion['id_solicitud_usu_sobre_PQR'] = intance.id_solicitud_al_usuario_sobre_pqrsdf
            serializer_relacion = self.serializer_class_anexo_pqr(data=data_relacion) 
            serializer_relacion.is_valid(raise_exception=True)
            intance_3 =serializer_relacion.save()  
            relacion_pqr.append(serializer_relacion.data)
        
        descripcion = {"IdSolicitudTramite":intance.id_solicitud_tramite,"IdPersonaSolicita":intance.id_persona_solicita,"fecha_solicitud":intance.fecha_solicitud}
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 181,
            "cod_permiso": "CR",
            "subsistema": 'GEST',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_creados_detalles": valores_creados_detalles
            }
        Util.save_auditoria_maestro_detalle(auditoria_data)
        #BUSCA LA TAREA Y COLOCA LOS ATRIBUTOS DE REQUERIMIENTOS PENDIENTES A TRUE
        if  not 'id_tarea' in request.data:
            raise ValidationError("Debe enviarse la id de la tarea")
        tarea = TareasAsignadas.objects.filter(id_tarea_asignada=request.data['id_tarea']).first()

        if not tarea:
            raise ValidationError("No se encontro la tarea")
        asignacion_tarea = TareaBandejaTareasPersona.objects.filter(id_tarea_asignada=tarea.id_tarea_asignada,es_responsable_ppal=True)
        if asignacion_tarea:
            tarea.requerimientos_pendientes_respuesta = True
            tarea.save()



        print(tarea)
        
        return Response({'succes': True, 'detail':'Se crearon los siguientes registros', 'data':serializer.data,"estado":data_respuesta_estado_asociado,'anexos':data_anexos,'relacion_pqr':relacion_pqr}, status=status.HTTP_200_OK)

class RequerimientosPQRSDFGetByTramiteOPA(generics.ListAPIView):

    serializer_class = RequerimientoSobreOPAGetSerializer
    queryset =SolicitudAlUsuarioSobrePQRSDF.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self, request,tra):
        
        instance = self.get_queryset().filter(id_solicitud_tramite=tra,cod_tipo_oficio='R')
        if not instance:
            raise NotFound("No existen registros")
        
        serializador = self.serializer_class(instance,many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializador.data,}, status=status.HTTP_200_OK)



class RequerimientosTramiteGetByTramiteOPA(generics.ListAPIView):

    serializer_class = RequerimientoSobreOPATramiteGetSerializer
    queryset =Requerimientos.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self, request,tra):
        
        instance = self.get_queryset().filter(id_solicitud_tramite=tra)
        if not instance:
            raise NotFound("No existen registros")
        
        serializador = self.serializer_class(instance,many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializador.data,}, status=status.HTTP_200_OK)



class AnexosRequerimientoGetByRequerimiento(generics.ListAPIView):
#AnexosTramiteCreateSerializer
    serializer_class = Anexos_TramitresAnexosGetSerializer
    queryset = AnexosTramite.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self, request,re):
        
        instance = self.get_queryset().filter(id_requerimiento=re)
        if not instance:
            raise NotFound("No existen registros")
        
        serializador = self.serializer_class(instance,many=True)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializador.data,}, status=status.HTTP_200_OK)
    



##RESPUESTA A LA OPA 
class RespuestaOpaTramiteCreate(generics.CreateAPIView):
    serializer_class = RespuestaOpaTramiteCreateserializer
    serializer_class_anexo_tamite = AnexosTramiteCreateSerializer
    queryset = RespuestaOPA.objects.all()
    permission_classes = [IsAuthenticated]
    vista_estados = Estados_PQRCreate()
    vista_anexos = AnexosCreate()
    vista_archivos = ArchivosDgitalesCreate()
    vista_meta_dato = MetadatosAnexosTmpCreate()

    @transaction.atomic
    def post(self, request):
        fecha_actual =datetime.now()
        respuesta = request.data.get('respuesta')
        persona = request.user.persona
        categoria = tipo_archivo_CHOICES
        id_unidad = None
        data_anexos =[]
        #DATOS PARA AUDITORIA MATESTRO DETALLE
        valores_creados_detalles=[]
       
        data_archivos=[]
        if persona.id_unidad_organizacional_actual:
            id_unidad = persona.id_unidad_organizacional_actual.id_unidad_organizacional
        if not respuesta:
            raise ValidationError("Se requiere informacion de la respuesta")
        
        archivos = request.FILES.getlist('archivo')
        anexos = request.data.getlist('anexo')

        
        archivos_blancos = len(anexos)-len(archivos)
        contador = 0 #cuenta los anexos que tienen archivos digitales
        json_anexos =[]
        for anexo in anexos:
            json_anexo = json.loads(anexo)
            json_anexos.append(json_anexo)

        data_in = json.loads(respuesta)

        respuesta_opa = RespuestaOPA.objects.filter(id_solicitud_tramite=data_in['id_solicitud_tramite']).first()
        if respuesta_opa:
            raise ValidationError("La respuesta ya existe")
        #for archivo in archivos:
        for archivo in archivos:
            if  archivo:
                ruta = "home,BIA,Otros,OPAS,Respuestas"
                respuesta_archivo = self.vista_archivos.crear_archivo({"ruta":ruta,'es_Doc_elec_archivo':False},archivo)
                data_archivo = respuesta_archivo.data['data']
                if respuesta_archivo.status_code != status.HTTP_201_CREATED:
                    return respuesta_archivo
                #print(respuesta_archivo.data['data'])
                data_archivos.append(respuesta_archivo.data['data'])
                contador = contador+1
        for i in range(archivos_blancos):
            anexo_temporal = json_anexos[contador]
            meta_dato = anexo_temporal['meta_data']
            info_archivo = {}
            info_archivo['Nombre del Anexo'] = anexo_temporal['nombre_anexo']
            info_archivo['Asunto'] = meta_dato['asunto']
            info_archivo['descripcion'] = meta_dato['descripcion']
            
            for x in categoria:
                if x[0] == meta_dato['cod_categoria_archivo']:
                    info_archivo['Categoria de Archivo'] = x[1]

            if meta_dato['id_tipologia_doc']:
                tipologia = TipologiasDoc.objects.filter(id_tipologia_documental= meta_dato['id_tipologia_doc']).first()
                if tipologia:
                    info_archivo['Tipologia Documental'] =tipologia.nombre
              
            else:
               info_archivo['Tipologia Documental'] = meta_dato['tipologia_no_creada_TRD']
            #info_archivo['Medio_de_Almacenamiento'] = anexo_temporal['medio_almacenamiento']
            
            arch_blanco =  UtilsGestor.generar_archivo_blanco(info_archivo)
            data_archivos.append(arch_blanco.data['data'])
            i= i+1
            contador = contador+1
        total_folios =0
        for anexo,archivo in zip(json_anexos,data_archivos):
            #print( archivo['id_archivo_digital'])
            #print(anexo)
            #print(anexo['meta_data'])
            respuesta_anexo = self.vista_anexos.crear_anexo(anexo)
            if respuesta_anexo.status_code != status.HTTP_200_OK:
                return respuesta_anexo
            
            ##AUDITORIA DETALLE
            valores_creados_detalles.append({"NombreAnexo":anexo['nombre_anexo']})
            data_anexo = respuesta_anexo.data['data']
            meta_dato = anexo['meta_data']
            meta_dato['id_anexo']= data_anexo['id_anexo']
            meta_dato['id_archivo_sistema'] = archivo['id_archivo_digital']
            meta_dato['nro_folios_documento'] = data_anexo['numero_folios']
            respuest_meta_dato = self.vista_meta_dato.crear_meta_data(meta_dato)
            if respuest_meta_dato.status_code != status.HTTP_200_OK:
                return respuest_meta_dato
            #print(respuest_meta_dato.data['data'])
            data_anexos.append({**data_anexo,"meta_data":respuest_meta_dato.data['data'],'archivo':archivo})
            if data_anexo['numero_folios']:
                total_folios = total_folios + data_anexo['numero_folios']


        data_in['fecha_respuesta'] = fecha_actual
        data_in['id_persona_responde'] =persona.id_persona
        data_in['estado'] = 1
        data_in['nro_folios_totales'] = total_folios
        data_in['cantidad_anexos'] = len(data_anexos)#

        #RespuestaOPA
        # data_radicado = {}
        # data_radicado['fecha_actual'] = fecha_actual
        # data_radicado['id_persona'] = request.user.persona.id_persona
        # data_radicado['tipo_radicado'] = "E" #validar cual tipo de radicado
        # data_radicado['modulo_radica'] = 'Trámites y servicios'

        # print(data_radicado)
        # radicadoCreate = RadicadoCreate()
                
        # respuesta_radicado = radicadoCreate.post(data_radicado)
        # print(respuesta_radicado)

        # data_in['id_radicado'] = respuesta_radicado['id_radicado']
        # data_in['fecha_radicado'] = respuesta_radicado['fecha_radicado']




        
        serializer = self.serializer_class(data=data_in)
        serializer.is_valid(raise_exception=True)
        intance =serializer.save()
         
        #CREA UN ESTADO NUEVO DE PQR T255
        # data_estado = {}
        # data_estado['solicitud_usu_sobre_PQR'] = intance.id_solicitud_al_usuario_sobre_pqrsdf
        # data_estado['estado_solicitud'] = 1 # 254 Estado guardado
        # data_estado['persona_genera_estado'] = persona.id_persona
        # data_estado['fecha_iniEstado'] = fecha_actual
        # data_estado['id_tramite'] = data_in['id_solicitud_tramite']
        # respuesta_estado = self.vista_estados.crear_estado(data_estado)
        # data_respuesta_estado_asociado = respuesta_estado.data['data']

        ##CREAR LA RELACION ENTRE EL ANEXO Y LA RESPUESTA
        relacion_requerimiento=[]
        for anexo in data_anexos:
            data_relacion ={}
            data_relacion['id_anexo'] = anexo['id_anexo']
            data_relacion['id_respuesta_opa'] = intance.id_respuesta_opa
            serializer_relacion = self.serializer_class_anexo_tamite(data=data_relacion) 
            serializer_relacion.is_valid(raise_exception=True)
            intance_3 =serializer_relacion.save()  
            relacion_requerimiento.append(serializer_relacion.data)
        
        descripcion = {"IdRespuestaOpa":intance.id_solicitud_tramite,"IdPersonaRespode":intance.id_persona_responde,"FechaRespuesta":intance.fecha_respuesta}
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 308,
            "cod_permiso": "CR",
            "subsistema": 'GEST',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_creados_detalles": valores_creados_detalles
            }
        Util.save_auditoria_maestro_detalle(auditoria_data)
        #BUSCA LA TAREA Y COLOCA LOS ATRIBUTOS DE REQUERIMIENTOS PENDIENTES A TRUE
        if  not 'id_tarea' in request.data:
            raise ValidationError("Debe enviarse la id de la tarea")
        tarea = TareasAsignadas.objects.filter(id_tarea_asignada=request.data['id_tarea']).first()

        if not tarea:
            raise ValidationError("No se encontro la tarea")
        


        nombre_completo_responde = None
        nombre_list = [persona.primer_nombre, persona.segundo_nombre,
                        persona.primer_apellido, persona.segundo_apellido]
        nombre_completo_responde = ' '.join(item for item in nombre_list if item is not None)
        nombre_completo_responde = nombre_completo_responde if nombre_completo_responde != "" else None
        nombre_persona = nombre_completo_responde


        tarea.cod_estado_solicitud = 'Re'
        tarea.fecha_respondido =intance.fecha_respuesta #fecha_respuesta
        tarea.nombre_persona_que_responde = nombre_persona
        tarea.save()
        #SI LA TAREA FUE FRUTO DE UNA REASIGNACION 
        if tarea.id_tarea_asignada_padre_inmediata:
            tarea_padre = tarea.id_tarea_asignada_padre_inmediata

            # Iterar a través de las tareas padres hasta encontrar la tarea original
            while tarea_padre and not tarea_padre.id_asignacion:
                tarea_padre.fecha_respondido = intance.fecha_respuesta #fecha_respuesta
                tarea_padre.nombre_persona_que_responde = nombre_persona
                tarea_padre.ya_respondido_por_un_delegado = True
                tarea_padre.save()

                # Ir a la siguiente tarea padre
                tarea_padre = tarea_padre.id_tarea_asignada_padre_inmediata

            # Si se encontró la tarea original, actualizarla
            if tarea_padre:
                tarea_padre.fecha_respondido = intance.fecha_respuesta #fecha_respuesta
                tarea_padre.nombre_persona_que_responde = nombre_persona
                tarea_padre.ya_respondido_por_un_delegado = True
                tarea_padre.save()
        
        return Response({'succes': True, 'detail':'Se crearon los siguientes registros', 'data':serializer.data,"estado":'data_respuesta_estado_asociado','anexos':data_anexos,'relacion_pqr':relacion_requerimiento}, status=status.HTTP_200_OK)

class RespuestaOpaGet(generics.ListAPIView):
    serializer_class = RespuestaOPAGetSerializer
    queryset = RespuestaOPA.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request,tra):
        instance= self.get_queryset().filter(id_solicitud_tramite=tra).first()
        if not instance:
            raise ValidationError("La OPA no ha sido contestada")
        
        serializer = self.serializer_class(instance)
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':serializer.data,}, status=status.HTTP_200_OK)






class RespestaOpasInfoAnexosGet(generics.ListAPIView):
    serializer_class = AnexosRespuestaRequerimientosGetSerializer
    queryset = RespuestaOPA.objects.all()
    permission_classes = [IsAuthenticated]


    def get (self, request,pk):
        data=[]
        instance =self.queryset.filter(id_respuesta_opa=pk).first()


        if not instance:
                raise NotFound("No existen registros")
        anexos_opa = AnexosTramite.objects.filter(id_respuesta_opa=instance)
        for x in anexos_opa:
            info_anexo =x.id_anexo
            data_anexo = self.serializer_class(info_anexo)
            data.append(data_anexo.data)
        
        
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':data,}, status=status.HTTP_200_OK)
    

    
class RequerimienntoSobreOpaTramiteCreate(generics.CreateAPIView):
    serializer_class = RequerimientosOpaTramiteCreateserializer
    serializer_class_anexo_tamite = AnexosTramiteCreateSerializer
    queryset = Requerimientos.objects.all()
    permission_classes = [IsAuthenticated]
    vista_estados = Estados_PQRCreate()
    vista_anexos = AnexosCreate()
    vista_archivos = ArchivosDgitalesCreate()
    vista_meta_dato = MetadatosAnexosTmpCreate()



    @transaction.atomic
    def post(self, request):
        fecha_actual =datetime.now()
        requerimiento = request.data.get('requerimiento')
        persona = request.user.persona
        categoria = tipo_archivo_CHOICES
        id_unidad = None
        data_anexos =[]
        #DATOS PARA AUDITORIA MATESTRO DETALLE
        valores_creados_detalles=[]
       
        data_archivos=[]
        if persona.id_unidad_organizacional_actual:
            id_unidad = persona.id_unidad_organizacional_actual.id_unidad_organizacional
        if not requerimiento:
            raise ValidationError("Se requiere informacion del Requerimiento")
        
        archivos = request.FILES.getlist('archivo')
        anexos = request.data.getlist('anexo')

        
        archivos_blancos = len(anexos)-len(archivos)
        contador = 0 #cuenta los anexos que tienen archivos digitales
        json_anexos =[]
        for anexo in anexos:
            json_anexo = json.loads(anexo)
            json_anexos.append(json_anexo)

        data_in = json.loads(requerimiento)

        #for archivo in archivos:
        for archivo in archivos:
            if  archivo:
                ruta = "home,BIA,Otros,OPAS,Complementos"
                respuesta_archivo = self.vista_archivos.crear_archivo({"ruta":ruta,'es_Doc_elec_archivo':False},archivo)
                data_archivo = respuesta_archivo.data['data']
                if respuesta_archivo.status_code != status.HTTP_201_CREATED:
                    return respuesta_archivo
                #print(respuesta_archivo.data['data'])
                data_archivos.append(respuesta_archivo.data['data'])
                contador = contador+1
        for i in range(archivos_blancos):
            anexo_temporal = json_anexos[contador]
            meta_dato = anexo_temporal['meta_data']
            info_archivo = {}
            info_archivo['Nombre del Anexo'] = anexo_temporal['nombre_anexo']
            info_archivo['Asunto'] = meta_dato['asunto']
            info_archivo['descripcion'] = meta_dato['descripcion']
            
            for x in categoria:
                if x[0] == meta_dato['cod_categoria_archivo']:
                    info_archivo['Categoria de Archivo'] = x[1]

            if meta_dato['id_tipologia_doc']:
                tipologia = TipologiasDoc.objects.filter(id_tipologia_documental= meta_dato['id_tipologia_doc']).first()
                if tipologia:
                    info_archivo['Tipologia Documental'] =tipologia.nombre
              
            else:
               info_archivo['Tipologia Documental'] = meta_dato['tipologia_no_creada_TRD']
            #info_archivo['Medio_de_Almacenamiento'] = anexo_temporal['medio_almacenamiento']
            
            arch_blanco =  UtilsGestor.generar_archivo_blanco(info_archivo)
            data_archivos.append(arch_blanco.data['data'])
            i= i+1
            contador = contador+1
        total_folios =0
        for anexo,archivo in zip(json_anexos,data_archivos):
            #print( archivo['id_archivo_digital'])
            #print(anexo)
            #print(anexo['meta_data'])
            respuesta_anexo = self.vista_anexos.crear_anexo(anexo)
            if respuesta_anexo.status_code != status.HTTP_200_OK:
                return respuesta_anexo
            
            ##AUDITORIA DETALLE
            valores_creados_detalles.append({"NombreAnexo":anexo['nombre_anexo']})
            data_anexo = respuesta_anexo.data['data']
            meta_dato = anexo['meta_data']
            meta_dato['id_anexo']= data_anexo['id_anexo']
            meta_dato['id_archivo_sistema'] = archivo['id_archivo_digital']
            meta_dato['nro_folios_documento'] = data_anexo['numero_folios']
            respuest_meta_dato = self.vista_meta_dato.crear_meta_data(meta_dato)
            if respuest_meta_dato.status_code != status.HTTP_200_OK:
                return respuest_meta_dato
            #print(respuest_meta_dato.data['data'])
            data_anexos.append({**data_anexo,"meta_data":respuest_meta_dato.data['data'],'archivo':archivo})
            if data_anexo['numero_folios']:
                total_folios = total_folios + data_anexo['numero_folios']
        data_in['fecha_requerimiento'] = fecha_actual
        data_in['id_persona_crea_requerimiento'] =persona.id_persona
        data_in['plazo_inicial_entrega']  = fecha_actual
        data_in['plazo_final_entrega'] = fecha_actual
        data_in['estado'] = 3


        # #Tiempo que tiene un usuario para responder una Solicitud de Complementación o Solicitud de Requerimientos. tabla T271
        tiempo_respuesta = ConfiguracionTiemposRespuesta.objects.filter(id_configuracion_tiempo_respuesta=6).first()#'Tiempo que tiene un usuario para responder una Solicitud de Complementación o Solicitud de Requerimientos.

        if not tiempo_respuesta:
            raise ValidationError("No se encontro el tiempo de respuesta comuniquese con un administrador")
               
               
        delta = timedelta(days=tiempo_respuesta.tiempo_respuesta_en_dias)

        fecha_nueva = fecha_actual + delta                   
        data_in['plazo_inicial_entrega'] = fecha_nueva

        data_radicado = {}
        data_radicado['fecha_actual'] = fecha_actual
        data_radicado['id_persona'] = request.user.persona.id_persona
        data_radicado['tipo_radicado'] = "E"
        data_radicado['modulo_radica'] = 'Trámites y servicios'
        #print(data_radicado)
        radicadoCreate = RadicadoCreate()
           
        respuesta_radicado = radicadoCreate.post(data_radicado)
        #print(respuesta_radicado)

        data_in['id_radicado'] = respuesta_radicado['id_radicado']
        data_in['fecha_radicado'] = respuesta_radicado['fecha_radicado']




        
        serializer = self.serializer_class(data=data_in)
        serializer.is_valid(raise_exception=True)
        intance =serializer.save()
         
        #CREA UN ESTADO NUEVO DE PQR T255
        # data_estado = {}
        # data_estado['solicitud_usu_sobre_PQR'] = intance.id_solicitud_al_usuario_sobre_pqrsdf
        # data_estado['estado_solicitud'] = 1 # 254 Estado guardado
        # data_estado['persona_genera_estado'] = persona.id_persona
        # data_estado['fecha_iniEstado'] = fecha_actual
        # data_estado['id_tramite'] = data_in['id_solicitud_tramite']
        # respuesta_estado = self.vista_estados.crear_estado(data_estado)
        # data_respuesta_estado_asociado = respuesta_estado.data['data']
        ##CREAR LA RELACION ENTRE EL ANEXO Y EL COMPLEMENTO T259
        relacion_requerimiento=[]
        for anexo in data_anexos:
            data_relacion ={}
            data_relacion['id_anexo'] = anexo['id_anexo']
            data_relacion['id_requerimiento'] = intance.id_requerimiento
            serializer_relacion = self.serializer_class_anexo_tamite(data=data_relacion) 
            serializer_relacion.is_valid(raise_exception=True)
            intance_3 =serializer_relacion.save()  
            relacion_requerimiento.append(serializer_relacion.data)
        
        descripcion = {"IdSolicitudTramite":intance.id_solicitud_tramite,"IdPersonaCrea":intance.id_persona_crea_requerimiento,"FechaRequerimiento":intance.fecha_requerimiento}
        direccion=Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 309,
            "cod_permiso": "CR",
            "subsistema": 'GEST',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_creados_detalles": valores_creados_detalles
            }
        #Util.save_auditoria_maestro_detalle(auditoria_data)
        #BUSCA LA TAREA Y COLOCA LOS ATRIBUTOS DE REQUERIMIENTOS PENDIENTES A TRUE
        if  not 'id_tarea' in request.data:
            raise ValidationError("Debe enviarse la id de la tarea")
        tarea = TareasAsignadas.objects.filter(id_tarea_asignada=request.data['id_tarea']).first()

        if not tarea:
            raise ValidationError("No se encontro la tarea")
        asignacion_tarea = TareaBandejaTareasPersona.objects.filter(id_tarea_asignada=tarea.id_tarea_asignada,es_responsable_ppal=True)
        if asignacion_tarea:
            tarea.requerimientos_pendientes_respuesta = True
            tarea.save()
        
        return Response({'succes': True, 'detail':'Se crearon los siguientes registros', 'data':serializer.data,"estado":'data_respuesta_estado_asociado','anexos':data_anexos,'relacion_pqr':relacion_requerimiento}, status=status.HTTP_200_OK)




class ComplementoTareaOPAGetByTarea(generics.ListAPIView):#RespuestaRequerimientos
    serializer_class = AdicionalesDeTareasopaGetByTareaSerializer
    queryset = AdicionalesDeTareas.objects.all()

    def get(self, request,tarea):

        instance = TareasAsignadas.objects.filter(id_tarea_asignada=tarea).first()
        
        if not instance.id_asignacion:
            aux = instance
            while aux:
                aux=aux.id_tarea_asignada_padre_inmediata
                if  aux and aux.id_asignacion:
                    instance = aux 
                    break
            
            #raise ValidationError('No se encontro la asignacion')
        print(instance)
        complemento = AdicionalesDeTareas.objects.filter(id_tarea_asignada=instance)
        
        print(complemento)
        if not complemento:
            raise NotFound("No se encontro el complemento")
      
        serializer = self.serializer_class(complemento,many=True)
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros', 'data': serializer.data,}, status=status.HTTP_200_OK)
    


class RespuestaTramitesOpasInfoAnexosGet(generics.ListAPIView):
    serializer_class = AnexosRespuestaRequerimientosGetSerializer
    queryset = RespuestasRequerimientos.objects.all()
    permission_classes = [IsAuthenticated]


    def get (self, request,pk):
        data=[]
        instance =self.queryset.filter(id_respuesta_requerimiento=pk).first()


        if not instance:
                raise NotFound("No existen registros")
        anexos_opa = AnexosTramite.objects.filter(id_respuesta_requerimiento=instance)
        for x in anexos_opa:
            info_anexo =x.id_anexo
            data_anexo = self.serializer_class(info_anexo)
            data.append(data_anexo.data)
        
        
        return Response({'succes': True, 'detail':'Se encontraron los siguientes registros', 'data':data,}, status=status.HTTP_200_OK)
    




class RespuestaPQRSDFByTra(generics.UpdateAPIView):

    serializer_class = RespuestasOPAGetSeralizer
    queryset = RespuestaOPA.objects.all()
    permission_classes = [IsAuthenticated]
    def get(self, request,tra):
        
        respuesta = self.get_queryset().filter(id_solicitud_tramite=tra)
        if not respuesta:
            raise NotFound("No existen registros")

        serializer = self.serializer_class(respuesta,many=True)
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros', 'data': serializer.data,}, status=status.HTTP_200_OK)
        



class ActaInicioCreate(generics.CreateAPIView):



    @transaction.atomic
    def create(self, request):
        fecha_actual =datetime.now()
        data_in = request.data



        dato=self.acta_inicio(data_in['pk'])
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
    def acta_inicio(self,pk):


        context = {
            'key':pk

        }

        pathToTemplate = str(settings.BASE_DIR) + '/recaudo/templates/prueba.docx'
        outputPath = str(settings.BASE_DIR) + '/recaudo/templates/output.docx'

        doc = DocxTemplate(pathToTemplate)
        doc.render(context)
        #doc.save(outputPath)

        return doc
