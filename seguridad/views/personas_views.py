from asyncio import exceptions
from urllib.parse import quote_plus
from django.forms import ValidationError
from rest_framework.exceptions import APIException
from datetime import datetime, date, timedelta
import copy
import datetime as dt
from signal import raise_signal

#
from django.urls import reverse
from django.shortcuts import redirect
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.sites.shortcuts import get_current_site
from gestion_documental.serializers.ventanilla_serializers import AutorizacionNotificacionesSerializer

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
from seguridad.models import (
    Personas,
    TipoDocumento,
    EstadoCivil,
    ApoderadoPersona,
    SucursalesEmpresas,
    HistoricoEmails,
    HistoricoDireccion,
    ClasesTercero,
    ClasesTerceroPersona,
    Cargos,
    User,
    HistoricoCambiosIDPersonas,
    UsuariosRol,
    Roles,
    HistoricoCargosUndOrgPersona
)

from almacen.models import UnidadesOrganizacionales

from rest_framework import filters
from seguridad.serializers.personas_serializers import (
    EstadoCivilSerializer,
    EstadoCivilPostSerializer,
    EstadoCivilPutSerializer,
    GetClaseTerceroSerializers,
    PersonaNaturalPostAdminSerializer,
    PersonaNaturalUpdateAdminSerializer,
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
    SucursalesEmpresasSerializer,
    SucursalesEmpresasPostSerializer,
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
    UpdatePersonasJuridicasSerializer
)

# Views for Estado Civil


class GetEstadoCivil(generics.ListAPIView):
    serializer_class = EstadoCivilSerializer
    permission_classes = [IsAuthenticated, PermisoConsultarEstadoCivil]
    queryset = EstadoCivil.objects.filter(activo=True)


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
                    return Response({'success': False,'detail': 'Este estado civil ya está siendo usado, por lo cúal no es eliminable'}, status=status.HTTP_403_FORBIDDEN)   
  
                estado_civil.delete()    
                return Response({'success': True, 'detail': 'Este estado civil ha sido eliminado exitosamente'}, status=status.HTTP_200_OK)
            else:
                return Response({'success': False, 'detail': 'No puedes eliminar un estado civil precargado'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'success': False, 'detail':'No existe el estado civil'}, status=status.HTTP_404_NOT_FOUND)


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
                    return Response({'success':False, 'detail': 'Este estado civil ya está siendo usado, por lo cúal no es actualizable'}, status=status.HTTP_403_FORBIDDEN)
    
                serializer = self.serializer_class(estado_civil, data=request.data, many=False)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response({'success': True,'detail': 'Registro actualizado exitosamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)
            else:
                return Response({'success': False, 'detail': 'No puede actualizar un estado civil precargado'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'success': False, 'detail': 'No existe un estado civil con estos parametros'}, status=status.HTTP_404_NOT_FOUND)


# Views for Tipo Documento


class GetTipoDocumento(generics.ListAPIView):
    serializer_class = TipoDocumentoSerializer
    permission_classes = [IsAuthenticated, PermisoConsultarTipoDocumento]
    queryset = TipoDocumento.objects.filter(activo=True)


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
                    return Response({'success': False,'detail': 'Este tipo de documento ya está siendo usado, por lo cúal no es eliminable'}, status=status.HTTP_403_FORBIDDEN)   
                
                tipo_documento.delete()    
                return Response({'success': True,'detail': 'Este tipo de documento ha sido eliminado exitosamente'}, status=status.HTTP_200_OK)
            else:
                return Response({'success': False,'detail': 'No puedes eliminar un tipo de documento precargado'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'success':False, 'detail': 'No se encontró ningún tipo de documento con estos parámetros'}, status=status.HTTP_404_NOT_FOUND)


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
                    return Response({'success': False,'detail': 'Este tipo de documento ya está siendo usado, por lo cúal no es actualizable'}, status=status.HTTP_403_FORBIDDEN)
                
                serializer = self.serializer_class(tipo_documento, data=request.data, many=False)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                return Response({'success': True,'detail': 'Registro actualizado exitosamente', 'data': serializer.data}, status=status.HTTP_201_CREATED)
            else:
                return Response({'success': False, 'detail': 'Este es un dato precargado en el sistema, no se puede actualizar'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'success': False, 'detail':'No se encontró ningún tipo de documento con estos parámetros'}, status=status.HTTP_404_NOT_FOUND)
            

# Views for Personas

# class GetPersonas(generics.ListAPIView):
#     serializer_class = PersonasSerializer
#     permission_classes = [IsAuthenticated, PermisoConsultarPersona]
#     queryset = Personas.objects.all()


# @api_view(['GET'])
# def getPersonaByEmail(request, pk):
#     try:
#         persona = Personas.objects.get(email=pk)
#         serializer = PersonasSerializer(persona, many=False)
#         return Response({'success': True, 'data': serializer.data,},  status=status.HTTP_200_OK)
#     except:
#         return Response({'success': False ,"message": "No existe una persona con este email"}, status=status.HTTP_404_NOT_FOUND)


class GetPersonasByTipoDocumentoAndNumeroDocumento(generics.GenericAPIView):
    serializer_class = PersonasFilterSerializer
    queryset = Personas.objects.all()
    
    def get(self, request, tipodocumento, numerodocumento):
        persona = self.queryset.all().filter(tipo_documento=tipodocumento, numero_documento=numerodocumento).first()
        if persona:
            persona_serializer = self.serializer_class(persona)
            if not persona.email:
                return Response({'success':False,'detail':'El documento ingresado existe en el sistema, sin embargo no tiene un correo electrónico de notificación asociado, debe acercarse a Cormacarena y realizar una actualizacion  de datos para proceder con la creación del usuario en el sistema', 'data':persona_serializer.data},status=status.HTTP_403_FORBIDDEN)
            return Response({'success': True, 'detail':'Se encontró la siguiente persona', 'data': persona_serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success': True, 'detail': 'No existe una persona con los parametros ingresados'}, status=status.HTTP_200_OK)

class GetPersonasByID(generics.GenericAPIView):
    serializer_class = PersonasSerializer
    queryset = Personas.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        persona = Personas.objects.filter(id_persona=pk).first()
        if persona:
            persona_serializer = self.serializer_class(persona)
            if not persona.email:
                return Response({'success':False,'detail':'El documento ingresado existe en el sistema, sin embargo no tiene un correo electrónico de notificación asociado, debe acercarse a Cormacarena y realizar una actualizacion  de datos para proceder con la creación del usuario en el sistema', 'data':persona_serializer.data},status=status.HTTP_403_FORBIDDEN)
            return Response({'success': True, 'detail':'Se encontró la persona.','data': persona_serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False,'detail': 'No encontró ninguna persona con los parametros ingresados'}, status=status.HTTP_404_NOT_FOUND)
        
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
        return Response({'success':False,'detail':'No está asociado en ninguna empresa como representante legal'},status=status.HTTP_404_NOT_FOUND)
        
class UpdatePersonaNaturalByself(generics.RetrieveUpdateAPIView):
    http_method_names = ['patch']
    serializer_class = PersonaNaturalUpdateSerializer
    permission_classes = [IsAuthenticated]
    
    def patch(self, request):
        data = request.data
        persona = request.user.persona
        previous_persona = copy.copy(persona)
        
        if persona.tipo_persona != "N":
            return Response ({'success':False,'detail':'No se puede actualizar una persona jurídica con este servicio'},status=status.HTTP_403_FORBIDDEN)
        
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
            return Response({'success': validaciones_persona['success'], 'detail':validaciones_persona['detail']}, status=validaciones_persona['status'])       
        
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
    
        return Response({'success': True, 'detail': 'Persona actualizada correctamente', 'data': persona_serializada.data}, status=status.HTTP_201_CREATED)
    
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
                    return Response({'success':False,"detail":"No se puede dejar en blanco debido a que ya había una dirección de notificación"},status=status.HTTP_403_FORBIDDEN)
                
            if persona.tipo_persona != "N":
                return Response ({'success':False,'detail':'No se puede actualizar una persona jurídica con este servicio'},status=status.HTTP_403_FORBIDDEN)
                
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
                return Response({'success': validaciones_persona['success'], 'detail':validaciones_persona['detail']}, status=validaciones_persona['status'])       
            
            validaciones_cargo = Util.actualizacion_clase_tercero_admin(persona,request)
            
            if not validaciones_cargo['success']:
                return Response({'success': validaciones_cargo['success'], 'detail':validaciones_cargo['detail']}, status=validaciones_cargo['status'])       
        
            persona_actualizada = persona_serializada.save()
            
            if validaciones_cargo['actualizado'] == True and not cambio:

                persona_actualizada.fecha_ultim_actualiz_diferente_crea = datetime.now()
                persona_actualizada.id_persona_ultim_actualiz_diferente_crea = request.user.persona
                persona_actualizada.save()
            
            # AUDITORIA ACTUALIZAR PERSONA
            descripcion = {"TipodeDocumentoID": str(persona_actualizada.tipo_documento.cod_tipo_documento), "NumeroDocumentoID": str(persona_actualizada.numero_documento), "PrimerNombre": str(persona_actualizada.primer_nombre), "PrimerApellido": str(persona_actualizada.primer_apellido)}
            direccion=Util.get_client_ip(request)

            auditoria_data = {
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
        
            return Response ({'success':True,'detail':'Se actualizó la persona correctamente','data':persona_serializada.data},status=status.HTTP_200_OK)
        
        return Response ({'success':False,'detail':'No existe la persona'},status=status.HTTP)
    
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
                return Response ({'success':False,'detail':'No se puede actualizar una persona jurídica con este servicio'},status=status.HTTP_403_FORBIDDEN)
        
            cambio = Util.comparacion_campos_actualizados(data,persona)
            if persona_logueada != persona.id_persona_crea.id_persona:
                if cambio:
                    print(cambio)
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
                    if fecha_formateada > fecha_ahora or fecha_formateada <= persona.fecha_inicio_cargo_rep_legal.date():
                        return Response({'success':False,'detail':'La fecha de inicio del cargo del representante no debe ser superior a la del sistema y tiene que ser mayor a la fecha de inicio del representante legal anterior'}, status=status.HTTP_403_FORBIDDEN)

            else:
                fecha_inicio = data.get("fecha_inicio_cargo_rep_legal")
                if fecha_inicio: 
                
                    fecha_formateada = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                    print()
                    if persona.fecha_inicio_cargo_rep_legal.date() != fecha_formateada:
                        return Response({'success':False,'detail':'No se puede actualizar la fecha de inicio de representante legal sin haber cambiado el representante'},status=status.HTTP_403_FORBIDDEN)
                    
                data['fecha_cambio_representante_legal'] = None
                
            persona_serializada = self.serializer_class(persona, data=data, many=False)
            persona_serializada.is_valid(raise_exception=True)
            
            #PARA UTILIZARLO EN EL UTIL
            data['tipo_persona'] = persona.tipo_persona
            
            validaciones_persona = Util.guardar_persona(data)
            
            if not validaciones_persona['success']:
                return Response({'success': validaciones_persona['success'], 'detail':validaciones_persona['detail']}, status=validaciones_persona['status'])       
            
            validaciones_cargo=Util.actualizacion_clase_tercero_admin(persona,request)
            
            if not validaciones_cargo['success']:
                return Response({'success': validaciones_cargo['success'], 'detail':validaciones_cargo['detail']}, status=validaciones_cargo['status'])       
        
            persona_actualizada= persona_serializada.save()
            
            if validaciones_cargo['actualizado'] == True and not cambio:
                print("ENTRÓ")
                persona_actualizada.fecha_ultim_actualiz_diferente_crea = datetime.now()
                persona_actualizada.id_persona_ultim_actualiz_diferente_crea = request.user.persona
                persona_actualizada.save()
            
            return Response ({'success':True,'detail':'Se actualizó la persona correctamente','data':persona_serializada.data},status=status.HTTP_200_OK)
        
        return Response ({'success':False,'detail':'No existe la persona'},status=status.HTTP)


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
            return Response({'success': validaciones_persona['success'], 'detail':validaciones_persona['detail']}, status=validaciones_persona['status'])       

        serializador = serializer.save()

        # VALIDAR EXISTENCIA CLASES TERCERO
        clases_tercero = ClasesTercero.objects.filter(id_clase_tercero__in = persona['datos_clasificacion_persona'])
        if len(set(persona['datos_clasificacion_persona'])) != len(clases_tercero):
            return Response({'success':False, 'detail':'Debe validar que todas las clases tercero elegidas existan'}, status=status.HTTP_400_BAD_REQUEST)
        
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
        
        return Response({'success':True, 'detail': 'Se creo la persona jurídica correctamente', 'data':serializer.data}, status=status.HTTP_201_CREATED)

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
            return Response({'success': validaciones_persona['success'], 'detail':validaciones_persona['detail']}, status=validaciones_persona['status'])       

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
            else: return Response({'success':False,'detail':'La clase tercero '+str(clase_tercero)+" no existe"},status=status.HTTP_403_FORBIDDEN)

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
        
        return Response({'success':True, 'detail': 'Se creo la persona jurídica correctamente', 'data':serializer.data}, status=status.HTTP_201_CREATED)


class GetClasesTerceroByPersona(generics.ListAPIView):
    serializer_class = GetClaseTerceroSerializers
    queryset = ClasesTercero.objects.all()
    
    
    def get (self,request,id_persona):
        
        persona = Personas.objects.filter(id_persona=id_persona).first()
    
        if persona:
            
            clases_tercero_persona = ClasesTerceroPersona.objects.filter(id_persona = id_persona)
            if clases_tercero_persona:
                list_clases_tercero = [clases.id_clase_tercero for clases in clases_tercero_persona]
                
                serializador = self.serializer_class(list_clases_tercero,many =True)
            
                return Response ({'success':True,'detail':'Se encontraron clases tercero para la persona seleccionada','data':serializador.data},status=status.HTTP_200_OK)
            
            return Response({'success':True,'detail':'No se encontraron clases tercero para la persona seleccionada'},status=status.HTTP_200_OK)
        return Response({'success':False,'detail':'No existe la persona'},status=status.HTTP_403_FORBIDDEN)
        

# class UpdatePersonaNaturalByUserWithPermissions(generics.RetrieveUpdateAPIView):
#     http_method_names= ['patch']
#     serializer_class = PersonaNaturalUpdateUserPermissionsSerializer
#     serializer_historico = HistoricoCargosUndOrgPersonapostSerializer
#     permission_classes = [IsAuthenticated, PermisoActualizarPersona]
#     queryset = Personas.objects.all()

#     def patch(self, request, tipodocumento, numerodocumento):
#         datos_historico_unidad = {}
#         datos_ingresados = request.data

#         bandera = False
#         persona_por_actualizar = Personas.objects.filter(Q(tipo_documento=tipodocumento) & Q(numero_documento=numerodocumento) & Q(tipo_persona='N')).first()
#         if not persona_por_actualizar:
#             return Response({'success': False, 'detail': 'No existe ningúna persona con los parámetros enviados'}, status=status.HTTP_404_NOT_FOUND)
#         datos_ingresados['fecha_asignacion_unidad'] = datetime.now()
#         usuario = User.objects.filter(persona = persona_por_actualizar.id_persona).first()
#         if not usuario:
#             return Response({'success': False, 'detail': 'Esta persona no tiene un usuario asignado'}, status=status.HTTP_404_NOT_FOUND)
#         previous_persona = copy.copy(persona_por_actualizar)
        
#         if datos_ingresados['id_unidad_organizacional_actual'] and usuario.tipo_usuario != 'I':
#             return Response({'success': False, 'detail': 'No se puede asignar una unidad organizacional a un usuario que no sea interno'}, status=status.HTTP_400_BAD_REQUEST)

#         if persona_por_actualizar.id_unidad_organizacional_actual:
#             bandera = True

#             datos_historico_unidad['id_persona'] = persona_por_actualizar.id_persona
#             datos_historico_unidad['id_cargo'] = persona_por_actualizar.id_cargo.id_cargo
#             datos_historico_unidad['id_unidad_organizacional'] = persona_por_actualizar.id_unidad_organizacional_actual.id_unidad_organizacional
#             datos_historico_unidad['justificacion_cambio_und_org'] = datos_ingresados['justificacion_cambio_und_org']
#             datos_historico_unidad['fecha_inicial_historico'] = datetime.now()
#             datos_historico_unidad['fecha_final_historico'] = datetime.now()
        
#         if datos_ingresados['id_unidad_organizacional_actual']:
#             datos_ingresados['es_unidad_organizacional_actual'] = True
#         datos_ingresados.pop('justificacion_cambio_und_org')
        
#         persona_serializada = self.serializer_class(persona_por_actualizar, data=datos_ingresados, many=False)
#         persona_serializada.is_valid(raise_exception=True)
        
#         estado_civil = persona_serializada.validated_data.get('estado_civil')
#         if estado_civil:
#             estado_civil_instance = EstadoCivil.objects.filter(cod_estado_civil=estado_civil.cod_estado_civil).first()
#             if not estado_civil_instance:
#                 return Response({'success': False, 'detail': 'No existe el estado civil que está ingresando'}, status=status.HTTP_400_BAD_REQUEST) 

#                 # validacion email diferentes 
#             email_secundario = persona_serializada.validated_data.get('email_empresarial')
#             if email_secundario:
#                 validate_second_email = Util.validate_dns(email_secundario)
#                 if validate_second_email == False:
#                     return Response({'success': False, 'detail': 'Valide que el email secundario ingresado exista'}, status=status.HTTP_400_BAD_REQUEST)
            
#             email_principal = persona_serializada.validated_data.get('email')
#             validate_email = Util.validate_dns(email_principal)
#             if validate_email == False:
#                 return Response({'success': False, 'detail': 'Valide que el email principal ingresado exista'}, status=status.HTTP_400_BAD_REQUEST)
            
#             persona_email_validate = Personas.objects.filter(Q(email_empresarial=email_principal) | Q(email=email_secundario))
#             if len(persona_email_validate):
#                 return Response({'success': False, 'detail': 'Ya existe una persona con este email asociado como email principal o secundario'}, status=status.HTTP_400_BAD_REQUEST)
                    
#             if email_principal == email_secundario:
#                 return Response({'success': False, 'detail': 'El correo de notificaciones y el secundario deben ser diferentes'}, status=status.HTTP_400_BAD_REQUEST)
#             else:
#                 serializador = persona_serializada.save()
#             # validación correo principal obligatorio 
#             if not email_principal:
#                 return Response({'success':False,'detail': 'El email de notificaciones es obligatorio'}, status=status.HTTP_400_BAD_REQUEST)
         
#             if bandera:
#                 historico_serializado = self.serializer_historico(data=datos_historico_unidad, many=False)
#                 historico_serializado.is_valid(raise_exception=True)
#                 historico_serializado.save()
                
#             # auditoria actualizar persona
#             usuario = request.user.id_usuario
#             direccion=Util.get_client_ip(request)
#             descripcion = {"TipodeDocumentoID": str(serializador.tipo_documento), "NumeroDocumentoID": str(serializador.numero_documento), "PrimerNombre": str(serializador.primer_nombre), "PrimerApellido": str(serializador.primer_apellido)}
#             valores_actualizados = {'current': persona_por_actualizar, 'previous': previous_persona}

#             auditoria_data = {
#                 "id_usuario" : usuario,
#                 "id_modulo" : 1,
#                 "cod_permiso": "AC",
#                 "subsistema": 'TRSV',
#                 "dirip": direccion,
#                 "descripcion": descripcion, 
#                 "valores_actualizados": valores_actualizados
#             }
#             Util.save_auditoria(auditoria_data)
            
#             #SMS y EMAILS
#             persona = Personas.objects.get(email=email_principal)
            
#             sms = 'Actualizacion exitosa de persona Natural en Cormacarena por administrador.'
#             context = {'primer_nombre': persona.primer_nombre, 'primer_apellido': persona.primer_apellido}
#             template= render_to_string(('email-update-personanatural-byuser-withpermissions.html'), context)
#             subject = 'Actualización de datos exitosa ' + persona.primer_nombre
#             data = {'template': template, 'email_subject': subject, 'to_email': persona.email}
#             Util.send_email(data)
#             try:
#                 Util.send_sms(persona.telefono_celular, sms)
#             except:
#                 return Response({'success': True, 'detail': 'Se actualizó la persona pero no se pudo enviar el mensaje, verificar numero o servicio'}, status=status.HTTP_201_CREATED)
#             return Response({'success':True,'message': 'Persona actualizada y notificada exitosamente', 'data': persona_serializada.data}, status=status.HTTP_201_CREATED)

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
            return Response ({'success':False,'detail':'No se puede actualizar una persona natural con este servicio'},status=status.HTTP_403_FORBIDDEN)
            
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
                if fecha_formateada > fecha_ahora or fecha_formateada <= persona.fecha_inicio_cargo_rep_legal.date():
                    return Response({'success':False,'detail':'La fecha de inicio del cargo del representante no debe ser superior a la del sistema y tiene que ser mayor a la fecha de inicio del representante legal anterior'}, status=status.HTTP_403_FORBIDDEN)

        else:
            fecha_inicio = data.get("fecha_inicio_cargo_rep_legal")
            if fecha_inicio: 
            
                fecha_formateada = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
                print()
                if persona.fecha_inicio_cargo_rep_legal.date() != fecha_formateada:
                    return Response({'success':False,'detail':'No se puede actualizar la fecha de inicio de representante legal sin haber cambiado el representante'},status=status.HTTP_403_FORBIDDEN)
                
            data['fecha_cambio_representante_legal'] = None
        
        persona_serializada = self.serializer_class(persona, data=data, many=False)
        persona_serializada.is_valid(raise_exception=True)
        
        #PARA UTULIZARLO EN EL UTIL
        data['tipo_persona'] = persona.tipo_persona
        
        validaciones_persona = Util.guardar_persona(data)
        
        if not validaciones_persona['success']:
            return Response({'success': validaciones_persona['success'], 'detail':validaciones_persona['detail']}, status=validaciones_persona['status'])       
        
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
        
        return Response({'success': True, 'detail': 'Persona actualizada correctamente', 'data': persona_serializada.data}, status=status.HTTP_201_CREATED)
        
# class UpdatePersonaJuridicaByUserWithPermissions(generics.RetrieveUpdateAPIView):
#     http_method_names = ['patch']
#     serializer_class = PersonaJuridicaUpdateUserPermissionsSerializer
#     permission_classes = [IsAuthenticated, PermisoActualizarPersona]
#     queryset = Personas.objects.all()

#     def patch(self, request, tipodocumento, numerodocumento):
#         try:
#             persona_por_actualizar = Personas.objects.get(Q(tipo_documento=tipodocumento) & Q(numero_documento=numerodocumento) & Q(tipo_persona='J'))           
#             previous_persona = copy.copy(persona_por_actualizar)
#             try:
#                 persona_serializada = self.serializer_class(persona_por_actualizar, data=request.data, many=False)
#                 persona_serializada.is_valid(raise_exception=True)
#                 try:
#                     email_principal = persona_serializada.validated_data.get('email')
#                     email_secundario = persona_serializada.validated_data.get('email_empresarial')

#                     # validacion email diferentes 
#                     if email_secundario:
#                         validate_second_email = Util.validate_dns(email_secundario)
#                         if validate_second_email == False:
#                             return Response({'success': False, 'detail': 'Valide que el email secundario ingresado exista'}, status=status.HTTP_400_BAD_REQUEST)
        
#                     validate_email = Util.validate_dns(email_principal)
#                     if validate_email == False:
#                         return Response({'success': False, 'detail': 'Valide que el email principal ingresado exista'}, status=status.HTTP_400_BAD_REQUEST)
            
#                     persona_email_validate = Personas.objects.filter(Q(email_empresarial=email_principal) | Q(email=email_secundario))
#                     if len(persona_email_validate):
#                         return Response({'success': False, 'detail': 'Ya existe una persona con este email asociado como email principal o secundario'}, status=status.HTTP_400_BAD_REQUEST)
                    
#                     # validación correo principal obligatorio 
#                     if not email_principal:
#                         return Response({'success':False,'detail': 'El email de notificaciones es obligatorio'}, status=status.HTTP_400_BAD_REQUEST)
        
#                     if email_principal == email_secundario:
#                         return Response({'success': False, 'detail': 'El correo de notificaciones y el secundario deben ser diferentes'}, status=status.HTTP_400_BAD_REQUEST)
#                     else:
#                         serializador = persona_serializada.save()
                    
#                     if persona_por_actualizar.representante_legal == previous_persona.representante_legal:
#                         fecha_actual = persona_por_actualizar.fecha_cambio_representante_legal
#                     else:
#                         fecha_actual = dt.datetime.now()  
#                         persona_por_actualizar.fecha_cambio_representante_legal = fecha_actual
#                     persona_por_actualizar.save()
                    
#                     # auditoria actualizar persona
#                     usuario = request.user.id_usuario
#                     direccion=Util.get_client_ip(request)
#                     descripcion = {"TipodeDocumentoID": str(serializador.tipo_documento), "NumeroDocumentoID": str(serializador.numero_documento), "RazonSocial": str(serializador.razon_social), "NombreComercial": str(serializador.nombre_comercial)}
#                     valores_actualizados = {'current': persona_por_actualizar, 'previous': previous_persona}

#                     auditoria_data = {
#                         "id_usuario" : usuario,
#                         "id_modulo" : 1,
#                         "cod_permiso": "AC",
#                         "subsistema": 'TRSV',
#                         "dirip": direccion,
#                         "descripcion": descripcion, 
#                         "valores_actualizados": valores_actualizados
#                     }
#                     Util.save_auditoria(auditoria_data)    
                        
#                     #SMS y EMAILS
#                     persona = Personas.objects.get(email=email_principal)

#                     sms = 'Hola ' + str(persona.razon_social) + ' te informamos que ha sido exitosa la actualización de tus datos como PERSONA JURIDICA'
#                     context = {'razon_social': persona.razon_social}
#                     template = render_to_string(('email-update-personajuridica-byuser-withpermissions.html'), context)
#                     subject = 'Actualización de datos exitosa ' + str(persona.razon_social)
#                     data = {'template': template, 'email_subject': subject, 'to_email': persona.email} 
#                     Util.send_email(data)
#                     try:
#                         Util.send_sms(persona.telefono_celular_empresa, sms)
#                     except:
#                         return Response({'success':True,'detail': 'Se actualizó la persona pero no se pudo enviar el mensaje, verificar numero o servicio'}, status=status.HTTP_201_CREATED)
#                     return Response({'success':True,'detail': 'Persona actualizada y notificada exitosamente', 'data': persona_serializada.data}, status=status.HTTP_201_CREATED)
#                 except:
#                     return Response({'success':False,'detail': 'No pudo obtener el email principal y/o secundario'}, status=status.HTTP_400_BAD_REQUEST)
#             except:
#                 return Response({'success':False,'detail': 'Revisar parámetros de ingreso de información, el email debe ser único y debe tener telefono celular empresa'}, status=status.HTTP_400_BAD_REQUEST)
#         except:
#             return Response({'success':False,'detail': 'No existe ninguna persona con estos datos, por favor verificar'}, status=status.HTTP_400_BAD_REQUEST)

# class RegisterPersonaNaturalByUserInterno(generics.CreateAPIView):
#     serializer_class = PersonaNaturalPostByUserSerializer
#     permission_classes = [IsAuthenticated, PermisoCrearPersona]
    
#     def post(self, request):
#         persona = request.data
#         serializer = self.serializer_class(data=persona)
#         serializer.is_valid(raise_exception=True)

#         #Marcar tipo de documento como item ya usado
#         tipo_documento_usado = serializer.validated_data.get('tipo_documento')
#         try:
#             tipo_documento_instance = TipoDocumento.objects.get(cod_tipo_documento=tipo_documento_usado.cod_tipo_documento)
#             pass
#         except:
#             return Response({'success': False, 'detail': 'No existe el tipo de documento que está ingresando'}, status=status.HTTP_400_BAD_REQUEST)

#         email_principal = serializer.validated_data.get('email')
#         email_secundario = serializer.validated_data.get('email_empresarial')

#         #Validación de persona natural
#         tipo_persona = serializer.validated_data.get('tipo_persona')
#         if tipo_persona != 'N':
#             return Response({'success':False,'detail':'El tipo de persona debe ser Natural'}, status=status.HTTP_400_BAD_REQUEST)

#         #Validación de tipo documento
#         tipo_documento = serializer.validated_data.get('tipo_documento')
#         if tipo_documento.cod_tipo_documento == 'NT':
#             return Response({'success':False,'detail':'El tipo de documento debe ser el de una persona natural'}, status=status.HTTP_400_BAD_REQUEST)
        
#         #Validación emails dns
#         validate_email = Util.validate_dns(email_principal)
#         if validate_email == False:
#             return Response({'success':False,'detail': 'Valide que el email principal ingresado exista'}, status=status.HTTP_400_BAD_REQUEST)

#         if email_secundario:
#             validate_second_email = Util.validate_dns(email_secundario)
#             if validate_second_email == False:
#                 return Response({'success':False,'detail': 'Valide que el email secundario ingresado exista'}, status=status.HTTP_400_BAD_REQUEST)

#         # validación correo principal obligatorio 
#         if not email_principal:
#             return Response({'success':False,'detail': 'El email de notificaciones es obligatorio'}, status=status.HTTP_400_BAD_REQUEST)
        
#         # validacion de email entrante vs existente
#         persona_email_validate = Personas.objects.filter(Q(email=email_secundario))
#         if len(persona_email_validate):
#             return Response({'success':False,'detail': 'Ya existe una persona con este email asociado como email secundario'}, status=status.HTTP_400_BAD_REQUEST)
#         else:
#             serializador = serializer.save()
            
#             # auditoria crear persona
#             usuario = request.user.id_usuario
#             descripcion = {"TipodeDocumentoID": str(serializador.tipo_documento), "NumeroDocumentoID": str(serializador.numero_documento), "PrimerNombre": str(serializador.primer_nombre), "PrimerApellido": str(serializador.primer_apellido)}
#             direccion=Util.get_client_ip(request)

#             auditoria_data = {
#                 "id_usuario" : usuario,
#                 "id_modulo" : 1,
#                 "cod_permiso": "CR",
#                 "subsistema": 'TRSV',
#                 "dirip": direccion,
#                 "descripcion": descripcion, 
#             }
#             Util.save_auditoria(auditoria_data)

#             # envio de emails y sms
#             persona = Personas.objects.filter(tipo_documento=persona['tipo_documento'],numero_documento=persona['numero_documento']).first()
    
#             sms = 'Hola '+ persona.primer_nombre + ' ' + persona.primer_apellido + ' te informamos que has sido registrado como PERSONA NATURAL en el portal Bia Cormacarena \n Ahora puedes crear tu usuario, hazlo en el siguiente link' + 'url'  
#             context = {'primer_nombre': persona.primer_nombre, 'primer_apellido':  persona.primer_apellido}
#             template = render_to_string(('email-register-personanatural.html'), context)
#             subject = 'Registro exitoso ' + persona.primer_nombre
#             data = {'template': template, 'email_subject': subject, 'to_email': persona.email}
#             Util.send_email(data)
#             try:
#                 Util.send_sms(persona.telefono_celular, sms)
#             except:
#                 return Response({'success':True,'detail': 'Se guardo la persona pero no se pudo enviar el sms, verificar numero'}, status=status.HTTP_201_CREATED)
#             return Response({'success':True, 'detail': serializer.data, 'message': 'Se ejecutó todo exitosamente'}, status=status.HTTP_201_CREATED)

# Views for apoderados persona


"""class getApoderadosPersona(generics.ListAPIView):
    serializer_class = ApoderadoPersonaSerializer
    queryset = ApoderadoPersona.objects.all()


class getApoderadoPersonaById(generics.RetrieveAPIView):
    serializer_class = ApoderadoPersonaSerializer
    queryset = ApoderadoPersona.objects.all()


class deleteApoderadoPersona(generics.DestroyAPIView):
    serializer_class = ApoderadoPersonaSerializer
    queryset = ApoderadoPersona.objects.all()


class updateApoderadoPersona(generics.RetrieveUpdateAPIView):
    serializer_class = ApoderadoPersonaPostSerializer
    queryset = ApoderadoPersona.objects.all()


class registerApoderadoPersona(generics.CreateAPIView):
    serializer_class = ApoderadoPersonaPostSerializer 
    queryset = ApoderadoPersona.objects.all()"""


# Views for Sucursales Empresas


class getSucursalesEmpresas(generics.ListAPIView):
    serializer_class = SucursalesEmpresasSerializer
    queryset = SucursalesEmpresas.objects.all()


class getSucursalEmpresaById(generics.RetrieveAPIView):
    serializer_class = SucursalesEmpresasSerializer
    queryset = SucursalesEmpresas.objects.all()


class deleteSucursalEmpresa(generics.DestroyAPIView):
    serializer_class = SucursalesEmpresasSerializer
    queryset = SucursalesEmpresas.objects.all()
    permission_classes = [IsAuthenticated]
    
    def delete(self,request,pk):
        sucursal=SucursalesEmpresas.objects.filter(id_sucursal_empresa=pk).first()

        if sucursal:
            persona_empresa=sucursal.id_persona_empresa
            sucursal.delete()
            persona=Personas.objects.get(id_persona=persona_empresa.id_persona)
            usuario = request.user.id_usuario
            dirip = Util.get_client_ip(request)
            descripcion ={ "nombre razón social": str(persona.razon_social),"sucursal" :str(sucursal.sucursal)}
            auditoria_data = {
                'id_usuario': usuario,
                'id_modulo': 1,
                'cod_permiso': 'BO',
                'subsistema': 'TRSV',
                'dirip': dirip,
                'descripcion': descripcion,
            }
            
            Util.save_auditoria(auditoria_data)

            return Response({'success':True,'detail':'La sucursal empresa fue eliminada'}, status=status.HTTP_200_OK)
        else:
            return Response({'success':False,'detail':'No existe sucursal'}, status=status.HTTP_400_BAD_REQUEST)
            
class updateSucursalEmpresa(generics.RetrieveUpdateAPIView):
    serializer_class = SucursalesEmpresasPostSerializer
    queryset = SucursalesEmpresas.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self, request,pk=None):
        sucursal = SucursalesEmpresas.objects.filter(id_sucursal_empresa= pk).first()
        previous_sucursal = copy.copy(sucursal)
        if sucursal:
            sucursal_serializer = self.serializer_class(sucursal, data=request.data)
            sucursal_serializer.is_valid(raise_exception=True)
            sucursal_serializer.save()
            
            usuario = request.user.id_usuario
            persona=Personas.objects.get(id_persona=request.data['id_persona_empresa'])
            dirip = Util.get_client_ip(request)
            descripcion ={ "nombre razón social": str(persona.razon_social),"sucursal" :str(sucursal.sucursal)}
            valores_actualizados={'current':sucursal, 'previous':previous_sucursal}

            auditoria_data = {
                'id_usuario': usuario,
                'id_modulo': 1,
                'cod_permiso': 'AC',
                'subsistema': 'TRSV',
                'dirip': dirip,
                'descripcion': descripcion,
                'valores_actualizados': valores_actualizados
            }
            
            Util.save_auditoria(auditoria_data)
            return Response({'success':True,'detail':'la sucursal empresa actualizada'}, status=status.HTTP_201_CREATED)
        else:
            return Response({'success':False,'detail':'No existe sucursal'}, status=status.HTTP_400_BAD_REQUEST)

class registerSucursalEmpresa(generics.CreateAPIView):
    serializer_class = SucursalesEmpresasPostSerializer 
    queryset = SucursalesEmpresas.objects.all()
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializador=serializer.save()
        usuario = request.user.id_usuario

        persona=Personas.objects.get(id_persona=request.data['id_persona_empresa'])
        dirip = Util.get_client_ip(request)
        descripcion ={ "nombre razón social": str(persona.razon_social),"sucursal" :str(serializador.sucursal)}

        auditoria_data = {
            'id_usuario': usuario,
            'id_modulo': 1,
            'cod_permiso': 'CR',
            'subsistema': 'TRSV',
            'dirip': dirip,
            'descripcion': descripcion,
        }
        
        Util.save_auditoria(auditoria_data)
        headers = self.get_success_headers(serializer.data)
        return Response({'success':True},serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    

        # descripcion = "idUsuario:" + str(serializer_response.pk) + ";" + "fecha:" + formatDate + ";" + "observaciones:Registro de otro usuario" + ";" + "nombreUsuario:"+ serializer_response.nombre_de_usuario + "."
        
# Views for Historico Emails
class getHistoricoEmails(generics.ListAPIView):
    serializer_class = HistoricoEmailsSerializer
    queryset = HistoricoEmails.objects.all()


# Views for Historico Direcciones
class GetHistoricoDirecciones(generics.ListAPIView):
    queryset = HistoricoDireccion.objects.all()
    serializer_class = HistoricoDireccionSerializer

class GetCargosList(generics.ListAPIView):
    serializer_class = CargosSerializer
    queryset = Cargos.objects.all()

    def get(self, request):
        cargos = Cargos.objects.all()
        serializador = self.serializer_class(cargos, many=True)
        if cargos:
            return Response({'success':True, 'detail':'Se encontraron cargos', 'data':serializador.data}, status=status.HTTP_200_OK)
        else:
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
                return Response({'success':False, 'detail':'Este cargo ya está siendo usado, por lo cual no es actualizable'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'success': False, 'detail': 'No existe el cargo'}, status=status.HTTP_404_NOT_FOUND)

class DeleteCargo(generics.DestroyAPIView):
    serializer_class = CargosSerializer
    queryset = Cargos.objects.all()

    def delete(self, request, pk):
        cargo = Cargos.objects.filter(id_cargo=pk).first()
        if cargo:
            if not cargo.item_usado:
                cargo.delete()
                return Response({'success': True, 'detail': 'El cargo ha sido eliminado exitosamente'}, status=status.HTTP_200_OK)
            else:
                return Response({'success':False, 'detail':'Este cargo ya está siendo usado, no se pudo eliminar. Intente desactivar'}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({'success': False, 'detail':'No existe el cargo'}, status=status.HTTP_404_NOT_FOUND)

# class BusquedaPersonaNaturalView(generics.ListAPIView):
#     serializer_class = BusquedaPersonaNaturalSerializer
#     permission_classes = [IsAuthenticated]

#     def get(self,request):
#         tipo_documento = request.GET.get('tipo_documento')
#         numero_documento = request.GET.get('numero_documento')
#         primer_nombre = request.GET.get('primer_nombre')
#         primer_apellido = request.GET.get('primer_apellido')

#         personas = Personas.objects.all()
#         if tipo_documento:
#             personas = personas.filter(tipo_documento=tipo_documento)
#         if numero_documento:
#             personas = personas.filter(numero_documento=numero_documento)
#         if primer_nombre:
#             personas = personas.filter(primer_nombre__icontains=primer_nombre)
#         if primer_apellido:
#             personas = personas.filter(primer_apellido__icontains=primer_apellido)
        
#         if personas.exists():
#             serializer = self.serializer_class(personas, many=True)
#             return Response({'success':True, 'detail':'Se encontraron personas que coinciden con los criterios de búsqueda', 'data':serializer.data}, status=status.HTTP_201_CREATED)
        
#         else:
#             return Response({'success': False, 'detail': 'No se encontraron personas que coincidan con los criterios de búsqueda.'}, status=status.HTTP_404_NOT_FOUND)

class GetPersonasByFilters(generics.ListAPIView):
    serializer_class = PersonasFilterSerializer
    # permission_classes = [IsAuthenticated]
    queryset = Personas.objects.all()

    def get(self,request):
        filter = {}
        
        for key,value in request.query_params.items():
            if key in ['tipo_documento','numero_documento','primer_nombre','primer_apellido','razon_social','nombre_comercial']:
                if key in ['primer_nombre','primer_apellido','razon_social','nombre_comercial']:
                    if value != "":
                        filter[key+'__icontains']=  value
                elif key == "numero_documento":
                    if value != "":
                        filter[key+'__startswith'] = value
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
            return Response({'success':False, 'detail': 'La persona con el id proporcionado no tiene un historico de cambios asociado'}, status=status.HTTP_404_NOT_FOUND)
        cambios_persona = HistoricoCambiosIDPersonas.objects.filter(id_persona=id_persona)
        serializador = self.serializer_class(cambios_persona, many=True)
        return Response({'success':True, 'detail': 'La persona con el id proporcionado tiene un historico asociado', 'data':serializador.data}, status=status.HTTP_200_OK)

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
                return Response({'success': False, 'detail': "El tipo de documento no se puede actualizar a NIT"})
            
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

            ##HISTORICO
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

            return Response({'success': True, 'detail':'Se actualizó los datos de la persona natural','data':serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'detail': 'La persona no existe o es una persona jurídica'}, status=status.HTTP_404_NOT_FOUND)

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

            ##HISTORICO
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

            return Response({'success': True, 'detail': 'Se actualizó los datos de la persona jurídica','data':serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'detail': 'La persona no existe o es una persona natural'}, status=status.HTTP_404_NOT_FOUND)
"""     
# Views for Clases Tercero


class getClasesTercero(generics.ListAPIView):
    queryset = ClasesTercero.objects.all()
    serializer_class = ClasesTerceroSerializer


class getClaseTerceroById(generics.RetrieveAPIView):
    queryset = ClasesTercero.objects.all()
    serializer_class = ClasesTerceroSerializer


class deleteClaseTercero(generics.DestroyAPIView):
    queryset = ClasesTercero.objects.all()
    serializer_class = ClasesTerceroSerializer


class updateClaseTercero(generics.RetrieveUpdateAPIView):
    queryset = ClasesTercero.objects.all()
    serializer_class = ClasesTerceroSerializer


class registerClaseTercero(generics.CreateAPIView):
    queryset = ClasesTercero.objects.all()
    serializer_class = ClasesTerceroSerializer


# Views for Clases Tercero Persona


class getClasesTerceroPersonas(generics.ListAPIView):
    queryset = ClasesTerceroPersona.objects.all()
    serializer_class = ClasesTerceroPersonaSerializer


class getClaseTerceroPersonaById(generics.RetrieveAPIView):
    queryset = ClasesTerceroPersona.objects.all()
    serializer_class = ClasesTerceroPersonaSerializer


class deleteClaseTerceroPersona(generics.DestroyAPIView):
    queryset = ClasesTerceroPersona.objects.all()
    serializer_class = ClasesTerceroPersonaSerializer


class updateClaseTerceroPersona(generics.RetrieveUpdateAPIView):
    queryset = ClasesTerceroPersona.objects.all()
    serializer_class = ClasesTerceroPersonapostSerializer


class registerClaseTerceroPersona(generics.CreateAPIView):
    queryset = ClasesTerceroPersona.objects.all()
    serializer_class = ClasesTerceroPersonapostSerializer
"""

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
            return Response({'success': validaciones_persona['success'], 'detail':validaciones_persona['detail']}, status=validaciones_persona['status'])       
      
        #CREACION DE USUARIO PARA LA PERSONA JURIDICA
        
        redirect_url=request.data.get('redirect_url','')
        redirect_url=quote_plus(redirect_url)
        
        if " " in data['nombre_de_usuario']:
            return Response({'success':False,'detail':'No puede contener espacios en el nombre de usuario'},status=status.HTTP_403_FORBIDDEN)
        
        #GUARDAR PERSONA
        serializador = serializer.save()
        serializador.id_persona_crea = serializador
        serializador.save()
        
        #USUARIO
        data['creado_por_portal'] = True
        data['persona'] = serializador.id_persona
        
        serializer = self.serializer_class_usuario(data=data)
        serializer.is_valid(raise_exception=True)
        nombre_de_usuario = serializer.validated_data.get('nombre_de_usuario')
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
        descripcion = {'nombre_de_usuario': request.data["nombre_de_usuario"]}

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
        descripcion = {'nombre_de_usuario': request.data["nombre_de_usuario"], 'Rol': rol}
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

        #user = User.objects.get(email=user_data['email'])

        token = RefreshToken.for_user(serializer_response)

        current_site=get_current_site(request).domain

        #persona = Personas.objects.get(id_persona = request.data['persona'])

        relativeLink= reverse('verify')
        absurl= 'http://'+ current_site + relativeLink + "?token="+ str(token) + '&redirect-url=' + redirect_url

        # short_url = Util.get_short_url(request, absurl)

        subject = "Verifica tu usuario"
        template = "activación-de-usuario.html"

        Util.notificacion(serializador,subject,template,absurl=absurl)
    
        
        return Response ({'success':True,'detail':'Se creo la persona jurídica y el usuario correctamente'},status=status.HTTP_200_OK)


class CreatePersonaNaturalAndUsuario(generics.CreateAPIView):
    
    serializer_class = PersonaNaturalPostSerializer   
    serializer_class_usuario = RegisterExternoSerializer  
    queryset = Personas.objects.all()
    
    def post(self,request):
        
        data = request.data
        
        #CREACION DE PERSONA
        
        serializer_persona = self.serializer_class(data=data)
        serializer_persona.is_valid(raise_exception=True)

        validaciones_persona = Util.guardar_persona(data)
        
        if not validaciones_persona['success']:
            return Response({'success': validaciones_persona['success'], 'detail':validaciones_persona['detail']}, status=validaciones_persona['status'])       
        
        #CREACION DE USUARIO
        
        redirect_url=request.data.get('redirect_url','')
        redirect_url=quote_plus(redirect_url)
        
        if " " in data['nombre_de_usuario']:
            return Response({'success':False,'detail':'No puede contener espacios en el nombre de usuario'},status=status.HTTP_403_FORBIDDEN)
        
        #GUARDAR PERSONA
        serializador = serializer_persona.save()
        serializador.id_persona_crea = serializador
        serializador.save()
        
        data['creado_por_portal'] = True
        data['persona'] = serializador.id_persona
        
        serializer = self.serializer_class_usuario(data=data)
        serializer.is_valid(raise_exception=True)
        nombre_de_usuario = serializer.validated_data.get('nombre_de_usuario')
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
        descripcion = {'nombre_de_usuario': request.data["nombre_de_usuario"]}

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
        descripcion = {'nombre_de_usuario': request.data["nombre_de_usuario"], 'Rol': rol}
        auditoria_data = {
            'id_usuario': serializer_response.pk,
            'id_modulo': 5,
            'cod_permiso': 'CR',
            'subsistema': 'SEGU',
            'dirip': dirip,
            'descripcion': descripcion
        }
        Util.save_auditoria(auditoria_data)
        
        # AUDITORIA CREACION PERSONA NATURAL
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
        
        #user = User.objects.get(email=user_data['email'])

        token = RefreshToken.for_user(serializer_response)

        current_site=get_current_site(request).domain

        #persona = Personas.objects.get(id_persona = request.data['persona'])

        relativeLink= reverse('verify')
        absurl= 'http://'+ current_site + relativeLink + "?token="+ str(token) + '&redirect-url=' + redirect_url

        # short_url = Util.get_short_url(request, absurl)
        
        subject = "Verifica tu usuario"
        template = "activación-de-usuario.html"

        Util.notificacion(serializador,subject,template,absurl=absurl)
    
        return Response ({'success':True,'detail':'Se creo la persona natural y el usuario correctamente'},status=status.HTTP_200_OK)

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
                return Response({'success': True, 'detail': 'Autorización por correo electrónico y teléfono aceptada'}, status=status.HTTP_200_OK)
            elif acepta_autorizacion_email:
                return Response({'success': True, 'detail': 'Autorización por correo electrónico aceptada'}, status=status.HTTP_200_OK)
            elif acepta_autorizacion_sms:
                return Response({'success': True, 'detail': 'Autorización por teléfono aceptada'}, status=status.HTTP_200_OK)
            else:
                return Response({'success': True, 'detail': 'Autorizacion no aceptada'}, status=status.HTTP_200_OK)
        else: 
            return Response({'success': False, 'detail': 'No envió las autorizaciones'}, status=status.HTTP_400_BAD_REQUEST)