from django.core import signing
from urllib.parse import quote_plus, unquote_plus
from holidays_co import get_colombia_holidays_by_year
from backend.settings.base import FRONTEND_URL
from django.urls import reverse
from django.shortcuts import redirect
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from seguridad.permissions.permissions_user import PermisoCrearUsuarios, PermisoActualizarUsuarios, PermisoActualizarInterno, PermisoActualizarExterno
from seguridad.permissions.permissions_roles import PermisoDelegarRolSuperUsuario, PermisoConsultarDelegacionSuperUsuario
from rest_framework.response import Response
from seguridad.renderers.user_renderers import UserRender
from seguridad.models import *
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics, views
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Q
from django.contrib.sites.shortcuts import get_current_site
from seguridad.serializers.personas_serializers import PersonasFilterSerializer, PersonasSerializer
from seguridad.utils import Util
from django.contrib.auth.hashers import make_password
from rest_framework import status
import jwt
from django.conf import settings
from seguridad.serializers.user_serializers import EmailVerificationSerializer, RecuperarUsuarioSerializer, ResetPasswordEmailRequestSerializer, SetNewPasswordSerializer, UserPutAdminSerializer,  UserPutSerializer, UserSerializer, UserSerializerWithToken, UserRolesSerializer, RegisterSerializer  ,LoginSerializer, DesbloquearUserSerializer, SetNewPasswordUnblockUserSerializer, HistoricoActivacionSerializers, UsuarioBasicoSerializer, UsuarioFullSerializer, UsuarioInternoAExternoSerializers
from rest_framework.generics import RetrieveUpdateAPIView
from django.contrib.auth.hashers import make_password
from rest_framework import status
from seguridad.serializers.user_serializers import EmailVerificationSerializer ,UserSerializer, UserSerializerWithToken, UserRolesSerializer, RegisterSerializer, RegisterExternoSerializer, LoginErroneoPostSerializers,LoginErroneoSerializers,LoginSerializers,LoginPostSerializers
from seguridad.serializers.roles_serializers import UsuarioRolesSerializers
from django.template.loader import render_to_string
from datetime import datetime
from django.contrib import auth
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import encoding, http
import copy, re
from django.http import HttpResponsePermanentRedirect
from django.contrib.sessions.models import Session
from rest_framework.exceptions import NotFound,ValidationError


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        serializer = UserSerializerWithToken(self.user).data
        for k, v in serializer.items():
            data[k] = v

        return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class UpdateUserProfile(generics.UpdateAPIView):
    serializer_class = UserPutSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, PermisoActualizarInterno]

    def patch(self, request):
        user_loggedin = self.request.user.id_usuario
        user = User.objects.filter(id_usuario = user_loggedin).first()
        previous_user = copy.copy(user)
        
        if user:
            user_serializer = self.serializer_class(user, data=request.data)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

            # AUDITORIA AL ACTUALIZAR USUARIO PROPIO

            dirip = Util.get_client_ip(request)
            descripcion = {'nombre_de_usuario': user.nombre_de_usuario}
            valores_actualizados = {'current': user, 'previous': previous_user}

            auditoria_data = {
                'id_usuario': user_loggedin,
                'id_modulo': 2,
                'cod_permiso': 'AC',
                'subsistema': 'SEGU',
                'dirip': dirip,
                'descripcion': descripcion,
                'valores_actualizados': valores_actualizados
            }

            Util.save_auditoria(auditoria_data)

        return Response({'success': True,'data': user_serializer.data}, status=status.HTTP_200_OK)


class UpdateUser(generics.RetrieveUpdateAPIView):
    serializer_class = UserPutAdminSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        user_loggedin = request.user.id_usuario

        if int(pk) == 1:
            return Response({'success': False,'detail': 'No se puede actualizar el super usuario'}, status=status.HTTP_400_BAD_REQUEST)

        if int(user_loggedin) != int(pk):
            user = User.objects.filter(id_usuario=pk).first()
            id_usuario_operador = request.user.id_usuario
            fecha_operacion = datetime.now()
            justificacion_activacion = request.data.get('justificacion_activacion', '')
            justificacion_bloqueo = request.data.get('justificacion_bloqueo', '')
            previous_user = copy.copy(user)

            if user:
                id_usuario_afectado = user.id_usuario
                
                user_serializer = self.serializer_class(user, data=request.data)
                user_serializer.is_valid(raise_exception=True)
                tipo_usuario_ant = user.tipo_usuario
                tipo_usuario_act = user_serializer.validated_data.get('tipo_usuario')

                # VALIDACIÓN NO SE PUEDE INTERNO A EXTERNO
                if tipo_usuario_ant == 'I' and tipo_usuario_act == 'E':
                    return Response({'success': False,'detail': 'No se puede actualizar el usuario de interno a externo'}, status=status.HTTP_400_BAD_REQUEST)

                # VALIDACIÓN EXTERNO INACTIVO PASA A INTERNO ACTIVO
                if tipo_usuario_ant == 'E' and tipo_usuario_act == 'I':
                    
                    persona = Personas.objects.get(user=user)
                    
                    if persona.id_cargo is None or persona.fecha_a_finalizar_cargo_actual <= datetime.now():
                        return Response({'success':False, 'detail':'La persona propietaria del usuario no tiene cargo actual o la fecha final del cargo ha vencido'}, status=status.HTTP_403_FORBIDDEN)
                    
                    if persona.tipo_persona == 'J':
                        return Response({'success':False, 'detail':'Una persona jurídica no puede tener un usuario de tipo interno'}, status=status.HTTP_403_FORBIDDEN)
                    
                # Validación NO desactivar externo activo
                if user.tipo_usuario == 'E' and user.is_active and 'is_active' in request.data and str(request.data['is_active']).lower() == "false":
                    return Response({'success': False,'detail': 'No se puede desactivar un usuario externo activo'}, status=status.HTTP_403_FORBIDDEN)

                # Validación SE PUEDE desactivar interno
                if user.tipo_usuario == 'I' and str(user.is_active).lower() != str(request.data['is_active']).lower():
                    # user.is_active = False
                    if not user.is_active:
                        if user.persona.id_cargo is None or user.persona.fecha_a_finalizar_cargo_actual <= datetime.now():
                            return Response({'success':False, 'detail':'La persona propietaria del usuario no tiene cargo actual o la fecha final del cargo ha vencido, por lo cual no puede activar su usuario'}, status=status.HTTP_403_FORBIDDEN)
                        
                    if 'justificacion_activacion' not in request.data or not request.data['justificacion_activacion']:
                        return Response({'success': False,'detail': 'Se requiere una justificación para cambiar el estado de activación del usuario'}, status=status.HTTP_400_BAD_REQUEST)
                    justificacion = request.data['justificacion_activacion']
                
                # Validación bloqueo/desbloqueo usuario
                if str(user.is_blocked).lower() != str(request.data['is_blocked']).lower():
                    # user.is_active = False  
                    if 'justificacion_bloqueo' not in request.data or not request.data['justificacion_bloqueo']:
                        return Response({'success': False,'detail': 'Se requiere una justificación para cambiar el estado de bloqueo del usuario'}, status=status.HTTP_400_BAD_REQUEST)
                    justificacion = request.data['justificacion_bloqueo']
                
                # ACTUALIZAR FOTO DE USUARIO
                # foto_usuario = request.data.get('profile_img', None)
                # if foto_usuario:
                #     user.profile_img = foto_usuario
                
                # ACTUALIZAR ESTADO DE BLOQUEO 
                # is_blocked_act = user_serializer.validated_data.get('is_blocked')
                # if is_blocked_act is not None:
                #     user.is_blocked = is_blocked_act
                    
                # ASIGNAR ROLES
                roles_actuales = UsuariosRol.objects.filter(id_usuario=pk)
                
                lista_roles_bd = [rol.id_rol.id_rol for rol in roles_actuales]
                lista_roles_json = request.data.getlist("roles")
                
                lista_roles_json = [int(a) for a in lista_roles_json]
                
                if 1 in lista_roles_json:
                    lista_roles_json.remove(1)
                
                if tipo_usuario_ant == 'E' and tipo_usuario_act == 'E':
                    lista_roles_json = [2]
            
                valores_creados_detalles=[]
                valores_eliminados_detalles = []

                dirip = Util.get_client_ip(request)
                descripcion = {'nombre_de_usuario': user.nombre_de_usuario}

                if set(lista_roles_bd) != set(lista_roles_json):
                    roles = Roles.objects.filter(id_rol__in=lista_roles_json)
                    if len(set(lista_roles_json)) != len(roles):
                        return Response({'success':False, 'detail':'Debe validar que todos los roles elegidos existan'},status=status.HTTP_400_BAD_REQUEST)
                    
                    for rol in roles:
                        if rol.id_rol not in lista_roles_bd:
                            UsuariosRol.objects.create(
                                id_usuario=user, 
                                id_rol=rol
                            )

                            descripcion={'nombre':rol.nombre_rol}
                            valores_creados_detalles.append(descripcion)
                
                    # ELIMINAR ROLES
                    for rol in lista_roles_bd:
                        if rol not in lista_roles_json:
                            
                            if rol == 2:
                                return Response({'success': False, 'detail': 'El rol de ciudadano no puede ser eliminado'}, status=status.HTTP_403_FORBIDDEN)
                            else:
                                roles_actuales_borrar = roles_actuales.filter(id_usuario=user.id_usuario, id_rol=rol).first()
                                diccionario = {'nombre': roles_actuales_borrar.id_rol.nombre_rol}
                                valores_eliminados_detalles.append(diccionario)
                                roles_actuales_borrar.delete()
                    
                    valores_actualizados = {'current': user, 'previous': previous_user}
                    #AUDITORIA DEL SERVICIO DE ACTUALIZADO PARA DETALLES
                    auditoria_data = {
                        "id_usuario" : user_loggedin,
                        "id_modulo" : 2,
                        "cod_permiso": "AC",
                        "subsistema": 'SEGU',
                        "dirip": dirip,
                        "descripcion": descripcion,
                        "valores_actualizados_maestro": valores_actualizados, 
                        "valores_eliminados_detalles":valores_eliminados_detalles,
                        "valores_creados_detalles":valores_creados_detalles
                    }
                    Util.save_auditoria_maestro_detalle(auditoria_data)
                
                user_actualizado = user_serializer.save()
                # user.save()

                # HISTORICO 
                usuario_afectado = User.objects.get(id_usuario=id_usuario_afectado)
                usuario_operador = User.objects.get(id_usuario=id_usuario_operador)
                cod_operacion = ""

                if previous_user.tipo_usuario == 'E' and user_actualizado.tipo_usuario == 'I' and not previous_user.is_active:
                    cod_operacion = "A"
                    justificacion = "Activación automática por cambio de usuario externo a usuario interno"
                    
                    subject = "Verificación exitosa"
                    template = "verificacion-cuenta.html"
                    absurl = FRONTEND_URL+"#/auth/login"
                    Util.notificacion(user_actualizado.persona,subject,template,absurl=absurl)
                    
                    HistoricoActivacion.objects.create(
                        id_usuario_afectado = usuario_afectado,
                        cod_operacion = cod_operacion,
                        fecha_operacion = fecha_operacion,
                        justificacion = justificacion,
                        usuario_operador = usuario_operador,
                    )
                    
                elif user_actualizado.is_active != previous_user.is_active:
                    cod_operacion = "A" if user_actualizado.is_active else "I"
                    subject = "Verificación exitosa"
                    template = "verificacion-cuenta.html"
                    absurl = FRONTEND_URL+"#/auth/login"
                    Util.notificacion(user_actualizado.persona,subject,template,absurl=absurl)
                    
                    HistoricoActivacion.objects.create(
                        id_usuario_afectado = usuario_afectado,
                        cod_operacion = cod_operacion,
                        fecha_operacion = fecha_operacion,
                        justificacion = justificacion_activacion,
                        usuario_operador = usuario_operador,
                    )
                    
                if user_actualizado.is_blocked != previous_user.is_blocked:
                    cod_operacion = "B" if user_actualizado.is_blocked else "D"
                    
                    HistoricoActivacion.objects.create(
                        id_usuario_afectado = usuario_afectado,
                        cod_operacion = cod_operacion,
                        fecha_operacion = fecha_operacion,
                        justificacion = justificacion_bloqueo,
                        usuario_operador = usuario_operador,
                    )

                return Response({'success': True, 'detail':'Actualización exitosa','data': user_serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({'success': False,'detail': 'No se encontró el usuario'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'success': False,'detail': 'No puede actualizar sus propios datos por este módulo'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def roles(request):
    roles = UsuariosRol.objects.all()
    serializers = UserRolesSerializer(roles, many=True)
    return Response(serializers.data, status=status.HTTP_200_OK)

class GetUserRoles(generics.ListAPIView):
    queryset = UsuariosRol.objects.all()
    serializer_class = UserRolesSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserProfile(request):
    user = request.user
    serializer = UserSerializer(user, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUsers(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def getUserById(request, pk):
    try:
        user = User.objects.get(id_usuario=pk)
        pass
    except:
        return Response({'success':False,'detail': 'No existe ningún usuario con este ID'}, status=status.HTTP_404_NOT_FOUND)
    serializer = UserSerializer(user, many=False)
    return Response(serializer.data, status=status.HTTP_200_OK)


class GetUserByPersonDocument(generics.ListAPIView):
    persona_serializer = PersonasSerializer
    serializer_class = UserSerializer
    def get(self, request, keyword1, keyword2):
        
        try:
            persona = Personas.objects.get(Q(tipo_documento = keyword1) & Q(numero_documento = keyword2))
            try:
                user = User.objects.get(persona=persona.id_persona)
                serializador = self.serializer_class(user)
                roles = UsuariosRol.objects.filter(id_usuario=user.id_usuario)
                serializador_roles = UserRolesSerializer(roles,many=True)
                return Response({'success':True,'Usuario' : serializador.data, 'Roles':serializador_roles.data}, status=status.HTTP_200_OK)
            except:
                serializador = PersonasSerializer(persona, many=False)
                return Response({'success':True,'Persona': serializador.data}, status=status.HTTP_200_OK)
        except:
            return Response({'success':False,'detail': 'No se encuentra persona con este numero de documento'}, status=status.HTTP_200_OK)


class GetUserByEmail(generics.ListAPIView):
    persona_serializer = PersonasSerializer
    serializer_class = UserSerializer

    def get(self, request, email):
        try:
            persona = Personas.objects.get(email=email)
            pass
        except:
            return Response({'success':False,'detail': 'No se encuentra ninguna persona con este email'}, status=status.HTTP_404_NOT_FOUND)
        try:
            user = User.objects.get(persona=persona.id_persona)
            serializer = self.serializer_class(user, many=False)
            return Response({'success':True,'Usuario': serializer.data}, status=status.HTTP_200_OK)
        except:
            return Response({'success':False,'detail': 'Este email está conectado a una persona, pero esa persona no tiene asociado un usuario'}, status=status.HTTP_403_FORBIDDEN)

"""@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateUserAdmin(request, pk):
    user = User.objects.get(id_usuario=pk)

    data = request.data

    user.nombre_de_usuario= data['email']
    user.email = data['email']
    user.is_blocked = data['is_blocked']


    user.save()

    serializer = UserSerializer(user, many=False)

    return Response(serializer.data)"""
    
class AsignarRolSuperUsuario(generics.CreateAPIView):
    serializer_class = UsuarioRolesSerializers
    queryset = UsuariosRol.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, id_persona):
        user_logeado = request.user.id_usuario

        #Validaciones
        
        persona = Personas.objects.filter(id_persona=id_persona).first()
        
        if not persona:
            return Response({'success':False,'detail': 'No existe la persona'}, status=status.HTTP_404_NOT_FOUND)

        usuario_delegado = User.objects.filter(persona=persona.id_persona).exclude(id_usuario=1).first()
        
        if not usuario_delegado or usuario_delegado.tipo_usuario != 'I': 
            return Response({'success':False,'detail': 'Esta persona no tiene un usuario interno, por lo tanto no puede asignarle este rol'}, status=status.HTTP_403_FORBIDDEN)
        
       #Delegación del super usuario       
    
        usuario_delegante = User.objects.filter(id_usuario=user_logeado).first()
        previous_usuario_delegante = copy.copy(usuario_delegante)

        #EMAIL para DELEGANTE
        template = 'delegar-superusuario-delegante.html'
        subject = 'Delegación de rol exitosa'
        absurl = FRONTEND_URL+"#/auth/login"
        
        Util.notificacion(usuario_delegante.persona,subject,template,absurl=absurl)

        usuario_delegante.persona = persona
        usuario_delegante.save()

        #Auditoria Delegación de Rol Super Usuario
        valores_actualizados = {'previous':previous_usuario_delegante,'current':usuario_delegante}
        dirip = Util.get_client_ip(request)
        descripcion = {'nombre_de_usuario': usuario_delegante.nombre_de_usuario}
        auditoria_data = {
            'id_usuario': user_logeado,
            'id_modulo': 8,
            'cod_permiso': 'EJ',
            'subsistema': 'SEGU',
            'dirip': dirip,
            'descripcion': descripcion,
            'valores_actualizados': valores_actualizados
        }
        Util.save_auditoria(auditoria_data)
        
        #EMAIL para DELEGADO
        template = 'delegar-superusuario-delegado.html'
        subject = 'Delegación de rol exitosa'
        absurl = FRONTEND_URL+"#/auth/login"
        
        Util.notificacion(usuario_delegado.persona,subject,template,absurl=absurl)
        
        return Response({'success':True,'detail': 'Delegación y notificación exitosa'}, status=status.HTTP_200_OK)

class UnblockUser(generics.CreateAPIView):
    serializer_class = DesbloquearUserSerializer

    def post(self, request):
        nombre_de_usuario = request.data['nombre_de_usuario']
        tipo_documento = request.data['tipo_documento']
        numero_documento = request.data['numero_documento']
        telefono_celular = request.data['telefono_celular']
        email = request.data['email']
        fecha_nacimiento = request.data['fecha_nacimiento']

        try:
            usuario_bloqueado = User.objects.get(nombre_de_usuario=nombre_de_usuario)
            usuario_bloqueado
            pass
        except:
            return Response({'success':False,'detail': 'Los datos ingresados de usuario son incorrectos, intenta nuevamente'}, status=status.HTTP_400_BAD_REQUEST)
        
        uidb64 = signing.dumps({'user': str(usuario_bloqueado.id_usuario)})
        token = PasswordResetTokenGenerator().make_token(usuario_bloqueado)
        current_site = get_current_site(request=request).domain

        relative_link = reverse('password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})

        redirect_url = request.data.get('redirect_url', '')
        redirect_url=quote_plus(redirect_url)
        absurl = 'http://' + current_site + relative_link

        try:
            persona_usuario_bloqueado = Personas.objects.get( Q(id_persona=usuario_bloqueado.persona.id_persona))
            pass
        except:
            return Response({'success':False,'detail': 'Los datos ingresados de usuario-persona son incorrectos, intenta nuevamente' }, status=status.HTTP_400_BAD_REQUEST)
        
        tipo_persona = persona_usuario_bloqueado.tipo_persona
        if tipo_persona == 'N':    
            try:
                persona_usuario_bloqueado = Personas.objects.get( Q(id_persona=usuario_bloqueado.persona.id_persona)
                                                                & Q(tipo_documento=tipo_documento) 
                                                                & Q(numero_documento=numero_documento) 
                                                                & Q(telefono_celular=telefono_celular) 
                                                                & Q(email=email) 
                                                                & Q(fecha_nacimiento=fecha_nacimiento)
                                                                )
                pass
            except:
                return Response({'success':False,'detail': 'Los datos ingresados de persona natural son incorrectos, intenta nuevamente'}, status=status.HTTP_400_BAD_REQUEST)
            
            subject = "Desbloquea tu usuario"
            template = "desbloqueo-de-usuario.html"

            Util.notificacion(persona_usuario_bloqueado,subject,template,absurl=absurl+'?redirect-url='+ redirect_url)

        else:
            try:
                persona_usuario_bloqueado = Personas.objects.get( Q(id_persona=usuario_bloqueado.persona.id_persona)
                                                                & Q(tipo_documento=tipo_documento) 
                                                                & Q(numero_documento=numero_documento) 
                                                                & Q(telefono_celular_empresa=telefono_celular) 
                                                                & Q(email=email) 
                                                                )
                pass
            except:
                return Response({'success':False,'detail': 'Los datos ingresados de persona juridica son incorrectos, intenta nuevamente'}, status=status.HTTP_400_BAD_REQUEST)                                 
            subject = "Desbloquea tu usuario"
            template = "desbloqueo-de-usuario.html"

            Util.notificacion(persona_usuario_bloqueado,subject,template,absurl=absurl+'?redirect-url='+ redirect_url)

        return Response({'success': True, 'detail': 'Email y sms enviado para desbloquear usuario'}, status=status.HTTP_200_OK)

class UnBlockUserPassword(generics.GenericAPIView):
    serializer_class = SetNewPasswordUnblockUserSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'detail': 'Usuario Desbloqueado'}, status=status.HTTP_200_OK)

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        data._mutable = True
        usuario_logueado = request.user.id_usuario
        persona = Personas.objects.filter(id_persona=data['persona']).first()
        
        # ASIGNAR USUARIO CREADO COMO ID_USUARIO_CREADOR
        data['id_usuario_creador'] = usuario_logueado
        
        serializer = self.serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        
        #VALIDACION DE USUARIO EXISTENTE A LA PERSONA
        usuario = persona.user_set.exclude(id_usuario=1).first()

        print("usuario",usuario)
        if usuario:
            if usuario.is_active:
                return Response({'success':False,'detail':'La persona ya posee un usuario en el sistema'},status=status.HTTP_403_FORBIDDEN)
            elif not usuario.is_active:
                return Response({'success':False,'detail':'La persona ya posee un usuario en el sistema pero está inactivo'},status=status.HTTP_403_FORBIDDEN)
        
        if data["tipo_usuario"] == "I":
            # VALIDAR QUE PERSONA NO SEA JURIDICA
            if persona.tipo_persona == 'J':
                return Response({'success':False,'detail':'No puede registrar una persona jurídica como un usuario interno'},status=status.HTTP_403_FORBIDDEN)
                
            # VALIDAR QUE TENGA CARGO
            if not persona.id_cargo:
                return Response({'success':False,'detail':'La persona no tiene un cargo asociado'},status=status.HTTP_403_FORBIDDEN)
            
            # VALIDAR QUE ESTE VIGENTE EL CARGO
            if not persona.fecha_a_finalizar_cargo_actual or persona.fecha_a_finalizar_cargo_actual <= datetime.now():
                return Response({'success':False,'detail':'La fecha de finalización del cargo actual no es vigente'},status=status.HTTP_403_FORBIDDEN)
        
        valores_creados_detalles = []
        # ASIGNACIÓN DE ROLES
        roles_por_asignar = data.getlist("roles")
        
        if not roles_por_asignar:
            return Response( {'success':False, 'detail':'Debe enviar mínimo un rol para asignar al usuario'}, status=status.HTTP_400_BAD_REQUEST)
        
        roles_por_asignar = [int(a) for a in roles_por_asignar]
        roles_por_asignar= set(roles_por_asignar)
    
        if data["tipo_usuario"] == "I":
            if 2 not in roles_por_asignar:
                roles_por_asignar.append(2)
            if 1 in roles_por_asignar:
                roles_por_asignar.remove(1)
        elif data["tipo_usuario"] == "E":
            roles_por_asignar = [2]
        
        roles = Roles.objects.filter(id_rol__in=roles_por_asignar)
        
        if len(roles) != len(set(roles_por_asignar)):
            return Response( {'success':False, 'detail':'Deben existir todos los roles asignados'}, status=status.HTTP_400_BAD_REQUEST)

        user_serializer=serializer.save()

        for rol in roles:
            UsuariosRol.objects.create(
                id_usuario=user_serializer,
                id_rol=rol
            )
            descripcion={'nombre':rol.nombre_rol}
            valores_creados_detalles.append(descripcion)

        # # Crear registro de auditoría para el maestro detalle de Roles
        # descripcion = {'nombre_de_usuario': request.data["nombre_de_usuario"]}
        # dirip = Util.get_client_ip(request)
        # auditoria_data = {
        #     "id_usuario": user_serializer.pk,
        #     "id_modulo": 5,  
        #     "cod_permiso": "CR",
        #     "subsistema": "SEGU",
        #     "dirip": dirip,
        #     "descripcion": descripcion,
        #     "valores_creados_detalles": valores_creados_detalles,
        # }
        # Util.save_auditoria_maestro_detalle(auditoria_data)

        # redirect_url=request.data.get('redirect_url','')
        # token = RefreshToken.for_user(user_serializer)
        # current_site=get_current_site(request).domain

        # relativeLink= reverse('verify')
        # absurl= 'http://'+ current_site + relativeLink + "?token="+ str(token) + '&redirect-url=' + redirect_url
        # short_url = Util.get_short_url(request, absurl)
        
        uidb64 =signing.dumps({'user':str(user_serializer.id_usuario)})
        token = PasswordResetTokenGenerator().make_token(user_serializer)
        current_site=get_current_site(request=request).domain
        relativeLink=reverse('password-reset-confirm',kwargs={'uidb64':uidb64,'token':token})
        redirect_url= request.data.get('redirect_url','')
        redirect_url=quote_plus(redirect_url)
        absurl='http://'+ current_site + relativeLink + '?redirect-url='+ redirect_url
        
        subject = "Verifica tu usuario"
        template = "activación-de-usuario.html"

        Util.notificacion(persona,subject,template,absurl=absurl,email=persona.email)
        
        return Response({'success':True,'detail': 'Usuario creado exitosamente, se ha enviado un correo a ' + persona.email + ', con la información para la activación del usuario en el sistema', 'data': serializer.data}, status=status.HTTP_201_CREATED)

class RegisterExternoView(generics.CreateAPIView):
    serializer_class = RegisterExternoSerializer
    # renderer_classes = (UserRender,)

    def post(self, request):
        user = request.data
        
        persona = Personas.objects.filter(id_persona=user['persona']).first()
        
        if not persona:
            return Response({'success':False,'detail':'No existe la persona'},status=status.HTTP_404_NOT_FOUND)
        
        if not persona.email:
            return Response({'success':False,'detail':'La persona no tiene un correo electrónico de notificación asociado, debe acercarse a Cormacarena y realizar una actualizacion  de datos para proceder con la creación del usuario en el sistema'},status=status.HTTP_403_FORBIDDEN)
    
        usuario = persona.user_set.exclude(id_usuario=1).first()

        if usuario:
            if usuario.is_active or usuario.tipo_usuario == "I":
                return Response({'success':False,'detail':'La persona ya posee un usuario en el sistema, en caso de pérdida de credenciales debe usar las opciones de recuperación'},status=status.HTTP_403_FORBIDDEN)
            elif not usuario.is_active and usuario.tipo_usuario == "E" :
                return Response({'success':False,'detail':"La persona ya posee un usuario en el sistema, pero no se encuentra activado, ¿desea reenviar el correo de activación?","modal":True,"id_usuario":usuario.id_usuario},status=status.HTTP_403_FORBIDDEN)

        redirect_url=request.data.get('redirect_url','')
        redirect_url=quote_plus(redirect_url)
        
        if " " in user['nombre_de_usuario']:
            return Response({'success':False,'detail':'No puede contener espacios en el nombre de usuario'},status=status.HTTP_403_FORBIDDEN)
        
        user['creado_por_portal'] = True
        
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        nombre_de_usuario = serializer.validated_data.get('nombre_de_usuario')
        serializer_response = serializer.save()
        user_data = serializer.data
        
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

        #user = User.objects.get(email=user_data['email'])

        token = RefreshToken.for_user(serializer_response)

        current_site=get_current_site(request).domain

        #persona = Personas.objects.get(id_persona = request.data['persona'])

        relativeLink= reverse('verify')
        absurl= 'http://'+ current_site + relativeLink + "?token="+ str(token) + '&redirect-url=' + redirect_url

        # short_url = Util.get_short_url(request, absurl)
        
        subject = "Verifica tu usuario"
        template = "activación-de-usuario.html"

        Util.notificacion(persona,subject,template,absurl=absurl,email=persona.email)
    
        return Response({'success':True, 'detail':'Usuario creado exitosamente, se ha enviado un correo a '+persona.email+', con la información para la activación del usuario en el sistema', 'data':user_data}, status=status.HTTP_201_CREATED)

class Verify(views.APIView):

    serializer_class = EmailVerificationSerializer
    token_param_config = openapi.Parameter('token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get('token')
        redirect_url= request.query_params.get('redirect-url')
        redirect_url=unquote_plus(redirect_url)
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
            user = User.objects.get(id_usuario=payload['user_id'])
            if not user.is_active:
                user.is_active = True
                user.activated_at = datetime.now()
                user.save()
                
                HistoricoActivacion.objects.create(
                    id_usuario_afectado=user,
                    justificacion='Activación Inicial del Usuario',
                    usuario_operador=user,
                    cod_operacion='A'
                )
                
                subject = "Verificación exitosa"
                template = "verificacion-cuenta.html"
                absurl = FRONTEND_URL+"#/auth/login"
                Util.notificacion(user.persona,subject,template,absurl=absurl)
            
            # ELIMINAR DIRECCIÓN CORTA SI EXISTE
            current_site=get_current_site(request).domain

            relativeLink= reverse('verify')
            absurl= 'http://'+ current_site + relativeLink + "?token="+ token + '&redirect-url=' + redirect_url
            short_url = Shortener.objects.filter(long_url=absurl).first()
            if short_url:
                short_url.delete()
            redirect_url = redirect_url + '&' if '?' in redirect_url else redirect_url + '?'
            return redirect(redirect_url + "success=True")
        except jwt.ExpiredSignatureError as identifier:
            # ELIMINAR DIRECCIÓN CORTA SI EXISTE
            current_site=get_current_site(request).domain

            relativeLink= reverse('verify')
            absurl= 'http://'+ current_site + relativeLink + "?token="+ token + '&redirect-url=' + redirect_url
            short_url = Shortener.objects.filter(long_url=absurl).first()
            if short_url:
                short_url.delete()
            redirect_url = redirect_url + '&' if '?' in redirect_url else redirect_url + '?'
            return redirect(redirect_url + "success=False")

        except jwt.exceptions.DecodeError as identifier:
            # ELIMINAR DIRECCIÓN CORTA SI EXISTE
            current_site=get_current_site(request).domain

            relativeLink= reverse('verify')
            absurl= 'http://'+ current_site + relativeLink + "?token="+ token + '&redirect-url=' + redirect_url
            short_url = Shortener.objects.filter(long_url=absurl).first()
            if short_url:
                short_url.delete()
            redirect_url = redirect_url + '&' if '?' in redirect_url else redirect_url + '?'
            return redirect(redirect_url + "success=False")

class LoginConsultarApiViews(generics.RetrieveAPIView):
    serializer_class=LoginSerializers
    queryset = Login.objects.all()

class LoginListApiViews(generics.ListAPIView):
    serializer_class=LoginSerializers
    queryset = Login.objects.all()

class DeactivateUsers(generics.ListAPIView):
    serializer_class=LoginSerializers
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def post(self, request, id_persona):
        usuario = self.queryset.all().filter(persona__id_persona = id_persona).first()
        sesiones = Session.objects.all()
        
        if usuario:
            for sesion in sesiones:
                if sesion.get_decoded().get('_auth_user_id') == usuario.id_usuario:
                    sesion.delete()
            usuario.is_active = False
            usuario.save()
            
            return Response({'success':True, 'detail':'Se eliminó la sesión del usuario elegido'}, status=status.HTTP_200_OK)
        else:
            return Response({'success':False, 'detail':'No se encontró el usuario para la persona ingresada'}, status=status.HTTP_400_BAD_REQUEST)

#__________________LoginErroneo

class LoginErroneoConsultarApiViews(generics.RetrieveAPIView):
    serializer_class=LoginErroneoSerializers
    queryset = LoginErroneo.objects.all()

class LoginErroneoListApiViews(generics.ListAPIView):
    serializer_class=LoginErroneoSerializers
    queryset = LoginErroneo.objects.all()

class LoginApiView(generics.CreateAPIView):
    serializer_class=LoginSerializer

    def post(self, request):
        data = request.data
        user = User.objects.filter(nombre_de_usuario=data['nombre_de_usuario']).first()
        
        ip = Util.get_client_ip(request)
        device = Util.get_client_device(request)
        if user:
            if user.is_active:
                roles = UsuariosRol.objects.filter(id_usuario=user.id_usuario).values()
                rol_id_list = [rol['id_rol_id'] for rol in roles]
                permisos_list = []
                for rol in rol_id_list:
                    permisos = PermisosModuloRol.objects.filter(id_rol=rol).values()
                    permisos_list.append(permisos)
               
                try:
                    login_error = LoginErroneo.objects.filter(id_usuario=user.id_usuario).last()
                    
                    serializer = self.serializer_class(data=data)
                    serializer.is_valid(raise_exception=True)

                    login = Login.objects.create(
                        id_usuario = user,
                        dirip = str(ip),
                        dispositivo_conexion = device
                    )

                    LoginPostSerializers(login, many=False)

                    if login_error:
                        login_error.contador = 0
                        login_error.save()
                        
                    representante_legal=Personas.objects.filter(representante_legal=user.persona.id_persona).values()
                    representante_legal_list=[{'id_persona':representante['id_persona'],'razon_social':representante['razon_social'],'NUIP':representante['numero_documento']}for representante in representante_legal]
                    
                    # DEFINIR SI UN USUARIO SI O SI DEBE TENER UN PERMISO O NO
                    permisos_list = permisos_list[0] if permisos_list else []
                    
                    serializer_data = serializer.data
                    
                    user_info={'userinfo':serializer_data,'permisos':permisos_list,'representante_legal':representante_legal_list}
                    sms = "Bia Cormacarena te informa que se ha registrado una conexion con el usuario " + user.nombre_de_usuario + " en la fecha " + str(datetime.now())
                    
                    if user.persona.telefono_celular:
                        Util.send_sms(user.persona.telefono_celular, sms)
                    else:
                        subject = "Login exitoso"
                        template = "notificacion-login.html"
                        Util.notificacion(user.persona,subject,template,nombre_de_usuario=user.nombre_de_usuario)
                    
                    return Response({'userinfo':user_info}, status=status.HTTP_200_OK)
                except:
                    login_error = LoginErroneo.objects.filter(id_usuario=user.id_usuario).first()
                    if login_error:
                        if login_error.contador < 3:
                            hour_difference = datetime.utcnow().replace(tzinfo=None) - login_error.fecha_login_error.replace(tzinfo=None)
                            hour_difference = (hour_difference.days * 24) + (hour_difference.seconds//3600)
                            if hour_difference < 24:
                                login_error.contador += 1
                                login_error.restantes = 3 - login_error.contador
                                login_error.save()
                            else :
                                login_error.contador = 1
                                login_error.save()
                            if login_error.contador == 3:
                                user.is_blocked = True
                                user.save()
                        
                                HistoricoActivacion.objects.create(
                                    id_usuario_afectado = user,
                                    cod_operacion = 'B',
                                    fecha_operacion = datetime.now(),
                                    justificacion = 'Usuario bloqueado por exceder los intentos incorrectos en el login',
                                    usuario_operador = user,
                                )
                                

                                return Response({'success':False,'detail':'Su usuario ha sido bloqueado'}, status=status.HTTP_403_FORBIDDEN)
                            serializer = LoginErroneoPostSerializers(login_error, many=False)
                            return Response({'success':False, 'detail':'La contraseña es invalida', 'login_erroneo': serializer.data}, status=status.HTTP_400_BAD_REQUEST)
                        else:
                            if user.is_blocked:
                                return Response({'success':False, 'detail':'Su usuario está bloqueado, debe comunicarse con el administrador'}, status=status.HTTP_403_FORBIDDEN)
                            else:
                                login_error.contador = 1
                                login_error.save()
                                serializer = LoginErroneoPostSerializers(login_error, many=False)
                                return Response({'success':False, 'detail':'La contraseña es invalida', 'login_erroneo': serializer.data}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        if user.is_blocked:
                            return Response({'success':False, 'detail':'Su usuario está bloqueado, debe comunicarse con el administrador'}, status=status.HTTP_403_FORBIDDEN)
                        else:
                            login_error = LoginErroneo.objects.create(
                                id_usuario = user,
                                dirip = str(ip),
                                dispositivo_conexion = device,
                                contador = 1
                            )
                        login_error.restantes = 3 - login_error.contador
                        serializer = LoginErroneoPostSerializers(login_error, many=False)
                        return Response({'success':False,'detail':'La contraseña es invalida', 'login_erroneo': serializer.data}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'success':False, 'detail':'Usuario no activado', 'data':{'modal':True, 'id_usuario':user.id_usuario, 'tipo_usuario':user.tipo_usuario}}, status=status.HTTP_403_FORBIDDEN)
        else:
            UsuarioErroneo.objects.create(
                campo_usuario = data['nombre_de_usuario'],
                dirip = str(ip),
                dispositivo_conexion = device
            )
            return Response({'success':False,'detail':'No existe el nombre de usuario ingresado'}, status=status.HTTP_400_BAD_REQUEST)

# class RequestPasswordResetEmail(generics.GenericAPIView):
#     serializer_class = ResetPasswordEmailRequestSerializer

#     def post(self,request):
#         serializer=self.serializer_class(data=request.data)
#         email = request.data['email']
        
#         if User.objects.filter(persona__email=email).exists():
#             user = User.objects.get(persona__email=email)
#             uidb64 =signing.dumps({'user':str(user.id_usuario)})
#             print(uidb64)
#             token = PasswordResetTokenGenerator().make_token(user)
#             current_site=get_current_site(request=request).domain
#             relativeLink=reverse('password-reset-confirm',kwargs={'uidb64':uidb64,'token':token})
#             redirect_url= request.data.get('redirect_url','')
#             absurl='http://'+ current_site + relativeLink 
#             if user.persona.tipo_persona == 'N':
#                 context = {
#                 'primer_nombre': user.persona.primer_nombre,
#                 'primer_apellido':user.persona.primer_apellido,
#                 'absurl': absurl + '?redirect-url='+ redirect_url,
#                 }
#                 template = render_to_string(('recuperar-contraseña.html'), context)
#                 subject = 'Actualiza tu contraseña ' + user.persona.primer_nombre
#                 data = {'template': template, 'email_subject': subject, 'to_email': user.persona.email}
#                 Util.send_email(data)
#             else:
#                 context = {
#                 'razon_social': user.persona.razon_social,
#                 'absurl': absurl + '?redirect-url='+ redirect_url,
#                 }
#                 template = render_to_string(('recuperar-contraseña.html'), context)
#                 subject = 'Actualiza tu contraseña ' + user.persona.razon_social
#                 data = {'template': template, 'email_subject': subject, 'to_email': user.persona.email}
#                 Util.send_email(data)
#         return Response( {'success':True,'detail':'Te enviamos el link para poder actualizar tu contraseña'},status=status.HTTP_200_OK)

class RequestPasswordResetEmail(generics.CreateAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer
    queryset = User.objects.all()
    
    def post(self,request):
        
        data = request.data
        
        usuario = self.queryset.all().filter(nombre_de_usuario=data['nombre_de_usuario']).first()
        
        if usuario:
            
            uidb64 =signing.dumps({'user':str(usuario.id_usuario)})
            print(uidb64)
            token = PasswordResetTokenGenerator().make_token(usuario)
            current_site=get_current_site(request=request).domain
            relativeLink=reverse('password-reset-confirm',kwargs={'uidb64':uidb64,'token':token})
            redirect_url= request.data.get('redirect_url','')
            redirect_url=quote_plus(redirect_url)
            absurl='http://'+ current_site + relativeLink 

            data_email = None
            sms = None
            nro_telefono = None
            
            if usuario.persona.tipo_persona == "N":
                template = 'recuperar-contraseña.html'
                subject = 'Actualiza tu contraseña'

                short_url = Util.get_short_url(request, absurl+'?redirect-url='+redirect_url)
                sms = subject + ' ' + short_url
                
                nro_telefono = usuario.persona.telefono_celular
            else:
                template = 'recuperar-contraseña.html'
                subject = 'Actualiza tu contraseña'
            
                short_url = Util.get_short_url(request, absurl+'?redirect-url='+redirect_url)
                sms = subject + ' ' + short_url
                
                nro_telefono = usuario.persona.telefono_celular_empresa
            
            if usuario.persona.email and not nro_telefono:
                Util.notificacion(usuario.persona,subject,template,absurl=absurl + '?redirect-url='+ redirect_url)
            else:
                if not data.get('tipo_envio') or data.get('tipo_envio') == '':

                    data_persona = {
                        'email': usuario.persona.email,
                        'sms': nro_telefono
                    }   
                    
                    return Response({'success':True,'detail':'Selecciona uno de los medios para la recuperación de contraseña', 'data':data_persona},status=status.HTTP_200_OK)
                else:
                    if data.get('tipo_envio') == 'email':
                        Util.notificacion(usuario.persona,subject,template,absurl=absurl + '?redirect-url='+ redirect_url)
                    elif data.get('tipo_envio') == 'sms':
                        Util.send_sms(nro_telefono, sms)
                    else:
                        return Response({'success':False,'detail':'Debe elegir un tipo de envío valido'},status=status.HTTP_400_BAD_REQUEST)
                    
            return Response({'success':True,'detail':'Se ha enviado correctamente la notificación de la recuperación de contraseña'},status=status.HTTP_200_OK)
        else:
            return Response({'success':False,'detail':'No se encontró ningún usuario por el nombre de usuario ingresado'},status=status.HTTP_404_NOT_FOUND)

class PasswordTokenCheckApi(generics.GenericAPIView):
    serializer_class=UserSerializer
    def get(self,request,uidb64,token):
        redirect_url= request.query_params.get('redirect-url')
        redirect_url=unquote_plus(redirect_url)
        try:
            id = int(signing.loads(uidb64)['user'])
            user = User.objects.get(id_usuario=id)
            redirect_url = redirect_url + '&' if '?' in redirect_url else redirect_url + '?'
            if not PasswordResetTokenGenerator().check_token(user,token):
                if len(redirect_url)>3:
                    return redirect(redirect_url+'token-valid=False')
                else:
                    return redirect(FRONTEND_URL+redirect_url+'token-valid=False')
            
            # ELIMINAR DIRECCIÓN CORTA SI EXISTE
            current_site=get_current_site(request=request).domain
            relativeLink=reverse('password-reset-confirm',kwargs={'uidb64':uidb64,'token':token})
            
            absurl='http://'+ current_site + relativeLink + '?redirect-url=' + redirect_url
            short_url = Shortener.objects.filter(long_url=absurl).first()
            if short_url:
                short_url.delete()
            redirect_url = redirect_url + '&' if '?' in redirect_url else redirect_url + '?'
            return redirect(redirect_url+'token-valid=True&message=Credentials-valid&uidb64='+uidb64+'&token='+token)
        except encoding.DjangoUnicodeDecodeError as identifier:
            # ELIMINAR DIRECCIÓN CORTA SI EXISTE
            current_site=get_current_site(request=request).domain
            relativeLink=reverse('password-reset-confirm',kwargs={'uidb64':uidb64,'token':token})
            
            absurl='http://'+ current_site + relativeLink + '?redirect-url=' + redirect_url
            short_url = Shortener.objects.filter(long_url=absurl).first()
            if short_url:
                short_url.delete()
                
            if not PasswordResetTokenGenerator().check_token(user):
                # ELIMINAR DIRECCIÓN CORTA SI EXISTE
                current_site=get_current_site(request=request).domain
                relativeLink=reverse('password-reset-confirm',kwargs={'uidb64':uidb64,'token':token})
                
                absurl='http://'+ current_site + relativeLink + '?redirect-url=' + redirect_url
                short_url = Shortener.objects.filter(long_url=absurl).first()
                if short_url:
                    short_url.delete()
                redirect_url = redirect_url + '&' if '?' in redirect_url else redirect_url + '?'
                return redirect(redirect_url+'token-valid=False')


class SetNewPasswordApiView(generics.GenericAPIView):
    serializer_class=SetNewPasswordSerializer
    
    def patch(self,request):
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        password = request.data.get('password')
        uidb64 = request.data.get('uidb64')
        id = int(signing.loads(uidb64)['user'])
        user = User.objects.filter(id_usuario=id).first()
        
        if user.password and user.password != "":
            message = 'Contraseña actualizada'
        else:
            user.is_active = True
            user.activated_at = datetime.now()
            
            HistoricoActivacion.objects.create(
                id_usuario_afectado=user,
                justificacion='Activación Inicial del Usuario',
                usuario_operador=user,
                cod_operacion='A'
            )
            
            subject = "Verificación exitosa"
            template = "verificacion-cuenta.html"
            absurl = FRONTEND_URL+"#/auth/login"
            Util.notificacion(user.persona,subject,template,absurl=absurl)
            
            message = 'Usuario activado correctamente'
        
        user.set_password(password)
        user.save()
        
        return Response({'success':True,'detail':message},status=status.HTTP_200_OK)

@api_view(['POST'])
def uploadImage(request):
    data = request.data
    print(data)
    user_id = data['id_usuario']
    user = User.objects.get(id_usuario=user_id)

    user.profile_img = request.FILES.get('image')
    user.save()

    return Response('Image was uploaded')

class GetNuevoSuperUsuario(generics.RetrieveAPIView):
    serializer_class = PersonasFilterSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get (self,request,tipo_documento,numero_documento):
        fecha_sistema = datetime.now()
                
        nuevo_super_usuario = Personas.objects.filter(tipo_documento=tipo_documento,numero_documento=numero_documento,fecha_a_finalizar_cargo_actual__gt=fecha_sistema).filter(~Q(id_cargo = None)).first()
        
        if nuevo_super_usuario:
            serializador = self.serializer_class(nuevo_super_usuario)
            return Response({'succes':True, 'detail':'Los datos coincidieron con la búsqueda realizada','data':serializador.data},status=status.HTTP_200_OK)
        else: 
            return Response({'succes':False, 'detail':'La persona no existe o no tiene cargo actual'},status=status.HTTP_404_NOT_FOUND)

class GetNuevoSuperUsuarioFilters(generics.ListAPIView):
    serializer_class = PersonasFilterSerializer
    queryset = Personas.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self,request):
    
        filter={}
        for key, value in request.query_params.items():
            if key in ['primer_nombre','primer_apellido','tipo_documento','numero_documento']:
                if key == 'primer_nombre' or key== 'primer_apellido':
                    if value != '':
                        filter[key+'__icontains'] = value
                elif key == 'numero_documento':
                    if value != '':
                        filter[key+'__startswith'] = value
                else:
                    if value != '':
                        filter[key] = value
                    
        fecha_sistema =  datetime.now()           
        filter['fecha_a_finalizar_cargo_actual__gt'] = fecha_sistema

        persona = self.queryset.all().filter(**filter).filter(~Q(id_cargo = None))
        
        serializador = self.serializer_class(persona,many=True)
        return Response({'succes':True, 'detail':'Se encontraron las siguientes personas','data':serializador.data},status=status.HTTP_200_OK)
        
class ReenviarCorreoVerificacionDeUsuario(generics.UpdateAPIView):
    serializer_class = RegisterExternoSerializer
    
    def put(self,request,id_usuario):
        
        user = User.objects.filter(id_usuario=id_usuario).first()
        
        if user.is_active == False and user.tipo_usuario == "E":
            
            redirect_url=request.data.get('redirect_url','')
            redirect_url=quote_plus(redirect_url)

            token = RefreshToken.for_user(user)

            current_site=get_current_site(request).domain

            persona = Personas.objects.filter(id_persona = user.persona.id_persona).first()

            relativeLink= reverse('verify')
            absurl= 'http://'+ current_site + relativeLink + "?token="+ str(token) + '&redirect-url=' + redirect_url

            # short_url = Util.get_short_url(request, absurl)
            subject = "Verifica tu usuario"
            template = "activación-de-usuario.html"

            Util.notificacion(persona,subject,template,absurl=absurl,email=persona.email)
            
            return Response({"success":True,'detail':"Se ha enviado un correo a "+persona.email+" con la información para la activación del usuario en el sistema"})
            
        else: 
            return Response ({'success':False,'detail':'El usuario ya se encuentra activado o es un usuario interno'},status=status.HTTP_403_FORBIDDEN)

class BusquedaHistoricoActivacion(generics.ListAPIView):
    serializer_class = HistoricoActivacionSerializers
    queryset = HistoricoActivacion.objects.all()

    def get_queryset(self):
        id_usuario = self.kwargs['id_usuario_afectado']
        queryset = HistoricoActivacion.objects.filter(id_usuario_afectado=id_usuario)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset.exists():
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
            return Response({'success': True, 'detail': 'Se encontró el siguiente historico de activación para ese usuario', 'data': data}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'detail': 'No se encontro historico de activación para ese usuario'}, status=status.HTTP_404_NOT_FOUND)

class UsuarioInternoAExterno(generics.UpdateAPIView):
    serializer_class = UsuarioInternoAExternoSerializers
    queryset = User.objects.all()
    # permission_classes = [IsAuthenticated]

    def put(self, request, id_usuario):
        user_loggedin = request.user
        serializador = self.serializer_class(user_loggedin)
        usuario = User.objects.filter(id_usuario=id_usuario, tipo_usuario='I', is_active=False).first()
        if usuario:
            usuario.tipo_usuario = 'E'
            usuario.is_active = True
            usuario.save()
            HistoricoActivacion.objects.create(
                id_usuario_afectado=usuario,
                justificacion='Usuario activado desde el portal, con cambio de INTERNO a EXTERNO',
                usuario_operador=user_loggedin,
                cod_operacion='A'
            )

            subject = "Cambio a usuario externo"
            template = "cambio-tipo-de-usuario.html"
            Util.notificacion(usuario.persona,subject,template,nombre_de_ususario=usuario.nombre_de_usuario)

            return Response({'success': True, 'detail': 'Se activo como usuario externo', 'data': serializador.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'detail': 'El usuario no existe o no cumple con los requisitos para ser convertido en usuario externo'}, status=status.HTTP_400_BAD_REQUEST)
        
#BUSQUEDA DE USUARIOS ENTREGA 18 UD.11

class BusquedaByNombreUsuario(generics.ListAPIView):
    serializer_class = UsuarioBasicoSerializer
    queryset = User.objects.all()
        
    def get(self,request):
        
        nombre_de_usuario = request.query_params.get('nombre_de_usuario')
        
        busqueda_usuario = self.queryset.all().filter(nombre_de_usuario__icontains=nombre_de_usuario)
        
        serializador = self.serializer_class(busqueda_usuario,many=True, context = {'request':request})
        
        return Response({'succes':True,'detail':'Se encontraron los siguientes usuarios.','data':serializador.data},status=status.HTTP_200_OK)

#BUSQUEDA ID PERSONA Y RETORNE LOS DATOS DE LA TABLA USUARIOS

class BuscarByIdPersona(generics.RetrieveAPIView):
    serializer_class = UsuarioBasicoSerializer
    queryset = User.objects.all()
    
    def get(self,request,id_persona):
        usuarios = self.queryset.all().filter(persona=id_persona)
            
        serializador = self.serializer_class(usuarios,many=True, context = {'request':request})
        return Response({'succes':True,'detail':'Se encontraron los siguientes usuarios.','data':serializador.data},status=status.HTTP_200_OK)
    
class GetByIdUsuario(generics.RetrieveAPIView):
    serializer_class = UsuarioFullSerializer
    queryset = User.objects.all()
    
    def get(self,request,id_usuario):
        usuario = self.queryset.all().filter(id_usuario=id_usuario).first()
        
        if not usuario:
            return Response({'succes':False, 'detail':'No se encontró el usuario ingresado'},status=status.HTTP_404_NOT_FOUND)
        
        serializador = self.serializer_class(usuario, context = {'request':request})
        return Response({'succes':True, 'detail':'Se encontró la información del usuario', 'data':serializador.data},status=status.HTTP_200_OK)
    

class RecuperarNombreDeUsuario(generics.UpdateAPIView):
    serializer_class = RecuperarUsuarioSerializer
    queryset = User.objects.all()
    
    def put(self,request):
        data = request.data
        
        if not data.get('tipo_documento') or not data.get('numero_documento') or not data.get('email'):
            raise ValidationError('Debe ingresar los parámetros respectivos: tipo de documento, número de documento, email')
        
        persona = Personas.objects.filter(tipo_documento=data['tipo_documento'], numero_documento=data['numero_documento'], email=data['email']).first()
        
        if persona:
            usuario = self.queryset.all().filter(persona = persona.id_persona).exclude(id_usuario=1).first()
            
            if usuario:
                
                subject = "Verifica tu usuario"
                template = "email-recupe-nombre-usuario.html"

                Util.notificacion(persona,subject,template,nombre_de_ususario=usuario.nombre_de_usuario)

                return Response({'success':True,'detail':'Se ha enviado el correo'},status=status.HTTP_200_OK)
            
            else:
                raise NotFound('No existe usuario') 
        raise NotFound('No existe usuario')