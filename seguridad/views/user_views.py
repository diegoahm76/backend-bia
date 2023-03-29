from django.core import signing
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
from seguridad.serializers.user_serializers import EmailVerificationSerializer, ResetPasswordEmailRequestSerializer, SetNewPasswordSerializer, UserPutAdminSerializer,  UserPutSerializer, UserSerializer, UserSerializerWithToken, UserRolesSerializer, RegisterSerializer  ,LoginSerializer, DesbloquearUserSerializer, SetNewPasswordUnblockUserSerializer, HistoricoActivacionSerializers, UsuarioInternoAExternoSerializers, GetBusquedaNombreUsuario,GetBuscarIdPersona
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
    http_method_names = ["patch"]
    serializer_class = UserPutAdminSerializer
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, PermisoActualizarUsuarios]

def patch(self, request, pk):
    user_loggedin = request.user.id_usuario

    if int(user_loggedin) != int(pk):
        user = User.objects.filter(id_usuario = pk).first()
        id_usuario_afectado = user.id_usuario
        id_usuario_operador = request.user.id_usuario
        fecha_operacion = datetime.now()
        justificacion = request.data.get('justificacion', '')
        cod_operacion = ''
        previous_user = copy.copy(user)

        if user:
            user_serializer = self.serializer_class(user, data=request.data)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

            # Obtenemos el tipo de usuario actual
            tipo_usuario_act = user_serializer.validated_data.get('tipo_usuario')

            # Si el tipo de usuario es externo y se actualiza a interno,
            # se activa automáticamente
            if tipo_usuario_act == 'I' and user.tipo_usuario != 'I':
                user.is_active = True

            roles = user_serializer.validated_data.get("roles")
            roles_actuales = UsuariosRol.objects.filter(id_usuario=pk).values('id_rol')
            roles_previous = copy.copy(roles_actuales)

            roles_asignados = {}

            # ASIGNAR ROLES NUEVOS A USUARIO
            for rol in roles:
                rol_existe = UsuariosRol.objects.filter(id_usuario=pk, id_rol=rol["id_rol"])
                if not rol_existe:
                    rol_instance = Roles.objects.filter(id_rol=rol["id_rol"]).first()
                    roles_asignados["nombre_rol_"+str(rol_instance.id_rol)] = rol_instance.nombre_rol
                    UsuariosRol.objects.create(
                        id_usuario = user,
                        id_rol = rol_instance
                    )

            # ELIMINAR ROLES A USUARIO

            roles_eliminados = {}
            roles_list = [rol['id_rol'] for rol in roles]
            roles_eliminar = UsuariosRol.objects.filter(id_usuario=pk).exclude(id_rol__in=roles_list)

            for rol in roles_eliminar:
                roles_eliminados["nombre_rol_"+str(rol.id_rol.id_rol)] = rol.id_rol.nombre_rol

            roles_eliminar.delete()

            # ACTUALIZAR TIPO DE USUARIO Y ESTADO DE ACTIVACIÓN
            is_active_act = None
            if 'is_active' in user_serializer.validated_data:
                is_active_act = user_serializer.validated_data.get('is_active')
            if tipo_usuario_act is not None:
                if user.tipo_usuario != tipo_usuario_act:
                    user.tipo_usuario = tipo_usuario_act
                if is_active_act is not None:
                    user.is_active = is_active_act
                    if user.is_active:
                        if is_active_act:
                            cod_operacion = 'A'
                            if user.tipo_usuario == 'E':
                                justificacion = 'Activación automática por cambio de usuario externo a usuario interno'
                        else:
                            cod_operacion = 'B'
                        if cod_operacion in ['A', 'B']:
                            justificacion = user_serializer.validated_data.get('justificacion', '')
                            if not justificacion:
                                return Response({'error': 'La justificación es obligatoria al actualizar el estado de activación o bloqueo.'}, status=status.HTTP_400_BAD_REQUEST)
                
                # ACTUALIZAR FOTO DE USUARIO
                foto_usuario = request.data.get('profile_img', None)
                if foto_usuario:
                    user.profile_img = foto_usuario
                    user.save()
                    previous_user.profile_img = foto_usuario
                    return Response({'message': 'Foto de usuario actualizada correctamente.'}, status=status.HTTP_200_OK)
                
                # ACTUALIZAR ESTADO DE ACTIVACIÓN 
                # is_active_act = user_serializer.validated_data.get('is_active')
                # if is_active_act is not None:
                #     previous_is_active = User.is_active
                #     user.is_active = is_active_act
                #     user.save()
                # if previous_is_active != is_active_act:
                #     if is_active_act:
                #         cod_operacion = 'A'
                #         if user.tipo_usuario == 'E':
                #             justificacion = 'Activación automática por cambio de usuario externo a usuario interno'
                    # else:
                    #     cod_operacion = 'I'
                    # if cod_operacion in ['A', 'I']:
                    #     justificacion = request.data.get('justificacion', '')
                    #     if not justificacion:
                    #         return Response({'error': 'La justificación es obligatoria al actualizar el estado de activación o bloqueo.'}, status=status.HTTP_400_BAD_REQUEST)


                # ACTUALIZAR ESTADO DE BLOQUEO 
                is_blocked_act = user_serializer.validated_data.get('is_blocked')
                if is_blocked_act is not None:
                    previous_is_blocked = user.is_blocked
                    user.is_blocked = is_blocked_act
                    user.save()
                    if previous_is_blocked != is_blocked_act:
                        if is_blocked_act:
                            cod_operacion = 'B'
                        else:
                            cod_operacion = 'D'
                            if cod_operacion in ['B', 'D']:
                                justificacion = request.data.get('justificacion', '') 
                                if not justificacion:
                                    return Response({'error': 'La justificación es obligatoria al actualizar el estado de activación o bloqueo.'}, status=status.HTTP_400_BAD_REQUEST)

                usuario_afectado = User.objects.get(id_usuario=id_usuario_afectado)
                usuario_operador = User.objects.get(id_usuario=id_usuario_operador)
                
                # HISTORICO 
                if cod_operacion:
                    HistoricoActivacion.objects.create(
                        id_usuario_afectado = usuario_afectado,
                        cod_operacion = cod_operacion,
                        fecha_operacion = fecha_operacion,
                        justificacion = justificacion,
                        usuario_operador = usuario_operador,
                    )
                
                user.save()

                # AUDITORIA AL ACTUALIZAR USUARIO

                dirip = Util.get_client_ip(request)
                descripcion = {'nombre_de_usuario': user.nombre_de_usuario}
                valores_actualizados = {'current': user, 'previous': previous_user}
                
                auditoria_user = {
                    'id_usuario': user_loggedin,
                    'id_modulo': 2,
                    'cod_permiso': 'AC',
                    'subsistema': 'SEGU',
                    'dirip': dirip,
                    'descripcion': descripcion,
                    'valores_actualizados': valores_actualizados
                }
                
                Util.save_auditoria(auditoria_user)
                
                # AUDITORIA AL ACTUALIZAR ROLES
                
                usuario = User.objects.get(id_usuario=user_loggedin)
                modulo = Modulos.objects.get(id_modulo = 5)
                permiso = Permisos.objects.get(cod_permiso = 'AC')
                
                descripcion_roles = 'nombre_de_usuario:' + user.nombre_de_usuario
                
                if roles_previous:
                    for rol in roles_previous:
                        rol_previous = Roles.objects.filter(id_rol=rol['id_rol']).first()
                        descripcion_roles += '|' + 'nombre_rol:' + rol_previous.nombre_rol
                    descripcion_roles += '.'
                else:
                    descripcion_roles += '.'
                
                if roles_asignados:
                    valores_actualizados = 'Se agregó en el detalle el rol '
                    for field, value in roles_asignados.items():
                        valores_actualizados += '' if not valores_actualizados else '|'
                        valores_actualizados += field + ":" + str(value)
                        
                    valores_actualizados += '.'
                    
                    auditoria_user = Auditorias.objects.create(
                        id_usuario = usuario,
                        id_modulo = modulo,
                        id_cod_permiso_accion = permiso,
                        subsistema = 'SEGU',
                        dirip = dirip,
                        descripcion = descripcion_roles,
                        valores_actualizados = valores_actualizados
                    )
                    
                    auditoria_user.save()
                
                if roles_eliminados:
                    valores_actualizados = 'Se eliminó en el detalle el rol '
                    for field, value in roles_eliminados.items():
                        valores_actualizados += '' if not valores_actualizados else '|'
                        valores_actualizados += field + ":" + str(value)
                        
                    valores_actualizados += '.'
                    
                    auditoria_user = Auditorias.objects.create(
                        id_usuario = usuario,
                        id_modulo = modulo,
                        id_cod_permiso_accion = permiso,
                        subsistema = 'SEGU',
                        dirip = dirip,
                        descripcion = descripcion_roles,
                        valores_actualizados = valores_actualizados
                    )
                    
                    auditoria_user.save()
                
                return Response({'success': True,'data': user_serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({'success': False,'detail': 'No se encontró el usuario'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'success': False,'detail': 'No puede realizar esa acción'}, status=status.HTTP_400_BAD_REQUEST)

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
        
        #EMAIL para DELEGANTE
        template = 'email-delegate-superuser.html'
        subject = 'Delegación de rol exitosa'
        
        Util.notificacion(usuario_delegante.persona,subject,template)
        
        #EMAIL para DELEGADO
        
        Util.notificacion(usuario_delegado.persona,subject,template)
        
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
            short_url = Util.get_short_url(request, absurl+'?redirect-url='+redirect_url)
            sms = 'Puedes desbloquear tu usuario en el siguiente link ' + short_url
            context = {'primer_nombre': persona_usuario_bloqueado.primer_nombre, 'primer_apellido': persona_usuario_bloqueado.primer_apellido, 'absurl': absurl+'?redirect-url='+ redirect_url}
            template = render_to_string(('email-unblock-user-naturalperson.html'), context)
            subject = 'Desbloquea tu usuario' + persona_usuario_bloqueado.primer_nombre
            data = {'template': template, 'email_subject': subject, 'to_email': persona_usuario_bloqueado.email}
            Util.send_email(data)
            try:
                Util.send_sms(persona_usuario_bloqueado.telefono_celular, sms)
            except:
                return Response({'success':True, 'detail':'No se pudo enviar sms de confirmacion'}, status=status.HTTP_200_OK)
            pass 

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
            short_url = Util.get_short_url(request, absurl+'?redirect-url='+redirect_url)
            sms = 'Puedes desbloquear tu usuario en el siguiente link ' + short_url
            context = {'razon_social': persona_usuario_bloqueado.razon_social, 'absurl': absurl+'?redirect-url='+ redirect_url}
            template = render_to_string(('email-unblock-user-naturaljuridica.html'), context)
            subject = 'Desbloquea tu usuario' + persona_usuario_bloqueado.razon_social
            data = {'template': template, 'email_subject': subject, 'to_email': persona_usuario_bloqueado.email}
            Util.send_email(data)
            try:
                Util.send_sms(persona_usuario_bloqueado.telefono_celular_empresa, sms)
            except:
                return Response({'success':True, 'detail':'No se pudo enviar sms de confirmacion'}, status=status.HTTP_200_OK)
            pass
        return Response({'success': True, 'detail': 'Email y sms enviado para desbloquear usuario'}, status=status.HTTP_200_OK)

class UnBlockUserPassword(generics.GenericAPIView):
    serializer_class = SetNewPasswordUnblockUserSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success': True, 'detail': 'Usuario Desbloqueado'}, status=status.HTTP_200_OK)

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    # renderer_classes = (UserRender,)
    permission_classes = [IsAuthenticated, PermisoCrearUsuarios]

    def post(self, request):
        user_logeado = request.user.id_usuario
        data = request.data
        redirect_url=request.data.get('redirect_url','')
        tipo_usuario = data.get('tipo_usuario')
        fecha_actual = datetime.today()
        
        if " " in data['nombre_de_usuario']:
            return Response({'success':False,'detail':'No puede contener espacios en el nombre de usuario'},status=status.HTTP_403_FORBIDDEN)

        persona = Personas.objects.filter(id_persona=data['persona']).first()
        
        if not persona:
            return Response ({'success':False,'detail':'No existe la persona'},status=status.HTTP_404_NOT_FOUND)
        
        if not persona.email:
                return Response({'success':False,'detail':'La persona no tiene un correo electrónico de notificación asociado, debe acercarse a Cormacarena y realizar una actualizacion  de datos para proceder con la creación del usuario en el sistema'},status=status.HTTP_403_FORBIDDEN)
    
        usuario = persona.user_set.exclude(id_usuario=1)

        if usuario:
            return Response ({'success':False,'detail':'la persona ya posee un usuario en el sistema, en caso de pérdida de credenciales debe usar las opciones de recuperación'},status=status.HTTP_403_FORBIDDEN)

        # VALIDACIÓN DE CARGO ACTUAL SI EL TIPO DE USUARIO ES INTERNO
        if tipo_usuario == 'I':
            cargo_actual = persona.id_cargo
            fecha_fin_cargo_actual = persona.fecha_a_finalizar_cargo_actual
            if not cargo_actual or not fecha_fin_cargo_actual or fecha_fin_cargo_actual <= fecha_actual:
                return Response({'success': False,'detail': 'La persona no tiene un cargo actual o el cargo actual está vencido, no se puede crear el usuario'}, status=status.HTTP_403_FORBIDDEN)

        #CREAR USUARIO
        serializer = self.serializer_class(data=data, many=False)
        serializer.is_valid(raise_exception=True)
        nombre_usuario_creado = serializer.validated_data.get('nombre_de_usuario')
        tipo_usuario = serializer.validated_data.get('tipo_usuario')
        if tipo_usuario != 'I':
            return Response({'success':False,'detail': 'El tipo de usuario debe ser interno'}, status=status.HTTP_403_FORBIDDEN)

        serializador = serializer.save()
        
        print('')

        #AUDITORIA CREAR USUARIO
        dirip = Util.get_client_ip(request)
        descripcion = {'nombre_de_usuario': serializador.nombre_de_usuario}
        auditoria_data = {
            'id_usuario': user_logeado,
            'id_modulo': 2,
            'cod_permiso': 'CR',
            'subsistema': 'SEGU',
            'dirip': dirip,
            'descripcion': descripcion
        }
        Util.save_auditoria(auditoria_data)

        #ASIGNACIÓN DE ROLES AL USUARIO
        roles = request.data['roles']
        for rol in roles:
            try:
                consulta_rol = Roles.objects.get(id_rol=rol['id_rol'])
                descripcion["Rol" + str(rol['id_rol'])] = str(consulta_rol.nombre_rol)
                if consulta_rol:
                    UsuariosRol.objects.create(
                        id_rol = consulta_rol,
                        id_usuario = serializador
                    )    

                    #Auditoria Asignación de Roles    
                    dirip = Util.get_client_ip(request)
                    auditoria_data = {
                        'id_usuario': user_logeado,
                        'id_modulo': 5,
                        'cod_permiso': 'CR',
                        'subsistema': 'SEGU',
                        'dirip': dirip,
                        'descripcion': descripcion,
                    }
                    Util.save_auditoria(auditoria_data)
                else:
                    return Response({'success':False,'detail':'No se puede asignar este rol por que no existe'}, status=status.HTTP_400_BAD_REQUEST)
            except:
                return Response({'success':False,'detail':'No se puede consultar por que no existe este rol'}, status=status.HTTP_400_BAD_REQUEST)
        
        token = RefreshToken.for_user(serializador)
        current_site=get_current_site(request).domain

        relativeLink= reverse('verify')
        absurl= 'http://'+ current_site + relativeLink + "?token="+ str(token) + '&redirect-url=' + redirect_url
        short_url = Util.get_short_url(request, absurl)
        
        subject = "Verifica tu usuario"
        template = "email-verification.html"

        Util.notificacion(persona,subject,template,absurl=absurl)
        
        return Response({'success':True,'detail': 'Usuario creado exitosamente, se ha enviado un correo a '+persona.email+', con la información para la activación del usuario en el sistema', 'usuario': serializer.data, 'Roles': roles, "redirect:":redirect_url}, status=status.HTTP_201_CREATED)

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
            if usuario.is_active == True or usuario.tipo_usuario == "I":
                return Response({'success':False,'detail':'La persona ya posee un usuario en el sistema, en caso de pérdida de credenciales debe usar las opciones de recuperación'},status=status.HTTP_403_FORBIDDEN)

            if usuario.is_active == False:
                return Response({'success':False,'detail':"La persona ya posee un usuario en el sistema, pero no se encuentra activado, ¿desea reenviar el correo de activación?","modal":True,"id_usuario":usuario.id_usuario},status=status.HTTP_403_FORBIDDEN)

        redirect_url=request.data.get('redirect_url','')
        
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
        template = "email-verification.html"

        Util.notificacion(persona,subject,template,absurl=absurl)
    
        return Response({'success':True, 'detail':'Usuario creado exitosamente, se ha enviado un correo a '+persona.email+', con la información para la activación del usuario en el sistema', 'data':user_data}, status=status.HTTP_201_CREATED)

class Verify(views.APIView):

    serializer_class = EmailVerificationSerializer
    token_param_config = openapi.Parameter('token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)

    @swagger_auto_schema(manual_parameters=[token_param_config])
    def get(self, request):
        token = request.GET.get('token')
        redirect_url= request.query_params.get('redirect-url')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms='HS256')
            user = User.objects.get(id_usuario=payload['user_id'])
            if not user.is_active:
                user.is_active = True
                user.save()
                if user.persona.tipo_persona == 'N':
                    context = {'primer_nombre': user.persona.primer_nombre}
                    template = render_to_string(('email-verified.html'), context)
                    subject = 'Verificación exitosa ' + user.nombre_de_usuario
                    data = {'template': template, 'email_subject': subject, 'to_email': user.persona.email}
                    Util.send_email(data)
                else:
                    context = {'razon_social': user.persona.razon_social}
                    template = render_to_string(('email-verified.html'), context)
                    subject = 'Verificación exitosa ' + user.nombre_de_usuario
                    data = {'template': template, 'email_subject': subject, 'to_email': user.persona.email}
                    Util.send_email(data)
            
            # ELIMINAR DIRECCIÓN CORTA SI EXISTE
            current_site=get_current_site(request).domain

            relativeLink= reverse('verify')
            absurl= 'http://'+ current_site + relativeLink + "?token="+ token + '&redirect-url=' + redirect_url
            print("absurl: ", absurl)
            short_url = Shortener.objects.filter(long_url=absurl).first()
            print("SHORT_URL: ", short_url)
            if short_url:
                short_url.delete()
        
            return redirect(redirect_url)
        except jwt.ExpiredSignatureError as identifier:
            # ELIMINAR DIRECCIÓN CORTA SI EXISTE
            current_site=get_current_site(request).domain

            relativeLink= reverse('verify')
            absurl= 'http://'+ current_site + relativeLink + "?token="+ token + '&redirect-url=' + redirect_url
            print("absurl: ", absurl)
            short_url = Shortener.objects.filter(long_url=absurl).first()
            print("SHORT_URL: ", short_url)
            if short_url:
                short_url.delete()
                
            return redirect(redirect_url)

        except jwt.exceptions.DecodeError as identifier:
            # ELIMINAR DIRECCIÓN CORTA SI EXISTE
            current_site=get_current_site(request).domain

            relativeLink= reverse('verify')
            absurl= 'http://'+ current_site + relativeLink + "?token="+ token + '&redirect-url=' + redirect_url
            print("absurl: ", absurl)
            short_url = Shortener.objects.filter(long_url=absurl).first()
            print("SHORT_URL: ", short_url)
            if short_url:
                short_url.delete()
                
            return redirect(redirect_url)

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
                        template = "email-login.html"
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
#                 template = render_to_string(('email-resetpassword.html'), context)
#                 subject = 'Actualiza tu contraseña ' + user.persona.primer_nombre
#                 data = {'template': template, 'email_subject': subject, 'to_email': user.persona.email}
#                 Util.send_email(data)
#             else:
#                 context = {
#                 'razon_social': user.persona.razon_social,
#                 'absurl': absurl + '?redirect-url='+ redirect_url,
#                 }
#                 template = render_to_string(('email-resetpassword.html'), context)
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
            absurl='http://'+ current_site + relativeLink 

            data_email = None
            sms = None
            nro_telefono = None
            
            if usuario.persona.tipo_persona == "N":
                context = {
                    'primer_nombre': usuario.persona.primer_nombre,
                    'primer_apellido':usuario.persona.primer_apellido,
                    'absurl': absurl + '?redirect-url='+ redirect_url,
                }
                template = render_to_string(('email-resetpassword.html'), context)
                subject = 'Actualiza tu contraseña ' + usuario.persona.primer_nombre
                data_email = {'template': template, 'email_subject': subject, 'to_email': usuario.persona.email}
                
                short_url = Util.get_short_url(request, absurl+'?redirect-url='+redirect_url)
                sms = subject + ' ' + short_url
                
                nro_telefono = usuario.persona.telefono_celular
            else:
                context = {
                    'razon_social': usuario.persona.razon_social,
                    'absurl': absurl + '?redirect-url='+ redirect_url,
                }
                template = render_to_string(('email-resetpassword.html'), context)
                subject = 'Actualiza tu contraseña ' + usuario.persona.razon_social
                data_email = {'template': template, 'email_subject': subject, 'to_email': usuario.persona.email}
            
                short_url = Util.get_short_url(request, absurl+'?redirect-url='+redirect_url)
                sms = subject + ' ' + short_url
                
                nro_telefono = usuario.persona.telefono_celular_empresa
            
            if usuario.persona.email and not nro_telefono:
                Util.send_email(data_email)
            else:
                if not data.get('tipo_envio') or data.get('tipo_envio') == '':

                    data_persona = {
                        'email': usuario.persona.email,
                        'sms': nro_telefono
                    }   
                    
                    return Response({'success':True,'detail':'Selecciona uno de los medios para la recuperación de contraseña', 'data':data_persona},status=status.HTTP_200_OK)
                else:
                    if data.get('tipo_envio') == 'email':
                        Util.send_email(data_email)
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
        try:
            id = int(signing.loads(uidb64)['user'])
            user = User.objects.get(id_usuario=id)
            if not PasswordResetTokenGenerator().check_token(user,token):
                if len(redirect_url)>3:
                    return redirect(redirect_url+'?token-valid=False')
                else:
                    return redirect(FRONTEND_URL+redirect_url+'?token-valid=False')
                
            # ELIMINAR DIRECCIÓN CORTA SI EXISTE
            current_site=get_current_site(request=request).domain
            relativeLink=reverse('password-reset-confirm',kwargs={'uidb64':uidb64,'token':token})
            
            absurl='http://'+ current_site + relativeLink + '?redirect-url=' + redirect_url
            print("absurl: ", absurl)
            short_url = Shortener.objects.filter(long_url=absurl).first()
            print("SHORT_URL: ", short_url)
            if short_url:
                short_url.delete()
                
            return redirect(redirect_url+'?token-valid=True&?message=Credentials-valid?&uidb64='+uidb64+'&?token='+token)
        except encoding.DjangoUnicodeDecodeError as identifier:
            # ELIMINAR DIRECCIÓN CORTA SI EXISTE
            current_site=get_current_site(request=request).domain
            relativeLink=reverse('password-reset-confirm',kwargs={'uidb64':uidb64,'token':token})
            
            absurl='http://'+ current_site + relativeLink + '?redirect-url=' + redirect_url
            print("absurl: ", absurl)
            short_url = Shortener.objects.filter(long_url=absurl).first()
            print("SHORT_URL: ", short_url)
            if short_url:
                short_url.delete()
                
            if not PasswordResetTokenGenerator().check_token(user):
                # ELIMINAR DIRECCIÓN CORTA SI EXISTE
                current_site=get_current_site(request=request).domain
                relativeLink=reverse('password-reset-confirm',kwargs={'uidb64':uidb64,'token':token})
                
                absurl='http://'+ current_site + relativeLink + '?redirect-url=' + redirect_url
                print("absurl: ", absurl)
                short_url = Shortener.objects.filter(long_url=absurl).first()
                print("SHORT_URL: ", short_url)
                if short_url:
                    short_url.delete()
                    
                return redirect(redirect_url+'?token-valid=False')


class SetNewPasswordApiView(generics.GenericAPIView):
    serializer_class=SetNewPasswordSerializer
    def patch(self,request):
        
        serializer=self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'success':True,'message':'Contraseña actualizada'},status=status.HTTP_200_OK)

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

            token = RefreshToken.for_user(user)

            current_site=get_current_site(request).domain

            persona = Personas.objects.filter(id_persona = user.persona.id_persona).first()

            relativeLink= reverse('verify')
            absurl= 'http://'+ current_site + relativeLink + "?token="+ str(token) + '&redirect-url=' + redirect_url

            # short_url = Util.get_short_url(request, absurl)
            subject = "Verifica tu usuario"
            template = "email-verification.html"

            Util.notificacion(persona,subject,template,absurl=absurl)
            
            return Response({"success":True,'detail':"Se ha enviado un correo a "+persona.email+" con la información para la activación del usuario en el sistema"})
            
        else: 
            return Response ({'success':False,'detail':'El usuario ya se encuentra activado'},status=status.HTTP_403_FORBIDDEN)

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
            for item in data:
                id_usuario_operador = item['usuario_operador']
                try:
                    user = User.objects.get(id_usuario=id_usuario_operador)
                    persona = user.persona
                    item['primer_nombre'] = persona.primer_nombre
                    item['primer_apellido'] = persona.primer_apellido
                except User.DoesNotExist:
                    # Si el usuario no existe, se asignan valores vacíos
                    item['primer_nombre'] = ''
                    item['primer_apellido'] = ''
            return Response({'success': True, 'detail': 'Se encontró el siguiente historico de activación para ese usuario', 'data': data}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'detail': 'No se encontro historico de activación para ese usuario'}, status=status.HTTP_404_NOT_FOUND)

class UsuarioInternoAExterno(generics.UpdateAPIView):
    serializer_class = UsuarioInternoAExternoSerializers
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

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
                justificacion='Usuario interno desactivado y convertido en externo activo',
                usuario_operador=user_loggedin,
                cod_operacion='A'
            )
            return Response({'success': True, 'detail': 'Se activo como usuario externo', 'data': serializador.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'detail': 'El usuario no existe o no cumple con los requisitos para ser convertido en usuario externo'}, status=status.HTTP_400_BAD_REQUEST)
#BUSQUEDA DE USUARIOS ENTREGA 18 UD.11

class BusquedaNombreUsuario(generics.ListAPIView):
    serializer_class = GetBusquedaNombreUsuario
    queryset = User.objects.all()
        
    def get(self,request):
        
        nombre_de_usuario = request.query_params.get('nombre_de_usuario')
        
        busqueda_usuario = User.objects.filter(nombre_de_usuario__icontains=nombre_de_usuario)
        
        if busqueda_usuario:
            serializador = self.serializer_class(busqueda_usuario,many=True)
            return Response({'succes':True,'detail':'Se encontraron los siguientes usuarios.','data':serializador.data},status=status.HTTP_200_OK)
        
        else:
            return Response({'succes':False,'detail':'No se encontro ningun resultado con los criterios de busqueda.'},status=status.HTTP_200_OK)

#BUSQUEDA ID PERSONA Y RETORNE LOS DATOS DE LA TABLA USUARIOS

class BuscarIdPersona(generics.RetrieveAPIView):
    serializer_class = GetBuscarIdPersona
    queryset = User.objects.all()
    
    def get(self,request,id_persona):
        persona = Personas.objects.filter(id_persona = id_persona).first()
        usuarios = User.objects.filter(persona=persona)
        print(usuarios)
        
        #ESTOS SON OTROS DOS METODOS DE BUSQUEDA
        
        # (metodo-1)usuarios = User.objects.filter(persona__id_persona = id_persona)
        
        # (metodo-2)personau = Personas.objects.filter(id_persona = id_persona).first()
        # usuarios = personauu.user_set.all()    

        if usuarios:
            serializador = self.serializer_class(usuarios,many=True)
            return Response({'succes':True,'detail':'Se encontraron los siguientes usuarios.','data':serializador.data},status=status.HTTP_200_OK)
        else:
            return Response({'succes':False,'detail':'No se encontro ningun resultado.'},status=status.HTTP_200_OK)
    
