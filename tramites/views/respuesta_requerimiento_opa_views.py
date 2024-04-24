
import copy
from datetime import datetime, date, timedelta

import json
from django.db.models import Q
from django.forms import model_to_dict
import os
from django.db import transaction
from rest_framework import generics,status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError,NotFound
from gestion_documental.models.trd_models import TipologiasDoc
from gestion_documental.views.archivos_digitales_views import ArchivosDgitalesCreate
from gestion_documental.views.bandeja_tareas_views import AnexosCreate, Estados_PQRCreate, MetadatosAnexosTmpCreate

from gestion_documental.views.pqr_views import RadicadoCreate
from tramites.models.tramites_models import RespuestasRequerimientos
from tramites.serializers.respuesta_requerimiento_opa_serializers import RespuestaRequerimientoOPACreateserializer,AnexosTramiteCreateSerializer
from gestion_documental.choices.tipo_archivo_choices import tipo_archivo_CHOICES
from gestion_documental.utils import UtilsGestor
from seguridad.utils import Util


class RespuestaRequerimientoOpaTramiteCreate(generics.CreateAPIView):
    serializer_class = RespuestaRequerimientoOPACreateserializer
    serializer_class_anexo_tamite = AnexosTramiteCreateSerializer
    queryset = RespuestasRequerimientos.objects.all()
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
            raise ValidationError("Se requiere informacion del Requerimiento")
        
        archivos = request.FILES.getlist('archivo')
        anexos = request.data.getlist('anexo')

        
        archivos_blancos = len(anexos)-len(archivos)
        contador = 0 #cuenta los anexos que tienen archivos digitales
        json_anexos =[]
        for anexo in anexos:
            json_anexo = json.loads(anexo)
            json_anexos.append(json_anexo)

        data_in = json.loads(respuesta)

        if not 'id_requerimiento' in data_in:
            raise ValidationError("Se requiere informacion del Requerimiento")
        id_requerimiento = data_in['id_requerimiento']

        respuestas= RespuestasRequerimientos.objects.filter(id_requerimiento=id_requerimiento).first()
        if respuestas:
            raise ValidationError("Ya existe una respuesta para este requerimiento")

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
        
        data_in['fecha_respuesta'] = fecha_actual
        data_in['id_persona_responde'] = request.user.persona.id_persona


        
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
  

        #Radicar 
        data_radicado = {}

        data_radicado = {}
        data_radicado['fecha_actual'] = fecha_actual
        data_radicado['id_persona'] = request.user.persona.id_persona
        data_radicado['tipo_radicado'] = "E"
        data_radicado['modulo_radica'] = 'Trámites y servicios'
        radicadoCreate = RadicadoCreate()
        respuesta_radicado = radicadoCreate.post(data_radicado)
        print(respuesta_radicado)


        data_in['id_radicado'] = respuesta_radicado['id_radicado']
        data_in['fecha_radicado'] = respuesta_radicado['fecha_radicado']

        serializer = self.serializer_class(data=data_in)
        serializer.is_valid(raise_exception=True)
        intance =serializer.save()


        relacion_requerimiento=[]
        for anexo in data_anexos:
            data_relacion ={}
            data_relacion['id_anexo'] = anexo['id_anexo']
            data_relacion['id_respuesta_requerimiento'] = intance.id_respuesta_requerimiento
            serializer_relacion = self.serializer_class_anexo_tamite(data=data_relacion) 
            serializer_relacion.is_valid(raise_exception=True)
            intance_3 =serializer_relacion.save()  
            relacion_requerimiento.append(serializer_relacion.data)
        
        descripcion = {"IdSolicitudTramite":intance.id_solicitud_tramite,"IdPersonaResponde":intance.id_persona_responde,"FechaRequerimiento":intance.fecha_respuesta}
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
        #Util.save_auditoria_maestro_detalle(auditoria_data)



        
        return Response({'succes': True, 'detail':'Se crearon los siguientes registros', 'data':serializer.data,"estado":'data_respuesta_estado_asociado','anexos':data_anexos,'relacion_pqr':relacion_requerimiento}, status=status.HTTP_200_OK)
