
import copy
from datetime import datetime
import hashlib
import os
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from rest_framework import generics,status
from rest_framework.permissions import IsAuthenticated
from gestion_documental.models.radicados_models import PQRSDF, Anexos, Anexos_PQR, EstadosSolicitudes, InfoDenuncias_PQRSDF, MediosSolicitud, MetadatosAnexosTmp, TiposPQR, modulos_radican
from rest_framework.response import Response
from gestion_documental.models.trd_models import FormatosTiposMedio
from gestion_documental.serializers.pqr_serializers import AnexosPQRSDFPostSerializer, AnexosPQRSDFSerializer, AnexosPostSerializer, AnexosSerializer, InfoDenunciasPQRSDFPostSerializer, InfoDenunciasPQRSDFSerializer, MediosSolicitudCreateSerializer, MediosSolicitudDeleteSerializer, MediosSolicitudSearchSerializer, MediosSolicitudUpdateSerializer, MetadatosPostSerializer, MetadatosSerializer, PQRSDFPostSerializer, PQRSDFPutSerializer, PQRSDFSerializer, RadicadoPostSerializer, TiposPQRGetSerializer, TiposPQRUpdateSerializer
from gestion_documental.views.archivos_digitales_views import ArchivosDgitalesCreate
from gestion_documental.views.configuracion_tipos_radicados_views import ConfigTiposRadicadoAgnoGenerarN
from gestion_documental.views.panel_ventanilla_views import Estados_PQRCreate, Estados_PQRDelete
from seguridad.utils import Util

from django.db.models import Q
from django.db import transaction
class TiposPQRGet(generics.ListAPIView):
    serializer_class = TiposPQRGetSerializer
    queryset = TiposPQR.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,pk):

        instance=TiposPQR.objects.filter(cod_tipo_pqr=pk)
        if not instance:
            raise NotFound("No existen tipos de radicado")
        
        serializer = self.serializer_class(instance, many=True)

                         
        return Response({'succes':True, 'detail':'Se encontró los siguientes registross','data':serializer.data}, status=status.HTTP_200_OK)


class TiposPQRUpdate(generics.UpdateAPIView):
    serializer_class = TiposPQRUpdateSerializer
    queryset = TiposPQR.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self,request,pk):
    
        try:    
            data = request.data
            instance = TiposPQR.objects.filter(cod_tipo_pqr=pk).first()
            
            if not instance:
                raise NotFound("No se existe un tipo de radicado con este codigo.")
            
            instance_previous=copy.copy(instance)
            serializer = self.serializer_class(instance,data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            
            serializer.save()

            #AUDITORIA 
            usuario = request.user.id_usuario
            direccion=Util.get_client_ip(request)
            descripcion = {"Nombre":instance.nombre}
            valores_actualizados = {'current': instance, 'previous': instance_previous}
            auditoria_data = {
                    "id_usuario" : usuario,
                    "id_modulo" : 153,
                    "cod_permiso": "AC",
                    "subsistema": 'GEST',
                    "dirip": direccion,
                    "descripcion": descripcion, 
                    "valores_actualizados": valores_actualizados
                }
            Util.save_auditoria(auditoria_data) 

            return Response({'success':True,'detail':"Se actualizo la actividad Correctamente.","data":serializer.data},status=status.HTTP_200_OK)
        
        except ValidationError  as e:
            error_message = {'error': e.detail}
            raise ValidationError  (e.detail)    

class GetPQRSDFForStatus(generics.ListAPIView):
    serializer_class = PQRSDFSerializer
    queryset = PQRSDF.objects.all()

    def get(self, request, id_persona_titular):
        pqrsdf = self.queryset.filter(Q(id_persona_titular = id_persona_titular) & 
                                      Q(Q(id_radicado = 0) | Q(id_radicado = None) | Q(~Q(id_radicado=0) & Q(requiere_rta = True) & Q(fecha_rta_final_gestion = None))))
        if pqrsdf:
            serializador = self.serializer_class(pqrsdf, many = True)
            return Response({'success':True, 'detail':'Se encontraron PQRSDF asociadas al titular','data':serializador.data},status=status.HTTP_200_OK)
        else:
            return Response({'success':True, 'detail':'No se encontraron PQRSDF asociadas al titular'},status=status.HTTP_200_OK) 


class PQRSDFCreate(generics.CreateAPIView):
    serializer_class = PQRSDFPostSerializer

    @transaction.atomic
    def post(self, request):
        try:
            with transaction.atomic():
                #Setea datos para modelos
                data_pqrsdf = request.data['pqrsdf']
                id_persona_guarda = request.data['id_persona_guarda']
                isCreateForWeb = request.data['isCreateForWeb']
                debe_radicar = isCreateForWeb and data_pqrsdf['es_anonima']
                denuncia = data_pqrsdf['denuncia']
                anexos = data_pqrsdf['anexos']

                #Crea el pqrsdf
                data_PQRSDF_creado = self.create_pqrsdf(data_pqrsdf)

                #Guarda el nuevo estado Guardado en la tabla T255
                HistoricoEstadosCreate.create_historico_estado(data_PQRSDF_creado, 'GUARDADO', id_persona_guarda)
                
                #Crea la denuncia si el tipo del PQRSDF es de tipo Denuncia
                if(data_pqrsdf['cod_tipo_PQRSDF'] == "D"):
                    DenunciasCreate.crear_denuncia(denuncia, data_pqrsdf['id_PQRSDF'])

                #Guarda los anexos en la tabla T258 y la relación entre los anexos y el PQRSDF en la tabla T259 si tiene anexos
                if anexos:
                    AnexosCreate.create_anexos_pqrsdf(anexos, data_PQRSDF_creado, isCreateForWeb)
                    update_requiere_digitalizacion = all(anexo.ya_digitalizado for anexo in anexos)
                    if update_requiere_digitalizacion:
                        data_PQRSDF_creado['requiereDigitalizacion'] = False
                        data_PQRSDF_creado = PQRSDFUpdate.put(data_PQRSDF_creado)

                #Si tiene que radicar, crea el radicado
                if debe_radicar:
                    request_radicado = {
                        'pqrsdf': data_PQRSDF_creado,
                        'id_persona_guarda': id_persona_guarda
                    }
                    data_PQRSDF_creado = RadicarPQRSDF.post(request_radicado)
                
                return Response({'success':True, 'detail':'Se creo el PQRSDF correctamente', 'data':data_PQRSDF_creado}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
      
    def create_pqrsdf(self, data):
        data_pqrsdf = self.set_data_pqrsdf(data)
        serializer = self.get_serializer(data=data_pqrsdf)
        serializer.is_valid(raise_exception=True)
        serializador = serializer.save()
        data_PQRSDF_creado = serializador.data
        return data_PQRSDF_creado

    def set_data_pqrsdf(self, data):
        data['fecha_registro'] = data['fecha_ini_estado_actual'] = datetime.now()
        data['requiereDigitalizacion'] = True if data['cantidad_anexos'] != 0 else False
    
        estado = EstadosSolicitudes.objects.filter(nombre='GUARDADO').first()
        data['id_estado_actual_solicitud'] = estado.id_estado_solicitud
    
        return data


class PQRSDFUpdate(generics.RetrieveUpdateAPIView):
    serializer_class = PQRSDFPutSerializer

    @transaction.atomic
    def put(self, request):
        try:
            with transaction.atomic():
                pqrsdf = PQRSDF.objects.filter(id_PQRSDF=request.data.id_PQRSDF)
                if(pqrsdf):
                    serializer = self.serializer_class(data=request.data, many=False)
                    serializer.is_valid(raise_exception=True)
                    serializador = serializer.save()
                    return Response({'success':True, 'detail':'Se creo el PQRSDF correctamente', 'data':serializador.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response({'success':False, 'detail':'No se encontro el PQRSDF para actualizar'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class PQRSDFDelete(generics.RetrieveDestroyAPIView):
    serializer_class = PQRSDFSerializer
    borrar_estados = Estados_PQRDelete
    queryset = PQRSDF.objects.all()

    @transaction.atomic
    def delete(self, request):
        try:
            with transaction.atomic():
                pqrsdf_delete = self.queryset.filter(id_PQRSDF = request.data['id_PQRSDF'])
                if pqrsdf_delete:
                    #Elimina los anexos, anexos_pqr, metadatos y el archivo adjunto
                    if request.data['anexos']:
                        AnexosDelete.delete(request.data['anexos'])

                    #Elimina el estado creado en el historico
                    self.borrar_estados.delete(request.data['id_PQRSDF'])
                    #Elimina la denuncia en caso de que se tenga una denuncia asociada al pqrsdf
                    DenunciasDelete.delete(request.data['id_PQRSDF'])
                    #Elimina el pqrsdf
                    pqrsdf_delete.delete()

                    return Response({'success':True, 'detail':'El PQRSDF ha sido descartado'}, status=status.HTTP_200_OK)
                else:
                    raise NotFound('No se encontró ningún pqrsdf con estos parámetros')
            
        except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        
########################## Historico Estados ##########################
class HistoricoEstadosCreate(generics.CreateAPIView):
    creador_estados = Estados_PQRCreate

    def create_historico_estado(self, data_PQRSDF, nombre_estado, id_persona_guarda):
        data_estado_crear = self.set_data_estado(data_PQRSDF, nombre_estado, id_persona_guarda)
        self.creador_estados.crear_estado(data_estado_crear)

    def set_data_estado(self, data_PQRSDF, nombre_estado, id_persona_guarda):
        data_estado = {}
        data_estado['PQRSDF'] = data_PQRSDF.id_PQRSDF
        data_estado['fecha_iniEstado'] = data_PQRSDF.fecha_ini_estado_actual
        data_estado['persona_genera_estado'] = None if id_persona_guarda == 0 else id_persona_guarda #TODO: TENER EN CUENTA QUE TALVES ESTE DATO NO PUEDA SER NULL

        estado = EstadosSolicitudes.objects.filter(nombre=nombre_estado).first()
        data_estado['estado_solicitud'] = estado.id_estado_solicitud

        return data_estado

########################## RADICADOS ##########################
class RadicarPQRSDF(generics.CreateAPIView):
    serializer_class = RadicadoPostSerializer
    
    @transaction.atomic
    def post(self, request):
        try:
            with transaction.atomic():
                data_PQRSDF_creado = request.data['pqrsdf']
                id_persona_guarda = request.data['id_persona_guarda']
                fecha_actual = datetime.now()

                #Obtiene los dias para la respuesta del PQRSDF
                tipo_pqr = self.get_tipos_pqr(data_PQRSDF_creado['cod_tipo_PQRSDF'])
                dias_respuesta = tipo_pqr.tiempo_respuesta_en_dias
                
                #Crea el radicado
                data_for_create = {}
                data_for_create['fecha_actual'] = fecha_actual
                data_for_create['id_usuario'] = id_persona_guarda
                data_for_create['tipo_radicado'] = "E"
                data_for_create['modulo_radica'] = "PQRSDF"
                data_radicado = RadicadoCreate.post(data_for_create)

                #Actualiza el estado y la data del radicado al PQRSDF
                data_update_pqrsdf = self.set_data_update_radicado_pqrsdf(data_PQRSDF_creado, data_radicado, dias_respuesta, fecha_actual)
                data_PQRSDF_creado = PQRSDFUpdate.put(data_update_pqrsdf)

                #Guarda el nuevo estado Radicado en la tabla T255
                HistoricoEstadosCreate.create_historico_estado(data_PQRSDF_creado, 'RADICADO', id_persona_guarda)

                response = {
                    'radicado': data_radicado,
                    'pqrsdf': data_PQRSDF_creado
                }

                return Response({'success':True, 'detail':'Se creo el radicado para el PQRSDF', 'data': response}, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get_tipos_pqr(self, cod_tipo_PQRSDF):
        tipo_pqr = TiposPQR.objects.filter(cod_tipo_pqr=cod_tipo_PQRSDF).first()
        if tipo_pqr.tiempo_respuesta_en_dias == None:
            raise ValidationError("No se encuentra configurado el numero de dias para la respuesta. La entidad debe configurar todos los días de respuesta para todas las PQRSDF para realizar el proceso creación.")
        return tipo_pqr
    
    def set_data_update_radicado_pqrsdf(self, pqrsdf, data_radicado, dias_respuesta, fecha_actual):
        pqrsdf['id_radicado'] = data_radicado.id_radicado
        pqrsdf['fecha_radicado'] = data_radicado.fecha_radicado
        pqrsdf['dias_para_respuesta'] = dias_respuesta

        estado = EstadosSolicitudes.objects.filter(nombre='RADICADO').first()
        pqrsdf['id_estado_actual_solicitud'] = estado.id_estado_solicitud
        pqrsdf['fecha_ini_estado_actual'] = fecha_actual

        return pqrsdf

class RadicadoCreate(generics.CreateAPIView):
    serializer_class = RadicadoPostSerializer
    config_radicados = ConfigTiposRadicadoAgnoGenerarN
    
    def post(self, request):
        try:
            with transaction.atomic():
                config_tipos_radicado = self.get_config_tipos_radicado(request)
                radicado_data = self.set_data_radicado(config_tipos_radicado, request.fecha_actual, request.id_usuario, request.modulo_radica)
                serializer = self.get_serializer(data=radicado_data)
                serializer.is_valid(raise_exception=True)
                serializador = serializer.save()
                return Response({'success':True, 'detail':'Se creo el radicado correctamente', 'data':serializador.data}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': 'Ocurrió un error durante la transacción.'}, status=500)


    def get_config_tipos_radicado(self, request):
        data_request = {
            'user': { 'persona': { 'id_persona': request.id_usuario } },
            'cod_tipo_radicado': request.tipo_radicado,
            'fecha_actual': request.fecha_actual
        }
        config_tipos_radicados = self.config_radicados.put(self, data_request)
        config_tipos_radicado_data = config_tipos_radicados.data
        if config_tipos_radicado_data.implementar == False:
            raise ValidationError("El sistema requiere que se maneje un radicado de entrada o unico, debe solicitar al administrador del sistema la configuración del radicado")
        else:
            return config_tipos_radicado_data
        
    def set_data_radicado(self, config_tipos_radicado, fecha_actual, id_usuario, modulo_radica):
        radicado = {}
        radicado['cod_tipo_radicado'] = config_tipos_radicado.cod_tipo_radicado
        radicado['prefijo_radicado'] = config_tipos_radicado.prefijo_consecutivo
        radicado['agno_radicado'] = config_tipos_radicado.prefijo_consecutivo.agno_radicado
        radicado['nro_radicado'] = config_tipos_radicado.prefijo_consecutivo.consecutivo_actual
        radicado['fecha_radicado'] = fecha_actual
        radicado['id_persona_radica'] = id_usuario

        modulo_radica = modulos_radican.objects.filter(nombre=modulo_radica)
        radicado['id_modulo_que_radica'] = modulo_radica.id_ModuloQueRadica

        return radicado


########################## DENUNCIAS ##########################
class DenunciasCreate(generics.CreateAPIView):
    serializer_class = InfoDenunciasPQRSDFPostSerializer

    def crear_denuncia(self, data_denuncia, id_PQRSDF):
        try:
            with transaction.atomic():
                data_denuncia['id_PQRSDF'] = id_PQRSDF
                data_to_create = self.set_data_metadato(data_denuncia)
                serializer = self.serializer_class(data=data_to_create)
                serializer.is_valid(raise_exception=True)
                serializador = serializer.save()
                return Response({'success':True, 'detail':'Se creo la denuncia correctamente', 'data':serializador.data}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': 'Ocurrió un error durante la transacción.'}, status=500)

class DenunciasDelete(generics.RetrieveAPIView):
    serializer_class = InfoDenunciasPQRSDFSerializer
    queryset = InfoDenuncias_PQRSDF.objects.all()

    @transaction.atomic
    def delete(self, request, id_PQRSDF):
        try:
            with transaction.atomic():
                denuncia = self.queryset.filter(id_PQRSDF = id_PQRSDF).first()
                message = ""
                if denuncia:
                    denuncia.delete()
                    message = "La denuncia ha sido eliminada exitosamente "
                else:
                    message = "No se cuenta con denuncias asociadas al PQRSDF"

                return Response({'success':True, 'detail':message}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)



########################## ANEXOS Y ANEXOS PQR ##########################
class AnexosCreate(generics.CreateAPIView):
    serializer_class = AnexosPostSerializer
    
    def create_anexos_pqrsdf(self, anexos, data_PQRSDF_creado, isCreateForWeb):
        lista_valores = anexos.get('nombre_anexo', [])
        # Validar que no haya valores repetidos
        if len(lista_valores) != len(set(lista_valores)):
            raise ValidationError("error': 'No se permiten nombres de anexos repetidos.")

        for anexo in anexos:
            data_anexo = self.crear_anexo(anexo)

            #Crea la relacion en la tabla T259
            data_anexos_PQR = {}
            data_anexos_PQR['id_PQRSDF'] = data_PQRSDF_creado.id_PQRSDF
            data_anexos_PQR['id_anexo'] = data_anexo.data.id_anexo
            AnexosPQRCreate.crear_anexo_pqr(data_anexos_PQR)

            #Guardar el archivo en la tabla T238
            if anexo.file:
                archivo_creado = self.crear_archivos(anexo.file, data_PQRSDF_creado.fecha_registro)
            else:
                raise ValidationError("No se puede crear anexos sin archivo adjunto")

            #Crea los metadatos del archivo cargado
            data_metadatos = {}
            data_metadatos['metadatos'] = anexo.metadatos
            data_metadatos['anexo'] = data_anexo
            data_metadatos['isCreateForWeb'] = isCreateForWeb
            data_metadatos['fecha_registro'] = data_PQRSDF_creado.fecha_registro
            data_metadatos['id_archivo_digital'] = archivo_creado.data.get('data').get('id_archivo_digital')
            MetadatosPQRCreate.create_metadatos_pqr(data_metadatos)

    def crear_anexo(self, request):
        try:
            with transaction.atomic():
                serializer = self.serializer_class(data=request)
                serializer.is_valid(raise_exception=True)
                serializador = serializer.save()
                return Response({'success':True, 'detail':'Se creo el anexo correctamente', 'data':serializador.data}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': 'Ocurrió un error durante la transacción.'}, status=500)

    def crear_archivos(self, uploaded_file, fecha_creacion):
        #Valida extensión del archivo
        nombre=uploaded_file.name
            
        extension = os.path.splitext(nombre)
        extension_sin_punto = extension[1:] if extension.startswith('.') else extension
        if not extension_sin_punto:
            raise ValidationError("No fue posible registrar el archivo")
        
        formatos=FormatosTiposMedio.objects.filter(nombre=extension_sin_punto,activo=True).first()
        if not formatos:
            raise ValidationError("Este formato "+str(extension_sin_punto)+" de archivo no esta permitido")

        # Obtiene el año actual para determinar la carpeta de destino
        current_year = fecha_creacion.year
        ruta = os.path.join("home", "BIA", "Otros", "GDEA", str(current_year))

        # Calcula el hash MD5 del archivo
        md5_hash = hashlib.md5()
        for chunk in uploaded_file.chunks():
            md5_hash.update(chunk)

        # Obtiene el valor hash MD5
        md5_value = md5_hash.hexdigest()

        # Crea el archivo digital y obtiene su ID
        data_archivo = {
            'es_Doc_elec_archivo': False,
            'ruta': ruta,
            'md5_hash': md5_value  # Agregamos el hash MD5 al diccionario de datos
        }
        
        archivos_Digitales = ArchivosDgitalesCreate()
        respuesta = archivos_Digitales.crear_archivo(data_archivo, uploaded_file)
        return respuesta
    
class AnexosDelete(generics.RetrieveDestroyAPIView):
    serializer_class = AnexosSerializer
    queryset = Anexos.objects.all()

    @transaction.atomic
    def delete(self, request, anexos):
        try:
            with transaction.atomic():
                for anexo in anexos:
                    anexo_delete = self.queryset.filter(id_anexo = anexo.id_anexo).first()
                    if anexo_delete:
                        MetadatosPQRDelete.delete(anexo.id_metadatos_anexo_tmp)
                        AnexosPQRDelete.delete(anexo.id_anexo)
                        anexo_delete.delete()
                    else:
                        raise NotFound('No se encontró ningún anexo con estos parámetros')
                return Response({'success':True, 'detail':'Los anexos han sido eliminados exitosamente'}, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'success': False, 'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class AnexosPQRCreate(generics.CreateAPIView):
    serializer_class = AnexosPQRSDFPostSerializer
    
    def crear_anexo_pqr(self, request):
        try:
            with transaction.atomic():
                serializer = self.serializer_class(data=request)
                serializer.is_valid(raise_exception=True)
                serializador = serializer.save()
                return Response({'success':True, 'detail':'Se creo el anexo pqr correctamente', 'data':serializador.data}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': 'Ocurrió un error durante la transacción.'}, status=500)
        
class AnexosPQRDelete(generics.RetrieveDestroyAPIView):
    serializer_class = AnexosPQRSDFSerializer
    queryset = Anexos_PQR.objects.all()

    @transaction.atomic
    def delete(self, request, id_anexo):
        with transaction.atomic():
            anexoPqr = self.queryset.filter(id_anexo = id_anexo).first()
            if anexoPqr:
                anexoPqr.delete()
                return Response({'success':True, 'detail':'El anexo pqr ha sido eliminado exitosamente'}, status=status.HTTP_200_OK)
            else:
                raise NotFound('No se encontró ningún anexo pqr asociado al anexo')

########################## METADATOS ##########################   
class MetadatosPQRCreate(generics.CreateAPIView):
    serializer_class = MetadatosPostSerializer

    def create_metadatos_pqr(self, data_metadatos):
        try:
            with transaction.atomic():
                data_to_create = self.set_data_metadato(data_metadatos)
                serializer = self.serializer_class(data=data_to_create)
                serializer.is_valid(raise_exception=True)
                serializador = serializer.save()
                return Response({'success':True, 'detail':'Se creo el metadato del anexo correctamente', 'data':serializador.data}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': 'Ocurrió un error durante la transacción.'}, status=500)
        
    def set_data_metadato(self, data_metadatos):
        metadato = {}
        anexo = data_metadatos.anexo
        data_metadato = data_metadatos.metadatos

        if data_metadatos.isCreateForWeb:
            metadato['fecha_creacion_doc'] = data_metadatos.fecha_registro
            metadato['cod_origen_archivo'] = data_metadato.cod_origen_archivo
            metadato['es_version_original'] = True
            metadato['id_archivo_sistema'] = data_metadato.id_archivo_digital
        else:
            data_metadato['id_anexo'] = anexo.id_anexo
            data_metadato['fecha_creacion_doc'] = data_metadatos.fecha_registro
            data_metadato['nro_folios_documento'] = anexo.numero_folios
            metadato['es_version_original'] = True
            data_metadato['id_archivo_sistema'] = data_metadato.id_archivo_digital
            metadato = data_metadato
        
        return metadato
    

class MetadatosPQRDelete(generics.RetrieveDestroyAPIView):
    serializer_class = MetadatosSerializer
    queryset = MetadatosAnexosTmp.objects.all()

    @transaction.atomic
    def delete(self, request, id_metadato):
        with transaction.atomic():
            metadato = self.queryset.filter(id_metadatos_anexo_tmp = id_metadato).first()
            if metadato:
                #TODO: Averiguar como se puede borrar un archivo, porque no se encuentra el metodo para ello
                metadato.delete()
                return Response({'success':True, 'detail':'El metadato ha sido eliminado exitosamente'}, status=status.HTTP_200_OK)
            else:
                raise NotFound('No se encontró ningún metadato con estos parámetros')

 ########################## MEDIOS DE SOLICITUD ##########################


#CREAR_MEDIOS_SOLICITUD
class MediosSolicitudCreate(generics.CreateAPIView):
    queryset = MediosSolicitud.objects.all()
    serializer_class = MediosSolicitudCreateSerializer
    permission_classes = [IsAuthenticated]


#BUSCAR_MEDIOS_SOLICITUD
class MediosSolicitudSearch(generics.ListAPIView):
    serializer_class = MediosSolicitudSearchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        nombre_medio_solicitud = self.request.query_params.get('nombre_medio_solicitud', '').strip()
        aplica_para_pqrsdf = self.request.query_params.get('aplica_para_pqrsdf', '').strip()
        aplica_para_tramites = self.request.query_params.get('aplica_para_tramites', '').strip()
        aplica_para_otros = self.request.query_params.get('aplica_para_otros', '').strip()
        activo = self.request.query_params.get('activo', '').strip()

        medios_solicitud = MediosSolicitud.objects.all()

        if nombre_medio_solicitud:
            medios_solicitud = medios_solicitud.filter(nombre__icontains=nombre_medio_solicitud)

        
        if aplica_para_pqrsdf:
            medios_solicitud = medios_solicitud.filter(aplica_para_pqrsdf__icontains=aplica_para_pqrsdf)


        if aplica_para_tramites:
            medios_solicitud = medios_solicitud.filter(aplica_para_tramites__icontains=aplica_para_tramites)

        if aplica_para_otros:
            medios_solicitud = medios_solicitud.filter(descripcion__icontains=aplica_para_otros)

    
        if activo:
            medios_solicitud = medios_solicitud.filter(activo__icontains=activo)
            

        medios_solicitud = medios_solicitud.order_by('id_medio_solicitud')  # Ordenar aquí

        return medios_solicitud

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset.exists():
            return Response({
                'success': True,
                'detail': 'No se encontraron medios de solicitud que coincidan con los criterios de búsqueda.',
                'data': []
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(queryset, many=True)

        return Response({
            'success': True,
            'detail': 'Se encontraron los siguientes medios de solicitud.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    
#BORRAR_MEDIO_SOLICITUD
class MediosSolicitudDelete(generics.DestroyAPIView):
    queryset = MediosSolicitud.objects.all()
    serializer_class = MediosSolicitudDeleteSerializer 
    lookup_field = 'id_medio_solicitud'

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # Verificar si T253registroPrecargado es TRUE
        if instance.registro_precargado:
            return Response({'success': False,"detail": "No puedes eliminar este medio de solicitud porque está precargado (Registro_Precargado=TRUE)."}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar si T253itemYaUsado es TRUE
        if instance.item_ya_usado:
            return Response({'success': False,"detail": "No puedes eliminar este medio de solicitud porque ya ha sido usado (ItemYaUsado=TRUE)."}, status=status.HTTP_400_BAD_REQUEST)

        # Eliminar el medio de solicitud
        instance.delete()

        return Response({'success': True,"detail": "El medio de solicitud se eliminó con éxito."}, status=status.HTTP_200_OK)
    
#ACTUALIZAR_MEDIO_SOLICITUD
class MediosSolicitudUpdate(generics.UpdateAPIView):
    queryset = MediosSolicitud.objects.all()
    serializer_class = MediosSolicitudUpdateSerializer  
    lookup_field = 'id_medio_solicitud'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        # Verificar si T253registroPrecargado es TRUE
        if instance.registro_precargado:
            return Response({'success': False, "detail": "No puedes actualizar este medio de solicitud porque está precargado.", "data": MediosSolicitudUpdateSerializer(instance).data}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar si T253itemYaUsado es TRUE
        if instance.item_ya_usado:
            # Comprobar si 'nombre' está presente en los datos de solicitud
            if 'nombre' in request.data:
                return Response({'success': False, "detail": "No puedes actualizar el campo 'nombre' en este medio de solicitud.", "data": MediosSolicitudUpdateSerializer(instance).data}, status=status.HTTP_400_BAD_REQUEST)

            # Permitir actualizar otros campos
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'success': True, "detail": "El medio de solicitud se actualizó con éxito.", "data": serializer.data}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Si T253itemYaUsado es FALSE, permitir la actualización completa del medio de solicitud
        serializer = self.get_serializer(instance, data=request.data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, "detail": "El medio de solicitud se actualizó con éxito.", "data": serializer.data}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)