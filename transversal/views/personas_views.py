from asyncio import exceptions
from urllib.parse import quote_plus
from rest_framework.exceptions import APIException, ValidationError, NotFound, PermissionDenied
from datetime import datetime, date, timedelta
import copy
import datetime as dt
from signal import raise_signal

from django.urls import reverse
from django.shortcuts import redirect
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.sites.shortcuts import get_current_site
from gestion_documental.serializers.ventanilla_serializers import AutorizacionNotificacionesSerializer
from gestion_documental.views.bandeja_tareas_views import BandejaTareasPersonaCreate

from seguridad.serializers.user_serializers import RegisterExternoSerializer
from django.shortcuts import render
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from seguridad.renderers.user_renderers import UserRender
from django.template.loader import render_to_string
from seguridad.utils import Util
from rest_framework import status
from django.db.models import Q
from datetime import datetime
#from dateutil.parser import parse
from seguridad.permissions.permissions_user import PermisoActualizarExterno, PermisoActualizarInterno
from seguridad.views.user_views import RegisterExternoView
from seguridad.permissions.permissions_user_over_person import (
    PermisoActualizarPersona, 
    PermisoActualizarTipoDocumento, 
    PermisoBorrarEstadoCivil,
    PermisoBorrarTipoDocumento,
    PermisoConsultarEstadoCivil, 
    PermisoConsultarPersona,
    PermisoConsultarTipoDocumento,
    PermisoCrearEstadoCivil, 
    PermisoCrearPersona, 
    PermisoActualizarEstadoCivil,
    PermisoCrearTipoDocumento
    )
from transversal.models.base_models import (
    Cargos,
    EstadoCivil,
    TipoDocumento,
    ClasesTercero,
    ClasesTerceroPersona,
    ApoderadoPersona,
    HistoricoEmails,
    HistoricoDireccion,
    HistoricoAutirzacionesNotis,
    HistoricoRepresentLegales,
    HistoricoCargosUndOrgPersona,
    HistoricoCambiosIDPersonas
)
from transversal.models.personas_models import Personas
from seguridad.models import (
    User,
    UsuariosRol,
    Roles
)

from transversal.serializers.personas_serializers import (
    EmpresaSerializer,
    EstadoCivilSerializer,
    EstadoCivilPostSerializer,
    EstadoCivilPutSerializer,
    GetClaseTerceroSerializers,
    PersonaNaturalPostAdminSerializer,
    PersonaNaturalUpdateAdminSerializer,
    PersonasFilterAdminUserSerializer,
    TipoDocumentoSerializer,
    TipoDocumentoPostSerializer,
    TipoDocumentoPutSerializer,
    PersonasSerializer,
    PersonaNaturalSerializer,
    PersonaJuridicaSerializer,
    PersonaNaturalPostSerializer,
    PersonaJuridicaPostSerializer,
    PersonaNaturalPostByUserSerializer,
    PersonaNaturalUpdateSerializer,
    PersonaNaturalUpdateUserPermissionsSerializer,
    PersonaJuridicaUpdateSerializer,
    PersonaJuridicaUpdateUserPermissionsSerializer,
    ApoderadoPersonaSerializer,
    ApoderadoPersonaPostSerializer,
    HistoricoEmailsSerializer,
    HistoricoDireccionSerializer,
    ClasesTerceroSerializer,
    ClasesTerceroPersonaSerializer,
    ClasesTerceroPersonapostSerializer,
    GetPersonaJuridicaByRepresentanteLegalSerializer,
    CargosSerializer,
    HistoricoCargosUndOrgPersonapostSerializer,
    PersonasFilterSerializer,
    BusquedaHistoricoCambiosSerializer,
    UpdatePersonasNaturalesSerializer,
    UpdatePersonasJuridicasSerializer,
    HistoricoNotificacionesSerializer,
    HistoricoRepresentLegalSerializer
)

from rest_framework.views import APIView
from django.conf import settings
import jwt

from transversal.views.bandeja_alertas_views import BandejaAlertaPersonaCreate

# Views for Estado Civil


class GetEstadoCivil(generics.ListAPIView):
    serializer_class = EstadoCivilSerializer
    permission_classes = [IsAuthenticated] #PermisoConsultarEstadoCivil]
    queryset = EstadoCivil.objects.all()


class GetEstadoCivilById(generics.RetrieveAPIView):
    serializer_class = EstadoCivilSerializer
    queryset = EstadoCivil.objects.all()

class DeleteEstadoCivil(generics.RetrieveDestroyAPIView):
    serializer_class = EstadoCivilSerializer
    permission_classes = [IsAuthenticated, PermisoBorrarEstadoCivil]
    queryset = EstadoCivil.objects.all()
    
    def delete(self, request, pk):
        estado_civil = EstadoCivil.objects.filter(cod_estado_civil=pk).first()
        if estado_civil:
            pass 
            if estado_civil.precargado == False:
                if estado_civil.item_ya_usado == True:
                    raise PermissionDenied('Este estado civil ya está siendo usado, por lo cúal no es eliminable')   
  
                estado_civil.delete()    
                return Response({'success':True, 'detail':'Este estado civil ha sido eliminado exitosamente'}, status=status.HTTP_200_OK)
            else:
                raise PermissionDenied('No puedes eliminar un estado civil precargado')
        else:
            raise NotFound('No existe el estado civil')


class RegisterEstadoCivil(generics.CreateAPIView):
    serializer_class =  EstadoCivilPostSerializer
    permission_classes = [IsAuthenticated, PermisoCrearEstadoCivil]
    queryset = EstadoCivil.objects.all()   


class UpdateEstadoCivil(generics.RetrieveUpdateAPIView):
    serializer_class = EstadoCivilPutSerializer
    queryset = EstadoCivil.objects.all()
    permission_classes = [IsAuthenticated, PermisoActualizarEstadoCivil]

    def put(self, request, pk):
        estado_civil = EstadoCivil.objects.filter(cod_estado_civil=pk).first()

        if estado_civil:
            if estado_civil.precargado == False:
                if estado_civil.item_ya_usado == True:
                    raise PermissionDenied('Este estado civil ya está siendo usado, por lo cúal no es actualizable')
    
                serializer = self.serializer_class(estado_civil, data=request.data, many=False)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response({'success':True, 'detail':'Registro actualizado exitosamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)
            else:
                raise PermissionDenied('No puede actualizar un estado civil precargado')
        else:
            raise NotFound('No existe un estado civil con estos parametros')


# Views for Tipo Documento


class GetTipoDocumento(generics.ListAPIView):
    serializer_class = TipoDocumentoSerializer
    permission_classes = [IsAuthenticated] # PermisoConsultarTipoDocumento]
    queryset = TipoDocumento.objects.all()


class GetTipoDocumentoById(generics.RetrieveAPIView):
    serializer_class = TipoDocumentoSerializer
    queryset = TipoDocumento.objects.all()


class DeleteTipoDocumento(generics.RetrieveDestroyAPIView):
    serializer_class = TipoDocumentoSerializer
    permission_classes = [IsAuthenticated, PermisoBorrarTipoDocumento]
    queryset = TipoDocumento.objects.all()
    
    def delete(self, request, pk):
        tipo_documento = TipoDocumento.objects.filter(cod_tipo_documento=pk).first()
        if tipo_documento:
            if tipo_documento.precargado == False:
                if tipo_documento.item_ya_usado == True:
                    raise PermissionDenied('Este tipo de documento ya está siendo usado, por lo cúal no es eliminable')   
                
                tipo_documento.delete()    
                return Response({'success':True, 'detail':'Este tipo de documento ha sido eliminado exitosamente'}, status=status.HTTP_200_OK)
            else:
                raise PermissionDenied('No puedes eliminar un tipo de documento precargado')
        else:
            raise NotFound('No se encontró ningún tipo de documento con estos parámetros')


class RegisterTipoDocumento(generics.CreateAPIView):
    serializer_class = TipoDocumentoPostSerializer
    permission_classes = [IsAuthenticated, PermisoCrearTipoDocumento]
    queryset = TipoDocumento.objects.all()


class UpdateTipoDocumento(generics.RetrieveUpdateAPIView):
    serializer_class = TipoDocumentoPutSerializer
    queryset = TipoDocumento.objects.all()
    permission_classes = [IsAuthenticated, PermisoActualizarTipoDocumento]

    def put(self, request, pk):
        tipo_documento = TipoDocumento.objects.filter(cod_tipo_documento=pk).first()
        if tipo_documento:
            if tipo_documento.precargado == False:
                if tipo_documento.item_ya_usado == True:
                    raise PermissionDenied('Este tipo de documento ya está siendo usado, por lo cúal no es actualizable')
                
                serializer = self.serializer_class(tipo_documento, data=request.data, many=False)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response({'success':True, 'detail':'Registro actualizado exitosamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)
            else:
                raise PermissionDenied('Este es un dato precargado en el sistema, no se puede actualizar')
        else:
            raise NotFound('No se encontró ningún tipo de documento con estos parámetros')
            

# Views for Personas


class GetPersonasByTipoDocumentoAndNumeroDocumento(generics.GenericAPIView):
    serializer_class = PersonasFilterSerializer
    queryset = Personas.objects.all()
    
    def get(self, request, tipodocumento, numerodocumento):
        persona = self.queryset.all().filter(tipo_documento=tipodocumento, numero_documento=numerodocumento).first()
        if persona:
            persona_serializer = self.serializer_class(persona)
            if not persona.email:
                try:
                    raise PermissionDenied('El documento ingresado existe en el sistema, sin embargo no tiene un correo electrónico de notificación asociado, debe acercarse a Cormacarena y realizar una actualizacion  de datos para proceder con la creación del usuario en el sistema')
                except PermissionDenied as e:
                    return Response({'success':False, 'detail':'El documento ingresado existe en el sistema, sin embargo no tiene un correo electrónico de notificación asociado, debe acercarse a Cormacarena y realizar una actualizacion  de datos para proceder con la creación del usuario en el sistema', 'data':persona_serializer.data}, status=status.HTTP_403_FORBIDDEN)
            return Response({'success':True, 'detail':'Se encontró la siguiente persona', 'data': persona_serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success':True, 'detail':'No existe una persona con los parametros ingresados'}, status=status.HTTP_200_OK)

class GetPersonasByID(generics.GenericAPIView):
    serializer_class = PersonasSerializer
    queryset = Personas.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        persona = Personas.objects.filter(id_persona=pk).first()
        if persona:
            persona_serializer = self.serializer_class(persona)
            if not persona.email:
                try:
                    raise PermissionDenied('El documento ingresado existe en el sistema, sin embargo no tiene un correo electrónico de notificación asociado, debe acercarse a Cormacarena y realizar una actualizacion  de datos para proceder con la creación del usuario en el sistema')
                except PermissionDenied as e:
                    return Response({'success':False, 'detail':'El documento ingresado existe en el sistema, sin embargo no tiene un correo electrónico de notificación asociado, debe acercarse a Cormacarena y realizar una actualizacion  de datos para proceder con la creación del usuario en el sistema', 'data':persona_serializer.data}, status=status.HTTP_403_FORBIDDEN)
            return Response({'success':True, 'detail':'Se encontró la persona.','data': persona_serializer.data}, status=status.HTTP_200_OK)
        else:
            raise NotFound('No encontró ninguna persona con los parametros ingresados')
        
class GetPersonaJuridicaByRepresentanteLegal(generics.ListAPIView):
    serializer_class=GetPersonaJuridicaByRepresentanteLegalSerializer
    
    permission_classes=[IsAuthenticated]
    queryset = Personas.objects.all()
    
    def get(self,request):
        persona= request.user.persona
        representante_legal=self.queryset.all().filter(representante_legal=persona)
        if representante_legal:
            persona_serializada = self.serializer_class(representante_legal,many=True)
            return Response({'detail':persona_serializada.data},status=status.HTTP_200_OK)
        raise NotFound('No está asociado en ninguna empresa como representante legal')
        
class UpdatePersonaNaturalByself(generics.RetrieveUpdateAPIView):
    http_method_names = ['patch']
    serializer_class = PersonaNaturalUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def patch(self, request):
        data = request.data
        persona = request.user.persona
        previous_persona = copy.copy(persona)
        
        if persona.tipo_persona != "N":
            raise PermissionDenied('No se puede actualizar una persona jurídica con este servicio')
        
        if persona.id_persona != persona.id_persona_crea.id_persona:
                
            cambio = Util.comparacion_campos_actualizados(data,persona)
            if cambio:
                print(cambio)
                data['fecha_ultim_actualiz_diferente_crea'] = datetime.now()
                data['id_persona_ultim_actualiz_diferente_crea'] = persona.id_persona
        else:
            data['fecha_ultim_actualiz_diferente_crea'] = None
            data['id_persona_ultim_actualiz_diferente_crea'] = None 
        
        persona_serializada = self.serializer_class(persona, data=data, many=False)
        persona_serializada.is_valid(raise_exception=True)
        
        #PARA UTILIZARLO EN EL UTIL
        data['tipo_persona'] = persona.tipo_persona
        
        validaciones_persona = Util.guardar_persona(data)
        
        if not validaciones_persona['success']:
            return Response({'success':validaciones_persona['success'], 'detail':validaciones_persona['detail']}, status=validaciones_persona['status'])       
        
        serializador = persona_serializada.save()
        
        # auditoria actualizar persona
        usuario = request.user.id_usuario
        direccion=Util.get_client_ip(request)
        descripcion = {"TipodeDocumentoID": str(serializador.tipo_documento.cod_tipo_documento), "NumeroDocumentoID": str(serializador.numero_documento), "PrimerNombre": str(serializador.primer_nombre), "PrimerApellido": str(serializador.primer_apellido)}
        valores_actualizados = {'current': persona, 'previous': previous_persona}

        auditoria_data = {
            "id_usuario" : usuario,
            "id_modulo" : 1,
            "cod_permiso": "AC",
            "subsistema": 'TRSV',
            "dirip": direccion,
            "descripcion": descripcion, 
            "valores_actualizados": valores_actualizados
        }
        Util.save_auditoria(auditoria_data)
    
        return Response({'success':True, 'detail':'Persona actualizada correctamente', 'data': persona_serializada.data}, status=status.HTTP_201_CREATED)
    
class UpdatePersonaNaturalAdminPersonas(generics.UpdateAPIView):
    serializer_class = PersonaNaturalUpdateAdminSerializer
    permission_classes = [IsAuthenticated]
    queryset = Personas.objects.all()
    
    def put(self,request,id_persona):
    
        data = request.data
        persona_logueada = request.user.persona.id_persona
        persona = self.queryset.all().filter(id_persona = id_persona).first()
        
        if persona:
            persona_previous = copy.copy(persona)
            if persona.direccion_notificaciones != None:
                if data["direccion_notificaciones"] == None:
                    raise PermissionDenied('No se puede dejar en blanco debido a que ya había una dirección de notificación')
                
            if persona.tipo_persona != "N":
                raise PermissionDenied('No se puede actualizar una persona jurídica con este servicio')
                
            cambio = Util.comparacion_campos_actualizados(data,persona)
            
            if persona_logueada != persona.id_persona_crea.id_persona:
                
                if cambio:
                    data['fecha_ultim_actualiz_diferente_crea'] = datetime.now()
                    data['id_persona_ultim_actualiz_diferente_crea'] = persona_logueada
            else:
                data['fecha_ultim_actualiz_diferente_crea'] = None
                data['id_persona_ultim_actualiz_diferente_crea'] = None 
        
            persona_serializada = self.serializer_class(persona, data=data, many=False)
            persona_serializada.is_valid(raise_exception=True)
            
            #PARA UTILIZARLO EN EL UTIL
            data['tipo_persona'] = persona.tipo_persona
            
            validaciones_persona = Util.guardar_persona(data)
            
            if not validaciones_persona['success']:
                return Response({'success':validaciones_persona['success'], 'detail':validaciones_persona['detail']}, status=validaciones_persona['status'])       
            
            validaciones_cargo = Util.actualizacion_clase_tercero_admin(persona,request)
            
            if not validaciones_cargo['success']:
                return Response({'success':validaciones_cargo['success'], 'detail':validaciones_cargo['detail']}, status=validaciones_cargo['status'])       
        
            persona_actualizada = persona_serializada.save()
            
            if validaciones_cargo['actualizado'] == True and not cambio:

                persona_actualizada.fecha_ultim_actualiz_diferente_crea = datetime.now()
                persona_actualizada.id_persona_ultim_actualiz_diferente_crea = request.user.persona
                persona_actualizada.save()
            
            # AUDITORIA ACTUALIZAR PERSONA
            descripcion = {"TipodeDocumentoID": str(persona_actualizada.tipo_documento.cod_tipo_documento), "NumeroDocumentoID": str(persona_actualizada.numero_documento), "PrimerNombre": str(persona_actualizada.primer_nombre), "PrimerApellido": str(persona_actualizada.primer_apellido)}
            direccion=Util.get_client_ip(request)

            auditoria_data = {
                'id_usuario': request.user.id_usuario,
                "id_modulo" : 1,
                "cod_permiso": "AC",
                "subsistema": 'SEGU',
                "dirip": direccion,
                "descripcion": descripcion,
                "valores_actualizados_maestro": {'previous':persona_previous, 'current':persona},
                "valores_creados_detalles": validaciones_cargo['valores_creados_detalles'],
                "valores_eliminados_detalles": validaciones_cargo['valores_eliminados_detalles']
            }
            Util.save_auditoria_maestro_detalle(auditoria_data)
        
            return Response({'success':True, 'detail':'Se actualizó la persona correctamente','data':persona_serializada.data},status=status.HTTP_200_OK)
        
        raise NotFound('No existe la persona')
    
class UpdatePersonaJuridicaAdminPersonas(generics.UpdateAPIView):
    serializer_class = PersonaJuridicaUpdateSerializer
    permission_classes = [IsAuthenticated]
    queryset = Personas.objects.all()
    
    def put (self,request,id_persona):
        
        persona_logueada = request.user.persona.id_persona
        data = request.data
        persona = self.queryset.all().filter(id_persona = id_persona).first()
        print("PERSONA",persona.cod_naturaleza_empresa)
        if persona:
            
            if persona.tipo_persona != "J":
                raise PermissionDenied('No se puede actualizar una persona jurídica con este servicio')
        
            cambio = Util.comparacion_campos_actualizados(data,persona)
            
            if not persona.id_persona_crea or persona_logueada != persona.id_persona_crea.id_persona:
                if cambio:
                    data['fecha_ultim_actualiz_diferente_crea'] = datetime.now()
                    data['id_persona_ultim_actualiz_diferente_crea'] = persona_logueada
            else:
                data['fecha_ultim_actualiz_diferente_crea'] = None
                data['id_persona_ultim_actualiz_diferente_crea'] = None 
                
            #Validacion de Fecha de cambio de representante legal y fecha de incio de representantele legalñ
            
            if persona.representante_legal.id_persona != data["representante_legal"]:
                data['fecha_cambio_representante_legal'] = datetime.now()
                
                fecha_inicio = data.get("fecha_inicio_cargo_rep_legal")
            
                if not fecha_inicio:
                    fecha_inicio = datetime.now()
                    
                else:
                    fecha_formateada = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                    fecha_ahora = date.today()
                    if fecha_formateada > fecha_ahora or fecha_formateada <= persona.fecha_inicio_cargo_rep_legal:
                        raise PermissionDenied('La fecha de inicio del cargo del representante no debe ser superior a la del sistema y tiene que ser mayor a la fecha de inicio del representante legal anterior')

            else:
                fecha_inicio = data.get("fecha_inicio_cargo_rep_legal")
                if fecha_inicio: 
                
                    fecha_formateada = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                  
                    if persona.fecha_inicio_cargo_rep_legal != fecha_formateada:
                        raise PermissionDenied('No se puede actualizar la fecha de inicio de representante legal sin haber cambiado el representante')
                    
                data['fecha_cambio_representante_legal'] = None
                
            persona_serializada = self.serializer_class(persona, data=data, many=False)
            persona_serializada.is_valid(raise_exception=True)
            
            #PARA UTILIZARLO EN EL UTIL
            data['tipo_persona'] = persona.tipo_persona
            
            validaciones_persona = Util.guardar_persona(data)
            
            if not validaciones_persona['success']:
                return Response({'success':validaciones_persona['success'], 'detail':validaciones_persona['detail']}, status=validaciones_persona['status'])       
            
            validaciones_cargo=Util.actualizacion_clase_tercero_admin(persona,request)
            
            if not validaciones_cargo['success']:
                return Response({'success':validaciones_cargo['success'], 'detail':validaciones_cargo['detail']}, status=validaciones_cargo['status'])       
        
            persona_actualizada= persona_serializada.save()
            
            if validaciones_cargo['actualizado'] == True and not cambio:
                print("ENTRÓ")
                persona_actualizada.fecha_ultim_actualiz_diferente_crea = datetime.now()
                persona_actualizada.id_persona_ultim_actualiz_diferente_crea = request.user.persona
                persona_actualizada.save()
            
            return Response({'success':True, 'detail':'Se actualizó la persona correctamente','data':persona_serializada.data},status=status.HTTP_200_OK)
        
        raise NotFound('No existe la persona')


class RegisterPersonaJuridicaAdmin(generics.CreateAPIView):
    serializer_class = PersonaJuridicaPostSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        
        persona = request.data
        
        persona_logueada = request.user.persona.id_persona
        persona['id_persona_crea'] = persona_logueada 
        
        serializer = self.serializer_class(data=persona)
        serializer.is_valid(raise_exception=True)

        validaciones_persona = Util.guardar_persona(persona)
        
        if not validaciones_persona['success']:
            return Response({'success':validaciones_persona['success'], 'detail':validaciones_persona['detail']}, status=validaciones_persona['status'])       

        serializador = serializer.save()

        # VALIDAR EXISTENCIA CLASES TERCERO
        clases_tercero = ClasesTercero.objects.filter(id_clase_tercero__in = persona['datos_clasificacion_persona'])
        if len(set(persona['datos_clasificacion_persona'])) != len(clases_tercero):
            raise ValidationError('Debe validar que todas las clases tercero elegidas existan')
        
        #CREACION DE CLASE TERCERO
        for clase_tercero in clases_tercero:
            ClasesTerceroPersona.objects.create(
                id_persona = serializador,
                id_clase_tercero = clase_tercero
            )
        # AUDITORIA CREAR PERSONA
        descripcion = {"TipodeDocumentoID": str(serializador.tipo_documento), "NumeroDocumentoID": str(serializador.numero_documento), "RazonSocial": str(serializador.razon_social), "NombreComercial": str(serializador.nombre_comercial)}
        direccion=Util.get_client_ip(request)

        auditoria_data = {
            "id_modulo" : 9,
            "cod_permiso": "CR",
            "subsistema": 'TRSV',
            "dirip": direccion,
            "descripcion": descripcion, 
        }
        Util.save_auditoria(auditoria_data)
        #CREACION DE BANDEJA DE ALERTAS
        crear_bandeja=BandejaAlertaPersonaCreate()

        response_bandeja=crear_bandeja.crear_bandeja_persona({"id_persona":serializador.id_persona})
            
        if response_bandeja.status_code!=status.HTTP_201_CREATED:
            raise ValidationError(response_bandeja)
        #CREACION DE BANDEJA DE TAREAS
        vista_bandeja = BandejaTareasPersonaCreate()
        respuesta_bandeja = vista_bandeja.crear_bandeja({"id_persona":serializador.id_persona})
        if respuesta_bandeja.status_code != status.HTTP_201_CREATED:
            return respuesta_bandeja
        return Response({'success':True, 'detail':'Se creo la persona jurídica correctamente', 'data':serializer.data}, status=status.HTTP_201_CREATED)

class RegisterPersonaNaturalAdmin(generics.CreateAPIView):
    serializer_class = PersonaNaturalPostAdminSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        
        persona = request.data
        
        persona_logueada = request.user.persona.id_persona
        persona['id_persona_crea'] = persona_logueada 
        
        serializer = self.serializer_class(data=persona)
        serializer.is_valid(raise_exception=True)

        validaciones_persona = Util.guardar_persona(persona)
        
        if not validaciones_persona['success']:
            return Response({'success':validaciones_persona['success'], 'detail':validaciones_persona['detail']}, status=validaciones_persona['status'])       

        serializador = serializer.save()
    
        #CREACION DE CLASE TERCERO
        valores_creados_detalles = []
        for clase_tercero in persona['datos_clasificacion_persona']:

            clase_tercero_instance = ClasesTercero.objects.filter(id_clase_tercero = clase_tercero ).first()
            
            if clase_tercero_instance:
                ClasesTerceroPersona.objects.create(
                    id_persona = serializador,
                    id_clase_tercero = clase_tercero_instance
                )
                valores_creados_detalles.append({"NombreClaseTercero":clase_tercero_instance.nombre})
            else: raise PermissionDenied('La clase tercero '+str(clase_tercero)+' no existe')

        # AUDITORIA CREAR PERSONA
        descripcion = {"TipodeDocumentoID": str(serializador.tipo_documento), "NumeroDocumentoID": str(serializador.numero_documento), "PrimerNombre": str(serializador.primer_nombre), "PrimerApellido": str(serializador.primer_apellido)}
        direccion=Util.get_client_ip(request)

        auditoria_data = {
            "id_modulo" : 1,
            "cod_permiso": "CR",
            "subsistema": 'SEGU',
            "dirip": direccion,
            "descripcion": descripcion,
            "valores_creados_detalles": valores_creados_detalles
        }
        Util.save_auditoria_maestro_detalle(auditoria_data)
        #CREACION DE BANDEJA DE ALERTAS
        crear_bandeja=BandejaAlertaPersonaCreate()

        response_bandeja=crear_bandeja.crear_bandeja_persona({"id_persona":serializador.id_persona})
            
        if response_bandeja.status_code!=status.HTTP_201_CREATED:
            raise ValidationError(response_bandeja)
        #CREACION DE BANDEJA DE TAREAS
        vista_bandeja = BandejaTareasPersonaCreate()
        respuesta_bandeja = vista_bandeja.crear_bandeja({"id_persona":serializador.id_persona})
        if respuesta_bandeja.status_code != status.HTTP_201_CREATED:
            return respuesta_bandeja

        return Response({'success':True, 'detail':'Se creo la persona jurídica correctamente', 'data':serializer.data}, status=status.HTTP_201_CREATED)


class GetClasesTerceroByPersona(generics.ListAPIView):
    serializer_class = GetClaseTerceroSerializers
    queryset = ClasesTercero.objects.all()
    
    
    def get (self,request,id_persona):
        
        persona = Personas.objects.filter(id_persona=id_persona).first()
    
        if persona:
            
            clases_tercero_persona = ClasesTerceroPersona.objects.filter(id_persona = id_persona)
            if clases_tercero_persona:
                list_clases_tercero = [clases.id_clase_tercero for clases in clases_tercero_persona]
                
                serializador = self.serializer_class(list_clases_tercero,many = True)
            
                return Response({'success':True, 'detail':'Se encontraron clases tercero para la persona seleccionada','data':serializador.data},status=status.HTTP_200_OK)
            
            return Response({'success':True, 'detail':'No se encontraron clases tercero para la persona seleccionada'},status=status.HTTP_200_OK)
        raise PermissionDenied('No existe la persona')
        

class UpdatePersonaJuridicaBySelf(generics.UpdateAPIView):
    http_method_names = ['patch']
    serializer_class = PersonaJuridicaUpdateSerializer
    permission_classes = [IsAuthenticated]
    queryset = Personas.objects.all()
    
    def patch(self,request):
        
        data = request.data
        persona = request.user.persona
        previous_persona = copy.copy(persona)
        
        if persona.tipo_persona != "J":
            raise PermissionDenied('No se puede actualizar una persona natural con este servicio')
            
        if persona.id_persona != persona.id_persona_crea.id_persona:
                
            cambio = Util.comparacion_campos_actualizados(data,persona)
            if cambio:
                print(cambio)
                data['fecha_ultim_actualiz_diferente_crea'] = datetime.now()
                data['id_persona_ultim_actualiz_diferente_crea'] = persona.id_persona
        else:
            data['fecha_ultim_actualiz_diferente_crea'] = None
            data['id_persona_ultim_actualiz_diferente_crea'] = None 
            
        #Validacion de Fecha de cambio de representante legal y fecha de incio de representantele legalñ
            
        if persona.representante_legal.id_persona != data["representante_legal"]:
            data['fecha_cambio_representante_legal'] = datetime.now()
            
            fecha_inicio = data.get("fecha_inicio_cargo_rep_legal")
        
            if not fecha_inicio:
                fecha_inicio = datetime.now()
                
            else:
                fecha_formateada = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                fecha_ahora = date.today()
                if fecha_formateada > fecha_ahora or fecha_formateada <= persona.fecha_inicio_cargo_rep_legal:
                    raise PermissionDenied('La fecha de inicio del cargo del representante no debe ser superior a la del sistema y tiene que ser mayor a la fecha de inicio del representante legal anterior')

        else:
            fecha_inicio = data.get("fecha_inicio_cargo_rep_legal")
            if fecha_inicio: 
            
                fecha_formateada = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                print()
                if persona.fecha_inicio_cargo_rep_legal != fecha_formateada:
                    raise PermissionDenied('No se puede actualizar la fecha de inicio de representante legal sin haber cambiado el representante')
                
            data['fecha_cambio_representante_legal'] = None
        
        persona_serializada = self.serializer_class(persona, data=data, many=False)
        persona_serializada.is_valid(raise_exception=True)
        
        #PARA UTULIZARLO EN EL UTIL
        data['tipo_persona'] = persona.tipo_persona
        
        validaciones_persona = Util.guardar_persona(data)
        
        if not validaciones_persona['success']:
            return Response({'success':validaciones_persona['success'], 'detail':validaciones_persona['detail']}, status=validaciones_persona['status'])       
        
        serializador = persona_serializada.save()
        
        # auditoria actualizar persona
        usuario = request.user.id_usuario
        direccion=Util.get_client_ip(request)
        descripcion = {"TipodeDocumentoID": str(serializador.tipo_documento), "NumeroDocumentoID": str(serializador.numero_documento), "PrimerNombre": str(serializador.primer_nombre), "PrimerApellido": str(serializador.primer_apellido)}
        valores_actualizados = {'current': persona, 'previous': previous_persona}

        auditoria_data = {
            "id_usuario" : usuario,
            "id_modulo" : 1,
            "cod_permiso": "AC",
            "subsistema": 'TRSV',
            "dirip": direccion,
            "descripcion": descripcion, 
            "valores_actualizados": valores_actualizados
        }
        Util.save_auditoria(auditoria_data)
        
        return Response({'success':True, 'detail':'Persona actualizada correctamente', 'data': persona_serializada.data}, status=status.HTTP_201_CREATED)


# Views for Sucursales Empresas


# class getSucursalesEmpresas(generics.ListAPIView):
#     serializer_class = SucursalesEmpresasSerializer
#     queryset = SucursalesEmpresas.objects.all()


# class getSucursalEmpresaById(generics.RetrieveAPIView):
#     serializer_class = SucursalesEmpresasSerializer
#     queryset = SucursalesEmpresas.objects.all()


# class deleteSucursalEmpresa(generics.DestroyAPIView):
#     serializer_class = SucursalesEmpresasSerializer
#     queryset = SucursalesEmpresas.objects.all()
#     permission_classes = [IsAuthenticated]
    
#     def delete(self,request,pk):
#         sucursal=SucursalesEmpresas.objects.filter(id_sucursal_empresa=pk).first()

#         if sucursal:
#             persona_empresa=sucursal.id_persona_empresa
#             sucursal.delete()
#             persona=Personas.objects.get(id_persona=persona_empresa.id_persona)
#             usuario = request.user.id_usuario
#             dirip = Util.get_client_ip(request)
#             descripcion ={ "nombre razón social": str(persona.razon_social),"sucursal" :str(sucursal.sucursal)}
#             auditoria_data = {
#                 'id_usuario': usuario,
#                 'id_modulo': 1,
#                 'cod_permiso': 'BO',
#                 'subsistema': 'TRSV',
#                 'dirip': dirip,
#                 'descripcion': descripcion,
#             }
            
#             Util.save_auditoria(auditoria_data)

#             return Response({'success':True, 'detail':'La sucursal empresa fue eliminada'}, status=status.HTTP_200_OK)
#         else:
#             raise ValidationError('No existe sucursal')
            
# class updateSucursalEmpresa(generics.RetrieveUpdateAPIView):
#     serializer_class = SucursalesEmpresasPostSerializer
#     queryset = SucursalesEmpresas.objects.all()
#     permission_classes = [IsAuthenticated]
    
#     def put(self, request,pk=None):
#         sucursal = SucursalesEmpresas.objects.filter(id_sucursal_empresa= pk).first()
#         previous_sucursal = copy.copy(sucursal)
#         if sucursal:
#             sucursal_serializer = self.serializer_class(sucursal, data=request.data)
#             sucursal_serializer.is_valid(raise_exception=True)
#             sucursal_serializer.save()
            
#             usuario = request.user.id_usuario
#             persona=Personas.objects.get(id_persona=request.data['id_persona_empresa'])
#             dirip = Util.get_client_ip(request)
#             descripcion ={ "nombre razón social": str(persona.razon_social),"sucursal" :str(sucursal.sucursal)}
#             valores_actualizados={'current':sucursal, 'previous':previous_sucursal}

#             auditoria_data = {
#                 'id_usuario': usuario,
#                 'id_modulo': 1,
#                 'cod_permiso': 'AC',
#                 'subsistema': 'TRSV',
#                 'dirip': dirip,
#                 'descripcion': descripcion,
#                 'valores_actualizados': valores_actualizados
#             }
            
#             Util.save_auditoria(auditoria_data)
#             return Response({'success':True, 'detail':'la sucursal empresa actualizada'}, status=status.HTTP_201_CREATED)
#         else:
#             raise ValidationError('No existe sucursal')

# class registerSucursalEmpresa(generics.CreateAPIView):
#     serializer_class = SucursalesEmpresasPostSerializer 
#     queryset = SucursalesEmpresas.objects.all()
#     permission_classes = [IsAuthenticated]
    
#     def create(self, request, *args, **kwargs):
#         serializer = self.get_serializer(data=request.data)
#         serializer.is_valid(raise_exception=True)

#         serializador=serializer.save()
#         usuario = request.user.id_usuario

#         persona=Personas.objects.get(id_persona=request.data['id_persona_empresa'])
#         dirip = Util.get_client_ip(request)
#         descripcion ={ "nombre razón social": str(persona.razon_social),"sucursal" :str(serializador.sucursal)}

#         auditoria_data = {
#             'id_usuario': usuario,
#             'id_modulo': 1,
#             'cod_permiso': 'CR',
#             'subsistema': 'TRSV',
#             'dirip': dirip,
#             'descripcion': descripcion,
#         }
        
#         Util.save_auditoria(auditoria_data)
#         headers = self.get_success_headers(serializer.data)
#         return Response({'success':True},serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    

# Views for Historico Emails
class HistoricoEmailsByIdPersona(generics.ListAPIView):
    serializer_class = HistoricoEmailsSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        id_persona = self.kwargs['id_persona']
        queryset = HistoricoEmails.objects.filter(id_persona=id_persona)
        return queryset

# Views for Historico Direcciones
class HistoricoDireccionByIdPersona(generics.ListAPIView):
    serializer_class = HistoricoDireccionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        id_persona = self.kwargs['id_persona']
        queryset = HistoricoDireccion.objects.filter(id_persona=id_persona)
        return queryset


class GetCargosList(generics.ListAPIView):
    serializer_class = CargosSerializer
    queryset = Cargos.objects.all()

    def get(self, request):
        cargos = Cargos.objects.all()
        serializador = self.serializer_class(cargos, many=True)
        if cargos:
            return Response({'success':True, 'detail':'Se encontraron cargos', 'data':serializador.data}, status=status.HTTP_200_OK)
        else:
            try:
                raise NotFound('No se encontró ningún cargo')
            except NotFound as e:
                return Response({'success':False, 'detail':'No se encontró ningún cargo', 'data':[]}, status=status.HTTP_404_NOT_FOUND)

class RegisterCargos(generics.CreateAPIView):
    serializer_class =  CargosSerializer
    queryset = Cargos.objects.all()

    def post(self, request):
        data = request.data
        serializador = self.serializer_class(data=data)
        serializador.is_valid(raise_exception=True)
        serializador.save()
        return Response({'success':True, 'detail':'Se ha creado el cargo', 'data':serializador.data}, status=status.HTTP_201_CREATED)

class UpdateCargos(generics.UpdateAPIView):
    serializer_class = CargosSerializer
    queryset = Cargos.objects.all()

    def put(self, request, pk):
        cargo = Cargos.objects.filter(id_cargo=pk).first()

        if cargo:
            if not cargo.item_usado:
                serializer = self.serializer_class(cargo, data=request.data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response({'success':True, 'detail':'Registro actualizado exitosamente', 'data':serializer.data}, status=status.HTTP_201_CREATED)
            else:
                raise PermissionDenied('Este cargo ya está siendo usado, por lo cual no es actualizable')
        else:
            raise NotFound('No existe el cargo')

class DeleteCargo(generics.DestroyAPIView):
    serializer_class = CargosSerializer
    queryset = Cargos.objects.all()

    def delete(self, request, pk):
        cargo = Cargos.objects.filter(id_cargo=pk).first()
        if cargo:
            if not cargo.item_usado:
                cargo.delete()
                return Response({'success':True, 'detail':'El cargo ha sido eliminado exitosamente'}, status=status.HTTP_200_OK)
            else:
                raise PermissionDenied('Este cargo ya está siendo usado, no se pudo eliminar. Intente desactivar')
        else:
            raise NotFound('No existe el cargo')


class GetPersonasByFilters(generics.ListAPIView):
    serializer_class = PersonasFilterSerializer
    queryset = Personas.objects.all()

    def get(self,request):
        filter = {}
        
        for key,value in request.query_params.items():
            if key in ['tipo_documento','numero_documento','primer_nombre','primer_apellido','razon_social','nombre_comercial', 'tipo_persona']:
                if key in ['primer_nombre','primer_apellido','razon_social','nombre_comercial']:
                    if value != "":
                        filter[key+'__icontains']=  value
                elif key == "numero_documento":
                    if value != "":
                        filter[key+'__icontains'] = value
                else:
                    if value != "":
                        filter[key] = value
                        
        personas = self.queryset.all().filter(**filter)
        
        serializer = self.serializer_class(personas, many=True)
        return Response({'success':True, 'detail':'Se encontraron las siguientes personas que coinciden con los criterios de búsqueda', 'data':serializer.data}, status=status.HTTP_200_OK)

class BusquedaHistoricoCambios(generics.ListAPIView):
    serializer_class = BusquedaHistoricoCambiosSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, id_persona):
        try:
            persona = HistoricoCambiosIDPersonas.objects.filter(id_persona=id_persona)
        except HistoricoCambiosIDPersonas.DoesNotExist:
            raise NotFound('La persona con el id proporcionado no tiene un historico de cambios asociado')
        cambios_persona = HistoricoCambiosIDPersonas.objects.filter(id_persona=id_persona)
        serializador = self.serializer_class(cambios_persona, many=True)
        return Response({'success':True, 'detail':'La persona con el id proporcionado tiene un historico asociado', 'data':serializador.data}, status=status.HTTP_200_OK)

class ActualizarPersonasNatCamposRestringidosView(generics.UpdateAPIView):
    serializer_class = UpdatePersonasNaturalesSerializer
    permission_classes = [IsAuthenticated]
    queryset = Personas.objects.filter(tipo_persona='N')

    def put(self, request, id_persona):

        data = request.data
        persona_log = request.user.persona.id_persona
        persona = self.queryset.all().filter(id_persona=id_persona).first()
        
        if persona is not None:
            previous_persona = copy.copy(persona)
            serializer = self.serializer_class(persona, data=data)
            serializer.is_valid(raise_exception=True)

            if data['tipo_documento'] == "NT":
                raise PermissionDenied('El tipo de documento no se puede actualizar a NIT')
            
            if persona.id_persona != persona_log:
                del data["justificacion"]
                del data["ruta_archivo_soporte"]
                cambio = Util.comparacion_campos_actualizados(data,persona)
                if cambio:
                    data['fecha_ultim_actualiz_diferente_crea'] = datetime.now()
                    data['id_persona_ultim_actualiz_diferente_crea'] = persona.id_persona
            else: 
                data['fecha_ultim_actualiz_diferente_crea'] = None
                data['id_persona_ultim_actualiz_diferente_crea'] = None
            
            historicos_creados = []

            #HISTORICO
            for field, value in request.data.items():
                if field != 'ruta_archivo_soporte' and field != "justificacion":
                    valor_previous= getattr(persona,field)
                    valor_previous = valor_previous.cod_tipo_documento if field == 'tipo_documento' else valor_previous

                    if value != valor_previous:
                        historico = HistoricoCambiosIDPersonas.objects.create(
                            id_persona=persona,
                            nombre_campo_cambiado=field,
                            valor_campo_cambiado=valor_previous if valor_previous!=None else "",
                            ruta_archivo_soporte=request.data.get('ruta_archivo_soporte', ''),
                            justificacion_cambio=request.data.get('justificacion', ''),
                        )
                        historicos_creados.append(historico)

            #ACTUALIZACIÓN GUARDADA
            serializer.save()

            #AUDITORÍA
            usuario = request.user.id_usuario
            direccion=Util.get_client_ip(request)
            descripcion = {"TipodeDocumentoID": str(previous_persona.tipo_documento), "NumeroDocumentoID": str(previous_persona.numero_documento)}
            valores_actualizados = {'current': persona, 'previous': previous_persona}

            auditoria_data = {
                "id_usuario" : usuario,
                "id_modulo" : 1,
                "cod_permiso": "AC",
                "subsistema": 'TRSV',
                "dirip": direccion,
                "descripcion": descripcion, 
                "valores_actualizados": valores_actualizados
            }
            Util.save_auditoria(auditoria_data)

            return Response({'success':True, 'detail':'Se actualizó los datos de la persona natural','data':serializer.data}, status=status.HTTP_200_OK)
        else:
            raise NotFound('La persona no existe o es una persona jurídica')

class ActualizarPersonasJurCamposRestringidosView(generics.UpdateAPIView):
    serializer_class = UpdatePersonasJuridicasSerializer
    permission_classes = [IsAuthenticated]
    queryset = Personas.objects.filter(tipo_persona='J')

    def put(self, request, id_persona):

        data = request.data
        persona_log = request.user.persona.id_persona
        persona = self.queryset.all().filter(id_persona=id_persona).first()
        if persona:
            previous_persona = copy.copy(persona)

            serializer = self.serializer_class(persona, data=data)
            serializer.is_valid(raise_exception=True)

            if persona.id_persona != persona_log:
                del data["justificacion"]
                del data["ruta_archivo_soporte"]
                cambio = Util.comparacion_campos_actualizados(data,persona)
                if cambio:
                    data['fecha_ultim_actualiz_diferente_crea'] = datetime.now()
                    data['id_persona_ultim_actualiz_diferente_crea'] = persona.id_persona
                else: 
                    data['fecha_ultim_actualiz_diferente_crea'] = None
                    data['id_persona_ultim_actualiz_diferente_crea'] = None
            historicos_creados = []

            #HISTORICO
            for field, value in request.data.items():
                
                if field != 'ruta_archivo_soporte' and field != "justificacion":
                    valor_previous= getattr(persona,field)
                    if value != valor_previous:
                        historico = HistoricoCambiosIDPersonas.objects.create(
                            id_persona=persona,
                            nombre_campo_cambiado=field,
                            valor_campo_cambiado=valor_previous if valor_previous!=None else "",
                            ruta_archivo_soporte=request.data.get('ruta_archivo_soporte', ''),
                            justificacion_cambio=request.data.get('justificacion', ''),
                        )
                        historicos_creados.append(historico)

            #ACTUALIZACIÓN GUARDADA
            serializer.save()

            #AUDITORÍA
            usuario = request.user.id_usuario
            direccion=Util.get_client_ip(request)
            descripcion = {"NumeroDocumentoID": str(previous_persona.numero_documento)}
            valores_actualizados = {'current': persona, 'previous': previous_persona}

            auditoria_data = {
                "id_usuario" : usuario,
                "id_modulo" : 1,
                "cod_permiso": "AC",
                "subsistema": 'TRSV',
                "dirip": direccion,
                "descripcion": descripcion, 
                "valores_actualizados": valores_actualizados
            }
            Util.save_auditoria(auditoria_data)

            return Response({'success':True, 'detail':'Se actualizó los datos de la persona jurídica','data':serializer.data}, status=status.HTTP_200_OK)
        else:
            raise NotFound('La persona no existe o es una persona natural')
        

class CreatePersonaJuridicaAndUsuario(generics.CreateAPIView):
    
    serializer_class = PersonaJuridicaPostSerializer   
    serializer_class_usuario = RegisterExternoSerializer  
    queryset = Personas.objects.all()
    
    def post(self,request):
        
        data = request.data
        
        #CREACION DE PERSONA JURIDICA
        
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)

        validaciones_persona = Util.guardar_persona(data)
        
        if not validaciones_persona['success']:
            return Response({'success':validaciones_persona['success'], 'detail':validaciones_persona['detail']}, status=validaciones_persona['status'])       
      
        #CREACION DE USUARIO PARA LA PERSONA JURIDICA
        
        redirect_url=request.data.get('redirect_url','')
        redirect_url=quote_plus(redirect_url)
        
        if " " in data['nombre_de_usuario']:
            raise PermissionDenied('No puede contener espacios en el nombre de usuario')
        
        #GUARDAR PERSONA
        serializador = serializer.save()
        serializador.id_persona_crea = serializador
        serializador.save()
        
        #USUARIO
        data['creado_por_portal'] = True
        data['persona'] = serializador.id_persona
        
        serializer = self.serializer_class_usuario(data=data)
        serializer.is_valid(raise_exception=True)
        nombre_de_usuario = str(serializer.validated_data.get('nombre_de_usuario', '')).lower()
        serializer_response = serializer.save()
        
        #ASIGNARLE ROL USUARIO EXTERNO POR DEFECTO
        rol = Roles.objects.get(id_rol=2)
        usuario_por_asignar = User.objects.get(nombre_de_usuario=nombre_de_usuario)     
        UsuariosRol.objects.create(
            id_rol = rol,
            id_usuario = usuario_por_asignar
        )

        # AUDITORIA AL REGISTRAR USUARIO

        dirip = Util.get_client_ip(request)
        descripcion = {'NombreUsuario': str(request.data["nombre_de_usuario"]).lower()}

        auditoria_data = {
            'id_usuario': serializer_response.pk,
            'id_modulo': 10,
            'cod_permiso': 'CR',
            'subsistema': 'SEGU',
            'dirip': dirip,
            'descripcion': descripcion
        }
        Util.save_auditoria(auditoria_data)

        #AUDITORIA AL ASIGNARLE ROL DE USUARIO EXTERNO POR DEFECTO
        dirip = Util.get_client_ip(request)
        descripcion = {'NombreUsuario': str(request.data["nombre_de_usuario"]).lower(), 'Rol': rol}
        auditoria_data = {
            'id_usuario': serializer_response.pk,
            'id_modulo': 5,
            'cod_permiso': 'CR',
            'subsistema': 'SEGU',
            'dirip': dirip,
            'descripcion': descripcion
        }
        Util.save_auditoria(auditoria_data)
        
        # AUDITORIA CREAR PESONA
        descripcion = {"TipodeDocumentoID": str(serializador.tipo_documento), "NumeroDocumentoID": str(serializador.numero_documento), "RazonSocial": str(serializador.razon_social), "NombreComercial": str(serializador.nombre_comercial)}
        direccion=Util.get_client_ip(request)

        auditoria_data = {
            "id_modulo" : 9,
            "cod_permiso": "CR",
            "subsistema": 'TRSV',
            "dirip": direccion,
            "descripcion": descripcion, 
        }
        Util.save_auditoria(auditoria_data)


        token = RefreshToken.for_user(serializer_response)

        current_site=get_current_site(request).domain

        relativeLink= reverse('verify')
        absurl= 'http://'+ current_site + relativeLink + "?token="+ str(token) + '&redirect-url=' + redirect_url


        subject = "Verifica tu usuario"
        template = "activación-de-usuario.html"

        Util.notificacion(serializador,subject,template,absurl=absurl,email=serializador.email)
        #CREACION DE BANDEJA DE ALERTAS
        crear_bandeja=BandejaAlertaPersonaCreate()

        response_bandeja=crear_bandeja.crear_bandeja_persona({"id_persona":serializador.id_persona})
            
        if response_bandeja.status_code!=status.HTTP_201_CREATED:
            raise ValidationError(response_bandeja)
        #CREACION DE BANDEJA DE TAREAS
        vista_bandeja = BandejaTareasPersonaCreate()
        respuesta_bandeja = vista_bandeja.crear_bandeja({"id_persona":serializador.id_persona})
        if respuesta_bandeja.status_code != status.HTTP_201_CREATED:
                return respuesta_bandeja
        return Response({'success':True, 'detail':'Se creo la persona jurídica y el usuario correctamente'},status=status.HTTP_200_OK)


class CreatePersonaNaturalAndUsuario(generics.CreateAPIView):
    
    serializer_class = PersonaNaturalPostSerializer   
    serializer_class_usuario = RegisterExternoSerializer  
    queryset = Personas.objects.all()
    
    def post(self,request):
        
        try:
            
            data = request.data
            fecha_nacimiento_str = data['fecha_nacimiento']

            try:
                fecha_nacimiento = datetime.strptime(fecha_nacimiento_str, '%Y-%m-%d').date()
            except ValueError:
                raise ValidationError('Formato de fecha de nacimiento inválido')
            
            if fecha_nacimiento >= datetime.now().date():
                raise ValidationError('La fecha de nacimiento es incorrecta')
            
            # fecha_nacimiento = parse(data['fecha_nacimiento']).date()
            # if fecha_nacimiento >= datetime.now().date():
            #     raise ValidationError('La fecha de nacimiento es incorrecta')

            #CREACION DE PERSONA
            
            serializer_persona = self.serializer_class(data=data)
            serializer_persona.is_valid(raise_exception=True)

            validaciones_persona = Util.guardar_persona(data)
            
            if not validaciones_persona['success']:
                return Response({'success':validaciones_persona['success'], 'detail':validaciones_persona['detail']}, status=validaciones_persona['status'])       
            
            #CREACION DE USUARIO
            
            redirect_url=request.data.get('redirect_url','')
            redirect_url=quote_plus(redirect_url)
            
            if " " in data['nombre_de_usuario']:
                raise PermissionDenied('No puede contener espacios en el nombre de usuario')
            
            #GUARDAR PERSONA
            serializador = serializer_persona.save()
            serializador.id_persona_crea = serializador
            serializador.save()
            
            data['creado_por_portal'] = True
            data['persona'] = serializador.id_persona
            
            serializer = self.serializer_class_usuario(data=data)
            serializer.is_valid(raise_exception=True)
            
            nombre_de_usuario = str(serializer.validated_data.get('nombre_de_usuario', '')).lower()
            
            serializer_response = serializer.save()
            serializer_response.id_usuario_creador = serializer_response
            serializer_response.save()
            
            #ASIGNARLE ROL USUARIO EXTERNO POR DEFECTO
            rol = Roles.objects.get(id_rol=2)
            usuario_por_asignar = User.objects.get(nombre_de_usuario=nombre_de_usuario)     
            UsuariosRol.objects.create(
                id_rol = rol,
                id_usuario = usuario_por_asignar
            )
            
            # AUDITORIA CREACION PERSONA NATURAL
            descripcion = {"TipodeDocumentoID": str(serializador.tipo_documento), "NumeroDocumentoID": str(serializador.numero_documento), "RazonSocial": str(serializador.razon_social), "NombreComercial": str(serializador.nombre_comercial)}
            dirip = Util.get_client_ip(request)
            auditoria_data = {
                'id_usuario': serializer_response.pk,
                "id_modulo" : 9,
                "cod_permiso": "CR",
                "subsistema": 'TRSV',
                "dirip": dirip,
                "descripcion": descripcion, 
            }
            Util.save_auditoria(auditoria_data)

            # AUDITORIA AL REGISTRAR USUARIO

            descripcion = {'NombreUsuario': str(request.data["nombre_de_usuario"]).lower()}
            valores_creados_detalles = [{"NombreRol": rol.nombre_rol}]
            auditoria_data = {
                'id_usuario': serializer_response.pk,
                'id_modulo': 10,
                'cod_permiso': 'CR',
                'subsistema': 'SEGU',
                'dirip': dirip,
                'descripcion': descripcion,
                'valores_creados_detalles': valores_creados_detalles
            }
            Util.save_auditoria_maestro_detalle(auditoria_data)
            
            token = RefreshToken.for_user(serializer_response)

            current_site=get_current_site(request).domain

            relativeLink= reverse('verify')
            absurl= 'http://'+ current_site + relativeLink + "?token="+ str(token) + '&redirect-url=' + redirect_url
            
            subject = "Verifica tu usuario"
            template = "activación-de-usuario.html"

            #CREACION DE BANDEJA DE ALERTAS
            crear_bandeja=BandejaAlertaPersonaCreate()

            response_bandeja=crear_bandeja.crear_bandeja_persona({"id_persona":serializador.id_persona})
            
            if response_bandeja.status_code!=status.HTTP_201_CREATED:
                raise ValidationError(response_bandeja)
            #print(response_bandeja.status_code)
            #CREACION DE BANDEJA DE TAREAS
            vista_bandeja = BandejaTareasPersonaCreate()
            respuesta_bandeja = vista_bandeja.crear_bandeja({"id_persona":serializador.id_persona})
            if respuesta_bandeja.status_code != status.HTTP_201_CREATED:
                return respuesta_bandeja

            #FIN CREACION DE BANDEJA DE TAREAS
            Util.notificacion(serializador,subject,template,absurl=absurl,email=serializador.email)
        
            return Response({'success':True, 'detail':'Se creo la persona natural y el usuario correctamente'},status=status.HTTP_200_OK)
    
        except ValidationError  as e:
            #error_message = {'error': }
            raise ValidationError(e.detail)



class AutorizacionNotificacionesPersonas(generics.RetrieveUpdateAPIView):
    serializer_class = AutorizacionNotificacionesSerializer
    queryset = Personas.objects.all()

    def put(self, request):
        persona_ = self.request.user.id_usuario
        persona = self.request.user.persona
        data = request.data
        previous_user = copy.copy(persona)

        if 'acepta_autorizacion_email' in data and 'acepta_autorizacion_sms' in data:
            acepta_autorizacion_email = data['acepta_autorizacion_email']
            acepta_autorizacion_sms = data['acepta_autorizacion_sms']

            persona.acepta_notificacion_email = acepta_autorizacion_email
            persona.acepta_notificacion_sms = acepta_autorizacion_sms
            persona.save()

            # AUDITORIA AUTORIZACION NOTIFICACIONES
            dirip = Util.get_client_ip(request)
            descripcion = {'tipo_documento': persona.tipo_documento, 'numero_documento':persona.numero_documento}
            valores_actualizados = {'current': persona, 'previous': previous_user}

            auditoria_data = {
                'id_usuario': persona_,
                'id_modulo': 69,
                'cod_permiso': 'AC',
                'subsistema': 'SEGU',
                'dirip': dirip,
                'descripcion': descripcion,
                'valores_actualizados': valores_actualizados
            }

            Util.save_auditoria(auditoria_data)

            if acepta_autorizacion_email and acepta_autorizacion_sms:
                return Response({'success':True, 'detail':'Autorización por correo electrónico y teléfono aceptada'}, status=status.HTTP_200_OK)
            elif acepta_autorizacion_email:
                return Response({'success':True, 'detail':'Autorización por correo electrónico aceptada'}, status=status.HTTP_200_OK)
            elif acepta_autorizacion_sms:
                return Response({'success':True, 'detail':'Autorización por teléfono aceptada'}, status=status.HTTP_200_OK)
            else:
                return Response({'success':True, 'detail':'Autorizacion no aceptada'}, status=status.HTTP_200_OK)
        else: 
            raise ValidationError('No envió las autorizaciones')

class GetPersonasByTipoDocumentoAndNumeroDocumentoAdminUser(GetPersonasByTipoDocumentoAndNumeroDocumento):
    serializer_class = PersonasFilterAdminUserSerializer
    queryset = Personas.objects.all()
    
class GetPersonasByFiltersAdminUser(GetPersonasByFilters):
    serializer_class = PersonasFilterAdminUserSerializer
    queryset = Personas.objects.all()

class HistoricoAutorizacionNotificacionesByIdPersona(generics.ListAPIView):
    serializer_class = HistoricoNotificacionesSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        id_persona = self.kwargs['id_persona']
        queryset = HistoricoAutirzacionesNotis.objects.filter(id_persona=id_persona)
        return queryset
    
class HistoricoRepresentLegalView(generics.ListAPIView):
    serializer_class = HistoricoRepresentLegalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        id_persona_empresa = self.kwargs['id_persona_empresa']
        queryset = HistoricoRepresentLegales.objects.filter(id_persona_empresa=id_persona_empresa)
        return queryset

class GetEmpresasByTipoDocumentoAndNumeroDocumento(generics.GenericAPIView):
    serializer_class = EmpresaSerializer
    queryset = Personas.objects.all()
    
    def get(self, request, tipo_documento, numero_documento):
        empresa = self.queryset.all().filter(tipo_documento=tipo_documento, numero_documento=numero_documento).first()
        if empresa:
            empresa_serializer = self.serializer_class(empresa)
            return Response({'success':True, 'detail': 'Se encontro la siguiente empresa', 'data': empresa_serializer.data}, status=status.HTTP_200_OK)
        else:
             raise NotFound("No existe una empresa con los parametros ingresados")

class GetEmpresasByFilters(generics.ListAPIView):
    serializer_class = EmpresaSerializer
    queryset = Personas.objects.all().filter(representante_legal__isnull=False)

    def get(self, request):
        filter = {}
        for key,value in request.query_params.items():
            if key in ['tipo_persona','tipo_documento','numero_documento', 'razon_social','nombre_comercial']:
                if key in ['razon_social','nombre_comercial']:
                    if value != "":
                        filter[key+'__icontains'] = value
                if key in ['numero_documento']:
                    if value != "":
                        filter[key+'__icontains'] = value
                else:
                    if value != "":
                        filter[key] = value
        empresas = self.queryset.filter(**filter)
        if empresas:
            serializador = self.serializer_class(empresas, many=True)
            return Response({'success':True, 'detail': 'Se encontraron las siguientes empresas', 'data': serializador.data}, status=status.HTTP_200_OK)
        else:
            raise NotFound("No existen empresas con los criterios de busqueda especificados")
        
class GetApoderadosByPoderdanteId(generics.ListAPIView):
    serializer_class = PersonasFilterSerializer
    queryset = Personas.objects.all()
    def get(self, request, id_poderdante):
        # fecha_actual = datetime.strptime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
        apoderados_serializer = []
        apoderados = ApoderadoPersona.objects.filter(Q(persona_poderdante=id_poderdante) & Q(Q(fecha_cierre__gte = datetime.now()) | Q(fecha_cierre = None)))
        if apoderados:
            for apoderado in apoderados:
                apoderado_persona = self.queryset.filter(id_persona=apoderado.persona_apoderada_id).first()
                if(apoderado_persona):
                    apoderados_serializer.append(apoderado_persona)
            serializador = self.serializer_class(apoderados_serializer, many=True)
            return Response({'success':True, 'detail': 'Se encontraron los siguientes apoderados', 'data': serializador.data}, status=status.HTTP_200_OK)
        else:
            raise NotFound("No existen apoderados para el poderdante seleccionado")


# class ValidacionTokenView(generics.ListAPIView):
#     permission_classes = [IsAuthenticated]  

#     def get(self, request, *args, **kwargs):
#         received_token = request.query_params.get('token', None)

#         if received_token is None:
#             return Response({'success':False, 'detail':'No se ha ingresado el token.'}, status=status.HTTP_400_BAD_REQUEST)

#         generated_token = request.user

#         try:
#             decoded_token = jwt.decode(received_token, settings.SECRET_KEY, algorithms=['HS256'])
#             if decoded_token['user_id'] != generated_token.id_usuario:
#                 return Response({'success':False, 'detail':'El token no coincide con el usuario autenticado.'}, status=status.HTTP_401_UNAUTHORIZED)
#             return Response({'success':True, 'detail':'El token es válido y coincide con el usuario autenticado.'}, status=status.HTTP_200_OK)
#         except jwt.ExpiredSignatureError:
#             return Response({'success':False, 'detail':'El token ha expirado'}, status=status.HTTP_401_UNAUTHORIZED)
#         except jwt.DecodeError:
#             return Response({'success':False, 'detail':'El token no es valido'}, status=status.HTTP_401_UNAUTHORIZED)


class ValidacionTokenView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        received_token = request.query_params.get('token', None)

        if received_token is None:
            return Response({'success': False, 'detail': 'No se ha ingresado el token.'}, status=status.HTTP_400_BAD_REQUEST)

        generated_token = request.user

        try:
            decoded_token = jwt.decode(received_token, algorithms=[], options={"verify_signature": False})
            if decoded_token['user_id'] != generated_token.id_usuario:
                return Response({'success': False, 'detail': 'El token no coincide con el usuario autenticado.'}, status=status.HTTP_401_UNAUTHORIZED)
            return Response({'success': True, 'detail': 'El token es válido y coincide con el usuario autenticado.'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError:
            return Response({'success': False, 'detail': 'El token ha expirado'}, status=status.HTTP_401_UNAUTHORIZED)
        except jwt.DecodeError:
            return Response({'success': False, 'detail': 'El token no es válido'}, status=status.HTTP_401_UNAUTHORIZED)
