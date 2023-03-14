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
from seguridad.serializers.personas_serializers import PersonasSerializer
from seguridad.utils import Util
from django.contrib.auth.hashers import make_password
from rest_framework import status
import jwt
from django.conf import settings
from seguridad.serializers.user_serializers import EmailVerificationSerializer, GetNuevoSuperUsuarioSerializer, GetSuperUsuarioSerializer, ResetPasswordEmailRequestSerializer, SetNewPasswordSerializer, UserPutAdminSerializer,  UserPutSerializer, UserSerializer, UserSerializerWithToken, UserRolesSerializer, RegisterSerializer  ,LoginSerializer, DesbloquearUserSerializer, SetNewPasswordUnblockUserSerializer, HistoricoActivacionSerializers
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
            previous_user = copy.copy(user)
            if user:
                user_serializer = self.serializer_class(user, data=request.data)
                user_serializer.is_valid(raise_exception=True)
                user_serializer.save()
                
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
        #validar si es necesario esta linea con el "id_rol=3"
        # rol_interno = Roles.objects.get(id_rol=3)

        #Validaciones
        
        persona = Personas.objects.filter(id_persona=id_persona).first()
        
        if not persona:
            return Response({'success':False,'detail': 'No existe la persona'}, status=status.HTTP_404_NOT_FOUND)

        usuario_delegado = User.objects.filter(persona=persona.id_persona).first()
        
        if not usuario_delegado or usuario_delegado.tipo_usuario != 'I': 
            return Response({'success':False,'detail': 'Esta persona no tiene un usuario interno, por lo tanto no puede asignarle este rol'}, status=status.HTTP_403_FORBIDDEN)
        
       #Delegación del super usuario       
    
        usuario_delegante = User.objects.filter(id_usuario=user_logeado).first()
        previous_usuario_delegante = copy.copy(usuario_delegante)
        usuario_delegante.persona = persona
        usuario_delegante.save()
        print(usuario_delegante)

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
        
        #SMS y EMAIL para DELEGANTE
        persona_delegante = Personas.objects.get(id_persona = usuario_delegante.persona.id_persona)
        #sms = 'Te informamos que has delegado tu rol super usuario exitosamente'
        context = {'primer_nombre': persona_delegante.primer_nombre, 'primer_apellido': persona_delegante.primer_apellido}
        template = render_to_string(('email-delegate-superuser.html'), context)
        subject = 'Delegación de rol exitosa ' + str(persona_delegante.primer_nombre)
        data = {'template': template, 'email_subject': subject, 'to_email': persona_delegante.email}
        Util.send_email(data)
        #try:
         #   Util.send_sms(persona_delegante.telefono_celular, sms)
          #  pass
        #except:
         #   return Response({'success':True,'detail':'Se realizó la asignación sin problema pero no se pudo enviar sms de confirmación'}, status=status.HTTP_200_OK)
        
        #SMS y EMAIL para DELEGADO
        persona_delegado = Personas.objects.get(id_persona = usuario_delegado.persona.id_persona)
        #sms = 'Te informamos que has sido delegado para tener el rol super usuario '
        context = {'primer_nombre': persona_delegado.primer_nombre, 'primer_apellido': persona_delegado.primer_apellido}
        template = render_to_string(('email-delegate-superuser.html'), context)
        subject = 'Delegación de rol exitosa ' + str(persona_delegado.primer_nombre)
        data = {'template': template, 'email_subject': subject, 'to_email': persona_delegado.email}
        Util.send_email(data)
        #try:
         #   Util.send_sms(persona_delegado.telefono_celular, sms)
          #  pass
        #except:
         #   return Response({'success':True,'detail':'Se realizó la asignación sin problema pero no se pudo enviar sms de confirmación'}, status=status.HTTP_200_OK)
        
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
    renderer_classes = (UserRender,)
    permission_classes = [IsAuthenticated, PermisoCrearUsuarios]

    def post(self, request):
        user_logeado = request.user.id_usuario
        data = request.data
        redirect_url=request.data.get('redirect_url','')
        
        if " " in data['nombre_de_usuario']:
            return Response({'success':False,'detail':'No puede contener espacios en el nombre de usuario'},status=status.HTTP_403_FORBIDDEN)

        persona = Personas.objects.filter(id_persona=data['persona']).first()
        
        if not persona:
            return Response ({'success':False,'detail':'No existe la persona'},status=status.HTTP_404_NOT_FOUND)
        
        usuario = persona.user_set.exclude(id_usuario=1)
      
        if usuario:
            return Response ({'success':False,'detail':'Esta persona ya tiene un usuario'},status=status.HTTP_403_FORBIDDEN)

        #CREAR USUARIO
        serializer = self.serializer_class(data=data, many=False)
        serializer.is_valid(raise_exception=True)
        nombre_usuario_creado = serializer.validated_data.get('nombre_de_usuario')
        tipo_usuario = serializer.validated_data.get('tipo_usuario')
        if tipo_usuario != 'I':
            return Response({'success':False,'detail': 'El tipo de usuario debe ser interno'}, status=status.HTTP_403_FORBIDDEN)

        serializador = serializer.save()
        
        print('')
        #usuario = User.objects.get(nombre_de_usuario=nombre_usuario_creado)

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
        
        token = RefreshToken.for_user(serializador).access_token
        current_site=get_current_site(request).domain

        relativeLink= reverse('verify')
        absurl= 'http://'+ current_site + relativeLink + "?token="+ str(token) + '&redirect-url=' + redirect_url
        short_url = Util.get_short_url(request, absurl)
    
        Util.enviar_notificacion_verificacion(persona, absurl)
        
        return Response({'success':True,'detail': 'Creado exitosamente', 'usuario': serializer.data, 'Roles': roles, "redirect:":redirect_url}, status=status.HTTP_201_CREATED)

class RegisterExternoView(generics.CreateAPIView):
    serializer_class = RegisterExternoSerializer
    renderer_classes = (UserRender,)

    def post(self, request):
        user = request.data
        
        persona = Personas.objects.filter(id_persona=user['persona']).first()
        
        if not persona:
            return Response ({'success':False,'detail':'No existe la persona'},status=status.HTTP_404_NOT_FOUND)
        
        usuario = persona.user_set.exclude(id_usuario=1)
      
        if usuario:
            return Response ({'success':False,'detail':'Esta persona ya tiene un usuario'},status=status.HTTP_403_FORBIDDEN)

        redirect_url=request.data.get('redirect_url','')
        print(redirect_url)
        
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

        token = RefreshToken.for_user(serializer_response).access_token

        current_site=get_current_site(request).domain

        #persona = Personas.objects.get(id_persona = request.data['persona'])

        relativeLink= reverse('verify')
        absurl= 'http://'+ current_site + relativeLink + "?token="+ str(token) + '&redirect-url=' + redirect_url

        # short_url = Util.get_short_url(request, absurl)

        Util.enviar_notificacion_verificacion(persona, absurl)
    
        return Response([{"success":True, "detail":"Usuario creado correctamente"},user_data,{"redi:":redirect_url}], status=status.HTTP_201_CREATED)


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
            return redirect(redirect_url)
        except jwt.ExpiredSignatureError as identifier:
            return redirect(redirect_url)

        except jwt.exceptions.DecodeError as identifier:
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
        
        print('USUARIO',user)
        
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
                    
                    # AÑADIR INFO PERSONA
                    serializer_data['tipo_usuario'] = user.tipo_usuario
                    serializer_data['id_persona'] = user.persona.id_persona
                    serializer_data['tipo_persona'] = user.persona.tipo_persona
                    
                    user_info={'userinfo':serializer_data,'permisos':permisos_list,'representante_legal':representante_legal_list}
                    sms = "Has iniciado sesion en bia cormacarena"
                    Util.send_sms(user.persona.telefono_celular, sms)
                    
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

                                if user.persona.tipo_persona == 'N':
                                    sms = 'Usuario Cormacarena Bia bloqueado por limite de intentos, desbloquealo enviando un correo a admin@admin.com'
                                    context = {'primer_nombre': user.persona.primer_nombre}
                                    template = render_to_string(('email-blocked-user.html'), context)
                                    subject = 'Bloqueo de cuenta ' + user.persona.primer_nombre
                                    email_data = {'template': template, 'email_subject': subject, 'to_email': user.persona.email}
                                    Util.send_email(email_data)
                                    try:
                                        Util.send_sms(user.persona.telefono_celular, sms)
                                    except:
                                        return Response({'success':False,'detail': 'Se bloqueó el usuario pero no pudo enviar el sms, verificar servicio o número'}, status=status.HTTP_403_FORBIDDEN)
                                    return Response({'success':False,'detail':'Su usuario ha sido bloqueado'}, status=status.HTTP_403_FORBIDDEN)
                                else:
                                    sms = 'Usuario Cormacarena Bia bloqueado por limite de intentos, desbloquealo enviando un correo a admin@admin.com'
                                    context = {'razon_social': user.persona.razon_social}
                                    template = render_to_string(('email-blocked-user.html'), context)
                                    subject = 'Bloqueo de cuenta ' + user.persona.razon_social
                                    email_data = {'template': template, 'email_subject': subject, 'to_email': user.persona.email}
                                    Util.send_email(email_data)
                                    try:
                                        Util.send_sms(user.persona.telefono_celular, sms)
                                    except:
                                        return Response({'success':False,'detail': 'Se bloqueó el usuario pero no pudo enviar el sms, verificar servicio o número'}, status=status.HTTP_403_FORBIDDEN)
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
                return Response({'success':False,'detail': 'Usuario no verificado'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            UsuarioErroneo.objects.create(
                campo_usuario = data['nombre_de_usuario'],
                dirip = str(ip),
                dispositivo_conexion = device
            )
            return Response({'success':False,'detail':'No existe el nombre de usuario ingresado'}, status=status.HTTP_400_BAD_REQUEST)

class RequestPasswordResetEmail(generics.GenericAPIView):
    serializer_class = ResetPasswordEmailRequestSerializer

    def post(self,request):
        serializer=self.serializer_class(data=request.data)
        email = request.data['email']
        
        if User.objects.filter(persona__email=email).exists():
            user = User.objects.get(persona__email=email)
            uidb64 =signing.dumps({'user':str(user.id_usuario)})
            print(uidb64)
            token = PasswordResetTokenGenerator().make_token(user)
            current_site=get_current_site(request=request).domain
            relativeLink=reverse('password-reset-confirm',kwargs={'uidb64':uidb64,'token':token})
            redirect_url= request.data.get('redirect_url','')
            absurl='http://'+ current_site + relativeLink 
            if user.persona.tipo_persona == 'N':
                context = {
                'primer_nombre': user.persona.primer_nombre,
                'primer_apellido':user.persona.primer_apellido,
                'absurl': absurl + '?redirect-url='+ redirect_url,
                }
                template = render_to_string(('email-resetpassword.html'), context)
                subject = 'Actualiza tu contraseña ' + user.persona.primer_nombre
                data = {'template': template, 'email_subject': subject, 'to_email': user.persona.email}
                Util.send_email(data)
            else:
                context = {
                'razon_social': user.persona.razon_social,
                'absurl': absurl + '?redirect-url='+ redirect_url,
                }
                template = render_to_string(('email-resetpassword.html'), context)
                subject = 'Actualiza tu contraseña ' + user.persona.razon_social
                data = {'template': template, 'email_subject': subject, 'to_email': user.persona.email}
                Util.send_email(data)
        return Response( {'success':True,'detail':'Te enviamos el link para poder actualizar tu contraseña'},status=status.HTTP_200_OK)
    
    
# class RequestPasswordResetEmail(generics.CreateAPIView):
#     serializer_class = ResetPasswordEmailRequestSerializer
#     queryset = User.objects.all()
    
#     def post(self,request):
        
#         data = request.data
        
#         usuario = self.queryset.all().filter(nombre_de_usuario=data['nombre_de_usuario']).first()
        
#         if usuario:
#             if usuario.persona.tipo_persona == "N":
                
#                 if usuario.persona.email and not usuario.persona.telefono_celular:
                
#                 else:
#                     return ({'success':True,'detail':'Cual de los dos medios registrados quiere '})
            
#             else:
                
#                 if usuario.persona.email and not usuario.persona.telefono_celular_empresa:
                    
            

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
                
            print(request.query_params.get('redirect-url'))
            print(token)
            print(uidb64)
            return redirect(redirect_url+'?token-valid=True&?message=Credentials-valid?&uidb64='+uidb64+'&?token='+token)
        except encoding.DjangoUnicodeDecodeError as identifier:

            if not PasswordResetTokenGenerator().check_token(user):
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

#MOSTRAR EL NOMBRE DEL SUPER USUARIO
class GetNombreSuperUsuario(generics.RetrieveAPIView):
    
    serializer_class = GetSuperUsuarioSerializer
    queryset = User.objects.all()
    
    def get (self,request):
        
        user = request.user
        
        serializador = self.serializer_class(user)
        
        return Response({'success':True,'detail':'Petición exitosa','data':serializador.data},status=status.HTTP_200_OK)
    
# CONSULTAR NUEVO SUPER USUARIO FECHA ACTUAL

class GetNuevoSuperUsuario(generics.RetrieveAPIView):
    
    serializer_class = GetNuevoSuperUsuarioSerializer
    queryset = User.objects.all()
    
    def get (self,request):
        
        tipo_documento = request.query_params.get('tipo_documento')
        numero_documentos = request.query_params.get('numero_documento')
        fecha_sistema = datetime.now()
        
                
        nuevo_super_usuario = Personas.objects.filter(tipo_documento=tipo_documento,numero_documento=numero_documentos,fecha_a_finalizar_cargo_actual__gt=fecha_sistema).filter(~Q(id_cargo = None)).first()
        
        if nuevo_super_usuario:
            serializador = self.serializer_class(nuevo_super_usuario)
            return Response({'succes':True, 'detail':'Los datos coincidieron con la busqueda realizada.','data':serializador.data},status=status.HTTP_200_OK)
        
        else: 
            return Response({'succes':True, 'detail':'La persona no existe o no tiene cargo actual.'},status=status.HTTP_200_OK)

#BUSQUEDA AVANZADA PARA LA TABLA PERSONAS

class Busqueda_Avanzada(generics.ListAPIView):
    serializer_class = GetNuevoSuperUsuarioSerializer
    queryset = Personas.objects.all()
    
    def get(self,request):
    
        filter={}
        for key, value in request.query_params.items():
            if key in ['primer_nombre','primer_apellido','tipo_documento','numero_documento']:
                if key == 'primer_nombre'or key== 'primer_apellido':
                    filter[key+'__icontains'] = value
                elif key == 'numero_documento':
                    filter[key+'__startswith'] = value
                else:
                    filter[key] = value
                    
        fecha_sistema =  datetime.now()           
        filter['fecha_a_finalizar_cargo_actual__gt'] = fecha_sistema
                    
        persona = self.queryset.all().filter(**filter).filter(~Q(id_cargo = None))
        
        if persona:
            serializador = self.serializer_class(persona,many=True)
            return Response({'succes':True, 'detail':'Se encontraron las siguientes personas.','data':serializador.data},status=status.HTTP_200_OK)
        else: 
             return Response({'succes':False, 'detail':'La persona no se encontro.'},status=status.HTTP_200_OK)

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
            return Response({'success': True, 'detail': 'Se encontró el siguiente historico de activación para ese usuario', 'data': serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'detail': 'No se encontro historico de activación para ese usuario'}, status=status.HTTP_404_NOT_FOUND)
       