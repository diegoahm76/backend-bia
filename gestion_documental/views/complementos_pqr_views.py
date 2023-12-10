import ast
import copy
from datetime import datetime
import json
from django.forms import model_to_dict
from rest_framework import generics,status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, NotFound
from django.db import transaction
from gestion_documental.models.radicados_models import PQRSDF, Anexos, Anexos_PQR, ComplementosUsu_PQR, TiposPQR

from gestion_documental.serializers.complementos_pqr_serializers import ComplementoPQRSDFPostSerializer, ComplementoPQRSDFPutSerializer, ComplementosSerializer, PQRSDFSerializer, PersonaSerializer
from gestion_documental.serializers.pqr_serializers import RadicadoPostSerializer
from gestion_documental.views.pqr_views import AnexosCreate, AnexosDelete, AnexosUpdate, RadicadoCreate, Util_PQR
from seguridad.signals.roles_signals import IsAuthenticated
from seguridad.utils import Util
from transversal.models.personas_models import Personas
from transversal.serializers.personas_serializers import PersonasFilterSerializer


class ComplementosPQRSDFGet(generics.ListAPIView):
    serializer_class = ComplementosSerializer
    serializer_class_persona = PersonaSerializer
    serializer_class_pqrsdf = PQRSDFSerializer
    queryset = ComplementosUsu_PQR.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            if request.query_params.get('id_PQRSDF')==None or request.query_params.get('id_persona_titular')==None or request.query_params.get('id_persona_interpone')==None:
                raise ValidationError('No se ingresaron parámetros necesarios para consultar el complemento de PQRSDF')
            
            id_PQRSDF = ast.literal_eval(request.query_params.get('id_PQRSDF', None))
            id_persona_titular = ast.literal_eval(request.query_params.get('id_persona_titular', None))
            id_persona_interpone = ast.literal_eval(request.query_params.get('id_persona_interpone', None))
            
            complementos_PQRSDF = self.queryset.filter(id_PQRSDF = id_PQRSDF)
            data_complementos_pqrsdf = self.set_data_complementos_PQRSDF(id_PQRSDF, id_persona_titular, id_persona_interpone, complementos_PQRSDF)
            return Response({'success':True, 'detail':'Se encontraron los siguientes complementos','data':data_complementos_pqrsdf},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def set_data_complementos_PQRSDF(self, id_PQRSDF, id_persona_titular, id_persona_interpone, complementos_PQRSDF):
        try:
            pqrsdf = PQRSDF.objects.filter(id_PQRSDF = id_PQRSDF).first()
            persona_titular = Personas.objects.filter(id_persona = id_persona_titular).first()
            persona_interpone = Personas.objects.filter(id_persona = id_persona_interpone).first()

            pqrsdf_serializer = self.serializer_class_pqrsdf(pqrsdf, many=False)
            persona_titular_serializer = self.serializer_class_persona(persona_titular, many=False)
            persona_interpone_serializer = self.serializer_class_persona(persona_interpone, many=False)
            complementos_serializer = self.serializer_class(complementos_PQRSDF, many=True)

            return {
                'pqrsdf': pqrsdf_serializer.data,
                'persona_titular': persona_titular_serializer.data,
                'persona_interpone': persona_interpone_serializer.data,
                'complementos_PQRSDF': complementos_serializer.data,
            }
        except Exception as e:
            raise({'success': False, 'detail': str(e)})



class ComplementoPQRSDFCreate(generics.CreateAPIView):
    serializer_class = ComplementoPQRSDFPostSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        try:
            with transaction.atomic():
                data_complemento_pqrsdf = json.loads(request.data.get('complemento_pqrsdf', ''))
                isCreateForWeb = ast.literal_eval(request.data.get('isCreateForWeb', ''))
                id_persona_guarda = ast.literal_eval(request.data.get('id_persona_guarda', ''))

                fecha_actual = datetime.now()
                valores_creados_detalles = []

                util_PQR = Util_PQR()
                anexos = util_PQR.set_archivo_in_anexo(data_complemento_pqrsdf['anexos'], request.FILES, "create")

                #Crea el pqrsdf
                data_complemento_PQRSDF_creado = self.create_complemento_pqrsdf(data_complemento_pqrsdf, fecha_actual, id_persona_guarda, isCreateForWeb)

                #Guarda los anexos en la tabla T258 y la relación entre los anexos y el PQRSDF en la tabla T259 si tiene anexos
                if anexos:
                    anexosCreate = AnexosCreate()
                    valores_creados_detalles = anexosCreate.create_anexos_pqrsdf(anexos, None, data_complemento_PQRSDF_creado['idComplementoUsu_PQR'], isCreateForWeb, fecha_actual)
                    update_requiere_digitalizacion = all(anexo.get('ya_digitalizado', False) for anexo in anexos)
                    if update_requiere_digitalizacion:
                        data_complemento_PQRSDF_creado = self.update_requiereDigitalizacion_pqrsdf(data_complemento_PQRSDF_creado)

                #Auditoria
                descripcion_auditoria = self.set_descripcion_auditoria(data_complemento_PQRSDF_creado)
                self.auditoria(request, descripcion_auditoria, isCreateForWeb, valores_creados_detalles)

                return Response({'success':True, 'detail':'Se creo el complemento de PQRSDF correctamente', 'data':data_complemento_PQRSDF_creado}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def create_complemento_pqrsdf(self, data, fecha_actual, id_persona_guarda, isCreateForWeb):
        data_complemento_pqrsdf = self.set_data_complemento_pqrsdf(data, fecha_actual, id_persona_guarda, isCreateForWeb)
        serializer = self.serializer_class(data=data_complemento_pqrsdf)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.data
    
    def update_requiereDigitalizacion_pqrsdf(self, data_complemento_PQRSDF_creado):
        complementoPQRSDFUpdate = ComplementoPQRSDFUpdate()
        complemento_pqr_instance = ComplementosUsu_PQR.objects.filter(idComplementoUsu_PQR = data_complemento_PQRSDF_creado['idComplementoUsu_PQR']).first()
        data_complemento_pqrsdf_update = copy.copy(data_complemento_PQRSDF_creado)
        data_complemento_pqrsdf_update['requiere_digitalizacion'] = False
        complemento_pqrsdf_update = complementoPQRSDFUpdate.update_complemento_pqrsdf(complemento_pqr_instance, data_complemento_pqrsdf_update)
        return complemento_pqrsdf_update
    
    def set_data_complemento_pqrsdf(self, data, fecha_actual, id_persona_guarda, isCreateForWeb):
        data['fecha_complemento'] = fecha_actual
        data['id_persona_recibe'] = None if isCreateForWeb else id_persona_guarda
        data['requiere_digitalizacion'] = True if data['cantidad_anexos'] != 0 else False
    
        return data
    
    def set_descripcion_auditoria(self, complemento_PQRSDF):
        pqrsdf = PQRSDF.objects.filter(id_PQRSDF = complemento_PQRSDF['id_PQRSDF']).first()
        tipo_pqrsdf = TiposPQR.objects.filter(cod_tipo_pqr=pqrsdf.cod_tipo_PQRSDF).first()

        #Persona interpone
        persona_interpone = Personas.objects.filter(id_persona = complemento_PQRSDF['id_persona_interpone']).first()
        persona_interpone_serializer = PersonasFilterSerializer(persona_interpone)
        nombre_persona_interpone = persona_interpone_serializer.data['nombre_completo'] if persona_interpone_serializer.data['tipo_persona'] == 'N' else persona_interpone_serializer.data['razon_social']
        
        #Persona titular
        persona = Personas.objects.filter(id_persona = pqrsdf.id_persona_titular_id).first()
        persona_serializer = PersonasFilterSerializer(persona)
        nombre_persona_titular = persona_serializer.data['nombre_completo'] if persona_serializer.data['tipo_persona'] == 'N' else persona_serializer.data['razon_social']

        data = {}
        if complemento_PQRSDF['id_PQRSDF']:
            data['IdPQRSDF'] = str(complemento_PQRSDF['id_PQRSDF'])
        else:
            data['IdSolicitudUsuPQR'] = str(complemento_PQRSDF['id_solicitud_usu_PQR'])

        data['NombrePersonaInterpone'] = str(nombre_persona_interpone)
        data['FechaComplemento'] = str(complemento_PQRSDF['fecha_complemento'])
        data['TipoPQRSDF'] = str(tipo_pqrsdf.nombre)
        data['NombrePersonaTitular'] = str(nombre_persona_titular)

        return data

    def auditoria(self, request, descripcion_auditoria, isCreateForWeb, valores_creados_detalles):
        # AUDITORIA
        direccion = Util.get_client_ip(request)
        descripcion = descripcion_auditoria
        auditoria_data = {
            "id_usuario": request.user.id_usuario,
            "id_modulo": 171 if isCreateForWeb else 162,
            "cod_permiso": 'AC' if isCreateForWeb else 'CR',
            "subsistema": 'GEST',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_creados_detalles": valores_creados_detalles
        }
        Util.save_auditoria_maestro_detalle(auditoria_data)
    

class ComplementoPQRSDFUpdate(generics.RetrieveUpdateAPIView):
    serializer_class = ComplementoPQRSDFPutSerializer
    queryset = ComplementosUsu_PQR.objects.all()
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def put(self, request):
        try:
            with transaction.atomic():
                #Obtiene los datos enviado en el request
                complemento_pqrsdf = json.loads(request.data.get('complemento_pqrsdf', ''))
                isCreateForWeb = ast.literal_eval(request.data.get('isCreateForWeb', ''))

                complemento_pqrsdf_db = self.queryset.filter(idComplementoUsu_PQR = complemento_pqrsdf['idComplementoUsu_PQR']).first()
                if complemento_pqrsdf_db:
                    anexos = complemento_pqrsdf['anexos']
                    fecha_actual = datetime.now()

                    #Actualiza los anexos y los metadatos
                    data_auditoria_anexos = self.procesa_anexos(anexos, request.FILES, complemento_pqrsdf['idComplementoUsu_PQR'], isCreateForWeb, fecha_actual)
                    update_requiere_digitalizacion = all(anexo.get('ya_digitalizado', False) for anexo in anexos)
                    complemento_pqrsdf['requiere_digitalizacion'] = False if update_requiere_digitalizacion else True
                    
                    #Actuaiza pqrsdf
                    pqrsdf_update = self.update_complemento_pqrsdf(complemento_pqrsdf_db, complemento_pqrsdf)

                    #Auditoria
                    descripcion_auditoria = self.set_descripcion_auditoria(pqrsdf_update)
                    self.auditoria(request, descripcion_auditoria, isCreateForWeb, data_auditoria_anexos)
                    
                    return Response({'success':True, 'detail':'Se editó el complemento de PQRSDF correctamente', 'data': pqrsdf_update}, status=status.HTTP_201_CREATED)
                else:
                    return Response({'success':False, 'detail':'No se encontró el complemento de PQRSDF para actualizar'}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def update_complemento_pqrsdf(self, complemento_pqrsdf_db, complemento_pqrsdf_update):
        try:
            serializer = self.serializer_class(complemento_pqrsdf_db, data=complemento_pqrsdf_update)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return serializer.data
        except Exception as e:
            raise({'success': False, 'detail': str(e)})
        
    def procesa_anexos(self, anexos, archivos, idComplementoUsu_PQR, isCreateForWeb, fecha_actual):
        data_auditoria_create = []
        data_auditoria_update = []
        data_auditoria_delete = []

        anexos = [] if not anexos else anexos
        nombres_anexos = [anexo['nombre_anexo'] for anexo in anexos]
        # Validar que no haya valores repetidos
        if len(nombres_anexos) != len(set(nombres_anexos)):
            raise ValidationError("error': 'No se permiten nombres de anexos repetidos.")

        anexos_pqr_DB = Anexos_PQR.objects.filter(id_complemento_usu_PQR = idComplementoUsu_PQR)
        if anexos_pqr_DB:
            util_PQR = Util_PQR()
            data_anexos_create = [anexo for anexo in anexos if anexo['id_anexo'] == None]
            anexos_create = util_PQR.set_archivo_in_anexo(data_anexos_create, archivos, "create")
            
            data_anexos_update = [anexo for anexo in anexos if not anexo['id_anexo'] == None]
            anexos_update = util_PQR.set_archivo_in_anexo(data_anexos_update, archivos, "update")

            ids_anexos_update = [anexo_update['id_anexo'] for anexo_update in anexos_update]
            anexos_delete = [anexo_pqr for anexo_pqr in anexos_pqr_DB if getattr(anexo_pqr,'id_anexo_id') not in ids_anexos_update]

            anexosCreate = AnexosCreate()
            anexosUpdate = AnexosUpdate()
            anexosDelete = AnexosDelete()

            data_auditoria_create = anexosCreate.create_anexos_pqrsdf(anexos_create, None, idComplementoUsu_PQR, isCreateForWeb, fecha_actual)
            data_auditoria_update = anexosUpdate.put(anexos_update, fecha_actual)
            data_auditoria_delete = anexosDelete.delete(anexos_delete)
            
        else:
            anexosCreate = AnexosCreate()
            util_PQR = Util_PQR()
            anexos_create = util_PQR.set_archivo_in_anexo(anexos, archivos, "create")
            data_auditoria_create = anexosCreate.create_anexos_pqrsdf(anexos_create, None, idComplementoUsu_PQR, isCreateForWeb, fecha_actual)

        return {
            'data_auditoria_create': data_auditoria_create,
            'data_auditoria_update': data_auditoria_update,
            'data_auditoria_delete': data_auditoria_delete
        }
    
    def set_descripcion_auditoria(self, complemento_PQRSDF):
        pqrsdf = PQRSDF.objects.filter(id_PQRSDF = complemento_PQRSDF['id_PQRSDF']).first()
        tipo_pqrsdf = TiposPQR.objects.filter(cod_tipo_pqr=pqrsdf.cod_tipo_PQRSDF).first()

        #Persona interpone
        persona_interpone = Personas.objects.filter(id_persona = complemento_PQRSDF['id_persona_interpone']).first()
        persona_interpone_serializer = PersonasFilterSerializer(persona_interpone)
        nombre_persona_interpone = persona_interpone_serializer.data['nombre_completo'] if persona_interpone_serializer.data['tipo_persona'] == 'N' else persona_interpone_serializer.data['razon_social']
        
        #Persona titular
        persona = Personas.objects.filter(id_persona = pqrsdf.id_persona_titular_id).first()
        persona_serializer = PersonasFilterSerializer(persona)
        nombre_persona_titular = persona_serializer.data['nombre_completo'] if persona_serializer.data['tipo_persona'] == 'N' else persona_serializer.data['razon_social']

        data = {}
        if complemento_PQRSDF['id_PQRSDF']:
            data['IdPQRSDF'] = str(complemento_PQRSDF['id_PQRSDF'])
        else:
            data['IdSolicitudUsuPQR'] = str(complemento_PQRSDF['id_solicitud_usu_PQR'])

        data['NombrePersonaInterpone'] = str(nombre_persona_interpone)
        data['FechaComplemento'] = str(complemento_PQRSDF['fecha_complemento'])
        data['TipoPQRSDF'] = str(tipo_pqrsdf.nombre)
        data['NombrePersonaTitular'] = str(nombre_persona_titular)

        return data

    def auditoria(self, request, descripcion_auditoria, isCreateForWeb, valores_detalles):
        # AUDITORIA
        direccion = Util.get_client_ip(request)
        descripcion = descripcion_auditoria
        auditoria_data = {
            "id_usuario": request.user.id_usuario,
            "id_modulo": 171 if isCreateForWeb else 162,
            "cod_permiso": 'AC',
            "subsistema": 'GEST',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_actualizados_detalles": valores_detalles['data_auditoria_update'],
            "valores_creados_detalles": valores_detalles['data_auditoria_create'],
            "valores_eliminados_detalles": valores_detalles['data_auditoria_delete']
        }
        Util.save_auditoria_maestro_detalle(auditoria_data)

class ComplementoPQRSDFDelete(generics.RetrieveDestroyAPIView):
    queryset = ComplementosUsu_PQR.objects.all()
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def delete(self, request):
        try:
            with transaction.atomic():
                if request.query_params.get('idComplementoUsu_PQR')==None or request.query_params.get('isCreateForWeb')==None:
                    raise ValidationError('No se ingresaron parámetros necesarios para eliminar el complemento de PQRSDF')
                idComplementoUsu_PQR = int(request.query_params.get('idComplementoUsu_PQR', 0))
                isCreateForWeb = ast.literal_eval(request.query_params.get('isCreateForWeb', False))

                valores_eliminados_detalles = []
                complemento_pqrsdf_delete = self.queryset.filter(idComplementoUsu_PQR = idComplementoUsu_PQR).first()
                if complemento_pqrsdf_delete:
                    if not complemento_pqrsdf_delete.id_radicado:
                        #Elimina los anexos, anexos_pqr, metadatos y el archivo adjunto
                        anexos_pqr = Anexos_PQR.objects.filter(id_complemento_usu_PQR = idComplementoUsu_PQR)
                        if anexos_pqr:
                            anexosDelete = AnexosDelete()
                            valores_eliminados_detalles = anexosDelete.delete(anexos_pqr)
                            #Elimina el pqrsdf
                            complemento_pqrsdf_delete.delete()
                            #Auditoria
                            descripcion_auditoria = self.set_descripcion_auditoria(complemento_pqrsdf_delete)
                            self.auditoria(request, descripcion_auditoria, isCreateForWeb, valores_eliminados_detalles)

                        return Response({'success':True, 'detail':'El complemento de PQRSDF ha sido descartado'}, status=status.HTTP_200_OK)
                    else:
                        raise NotFound('No se permite borrar complementos de pqrsdf ya radicados')
                else:
                    raise NotFound('No se encontró ningún complemento de pqrsdf con estos parámetros')
        
        except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def set_descripcion_auditoria(self, complemento_PQRSDF):
        pqrsdf = PQRSDF.objects.filter(id_PQRSDF = complemento_PQRSDF.id_PQRSDF_id).first()
        tipo_pqrsdf = TiposPQR.objects.filter(cod_tipo_pqr=pqrsdf.cod_tipo_PQRSDF).first()

        #Persona interpone
        persona_interpone = Personas.objects.filter(id_persona = complemento_PQRSDF.id_persona_interpone_id).first()
        persona_interpone_serializer = PersonasFilterSerializer(persona_interpone)
        nombre_persona_interpone = persona_interpone_serializer.data['nombre_completo'] if persona_interpone_serializer.data['tipo_persona'] == 'N' else persona_interpone_serializer.data['razon_social']
        
        #Persona titular
        persona = Personas.objects.filter(id_persona = pqrsdf.id_persona_titular_id).first()
        persona_serializer = PersonasFilterSerializer(persona)
        nombre_persona_titular = persona_serializer.data['nombre_completo'] if persona_serializer.data['tipo_persona'] == 'N' else persona_serializer.data['razon_social']

        data = {}
        if complemento_PQRSDF.id_PQRSDF:
            data['IdPQRSDF'] = str(complemento_PQRSDF.id_PQRSDF_id)
        else:
            data['IdSolicitudUsuPQR'] = str(complemento_PQRSDF.id_solicitud_usu_PQR_id)

        data['NombrePersonaInterpone'] = str(nombre_persona_interpone)
        data['FechaComplemento'] = str(complemento_PQRSDF.fecha_complemento)
        data['TipoPQRSDF'] = str(tipo_pqrsdf.nombre)
        data['NombrePersonaTitular'] = str(nombre_persona_titular)

        return data
    
    def auditoria(self, request, descripcion_auditoria, isCreateForWeb, valores_eliminados_detalles):
        # AUDITORIA
        direccion = Util.get_client_ip(request)
        descripcion = descripcion_auditoria
        auditoria_data = {
            "id_usuario": request.user.id_usuario,
            "id_modulo": 171 if isCreateForWeb else 162,
            "cod_permiso": 'BO',
            "subsistema": 'GEST',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_eliminados_detalles": valores_eliminados_detalles
        }
        Util.save_auditoria_maestro_detalle(auditoria_data) 
        
class RadicarComplementoPQRSDF(generics.CreateAPIView):
    serializer_class = RadicadoPostSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        try:
            with transaction.atomic():
                id_complemento_PQRSDF = request.data['id_complemento_PQRSDF']
                id_persona_guarda = request.data['id_persona_guarda']
                isCreateForWeb = request.data['isCreateForWeb']
                data_radicado_pqrsdf = self.radicar_pqrsdf(request, id_complemento_PQRSDF, id_persona_guarda, isCreateForWeb)
                return Response({'success':True, 'detail':'Se creo el radicado para el complemento PQRSDF', 'data': data_radicado_pqrsdf}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    def radicar_pqrsdf(self, request, id_complemento_PQRSDF, id_persona_guarda, isCreateForWeb):
        fecha_actual = datetime.now()
        complemento_pqr_instance = ComplementosUsu_PQR.objects.filter(idComplementoUsu_PQR = id_complemento_PQRSDF).first()
        previous_instance = copy.copy(complemento_pqr_instance)
        
        #Crea el radicado
        data_for_create = {}
        data_for_create['fecha_actual'] = fecha_actual
        data_for_create['id_usuario'] = id_persona_guarda
        data_for_create['tipo_radicado'] = "E"
        data_for_create['modulo_radica'] = "Complemento del Titular a una PQRSDF"
        radicadoCreate = RadicadoCreate()
        data_radicado = radicadoCreate.post(data_for_create)

        #Actualiza el estado y la data del radicado al PQRSDF
        complementoPQRSDFUpdate = ComplementoPQRSDFUpdate()
        complemento_pqrsdf_dic = model_to_dict(complemento_pqr_instance)
        complemento_pqrsdf_update = self.set_data_update_radicado(complemento_pqrsdf_dic, data_radicado)
        complementoPQRSDFUpdate.update_complemento_pqrsdf(complemento_pqr_instance, complemento_pqrsdf_update)

        # #Auditoria
        descripciones = self.set_descripcion_auditoria(previous_instance, complemento_pqr_instance)
        self.auditoria(request, descripciones['descripcion'], isCreateForWeb, descripciones['data_auditoria_update'])
        
        return data_radicado
    
    def set_data_update_radicado(self, complemento_pqrsdf, data_radicado):
        complemento_pqrsdf['id_radicado'] = data_radicado['id_radicado']
        complemento_pqrsdf['fecha_radicado'] = data_radicado['fecha_radicado']

        return complemento_pqrsdf
    
    def set_descripcion_auditoria(self, previous_complemento_pqrsdf, complemento_pqrsdf_update):
        descripcion_auditoria_update = {
            'IdRadicado': previous_complemento_pqrsdf.id_radicado,
            'FechaRadicado': previous_complemento_pqrsdf.fecha_radicado
        }

        data_auditoria_update = {'previous':previous_complemento_pqrsdf, 'current':complemento_pqrsdf_update}

        data = {
            'descripcion': descripcion_auditoria_update,
            'data_auditoria_update': data_auditoria_update
        }

        return data

    def auditoria(self, request, descripcion, isCreateForWeb, valores_actualizados):
        # AUDITORIA
        direccion = Util.get_client_ip(request)
        auditoria_data = {
            "id_usuario" : request.user.id_usuario,
            "id_modulo" : 171 if isCreateForWeb else 162,
            "cod_permiso": "AC",
            "subsistema": 'GEST',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_actualizados": valores_actualizados
        }
        Util.save_auditoria(auditoria_data)