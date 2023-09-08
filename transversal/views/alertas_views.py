import copy
import json
from collections import Counter
from django.http import HttpResponse
from django.utils import timezone
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime,date,timedelta
from gestion_documental.views.configuracion_tipos_radicados_views import actualizar_conf_agno_sig
from recurso_hidrico.models.programas_models import ProyectosPORH
from recurso_hidrico.serializers.programas_serializers import GenerardorMensajeProyectosPORHGetSerializer, ProyectosPORHSerializer
from transversal.funtions.alertas import alerta_proyectos_vigentes_porh, generar_alerta_segundo_plano
from transversal.models.alertas_models import AlertasProgramadas, ConfiguracionClaseAlerta, FechaClaseAlerta, PersonasAAlertar
from seguridad.models import Personas
from transversal.serializers.alertas_serializers import AlertasProgramadasPostSerializer, AlertasProgramadasUpdateSerializer, ConfiguracionClaseAlertaGetSerializer, ConfiguracionClaseAlertaUpdateSerializer, FechaClaseAlertaDeleteSerializer, FechaClaseAlertaGetSerializer, FechaClaseAlertaPostSerializer, PersonasAAlertarDeleteSerializer, PersonasAAlertarGetSerializer, PersonasAAlertarPostSerializer
from django.db import transaction 
from django.db.models import Q
from seguridad.choices.subsistemas_choices import subsistemas_CHOICES
from seguridad.choices.perfiles_sistema_choices import PERFIL_SISTEMA_CHOICES
# from background_task import background

class ConfiguracionClaseAlertaUpdate(generics.UpdateAPIView):
    serializer_class = ConfiguracionClaseAlertaUpdateSerializer
    queryset = ConfiguracionClaseAlerta.objects.all()
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        instance = self.get_object()
        previus=copy.copy(instance)
        data_in=request.data
        # Verificar si la instancia existe
        if not instance:
            return Response({'detail': 'La configuración de clase de alerta no existe.'}, status=status.HTTP_404_NOT_FOUND)
        cant_dias_previas = instance.cant_dias_previas
        frecuencia_previas = instance.frecuencia_previas
        cant_dias_post = instance.cant_dias_post
        frecuencia_post = instance.frecuencia_post

        if 'cant_dias_previas' in data_in and data_in['cant_dias_previas']:
            cant_dias_previas = data_in['cant_dias_previas']

        if 'frecuencia_previas' in data_in and data_in['frecuencia_previas']:
            frecuencia_previas = data_in['frecuencia_previas']

        if 'cant_dias_post' in data_in and data_in['cant_dias_post']:
            cant_dias_post = data_in['cant_dias_post']

        if 'frecuencia_post' in data_in and data_in['frecuencia_post']:
            frecuencia_post = data_in['frecuencia_post']

        if frecuencia_previas and cant_dias_previas and frecuencia_previas >= cant_dias_previas:
            raise ValidationError("La frecuencia previa debe ser menor que la cantidad de días previos")

        if frecuencia_post and cant_dias_post and frecuencia_post >= cant_dias_post:
            raise ValidationError("La frecuencia posterior debe ser menor que la cantidad de días posteriores")

        try:
           
                
            serializer = self.serializer_class(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            instance=serializer.save()

            #if (instance.envios_email != previus.envios_email) or (instance.nivel_prioridad != previus.nivel_prioridad) or (instance.activa != previus.activa):
            print( "cambio")
            cambios={       
                        "envios_email": instance.envios_email,
                        "nivel_prioridad": instance.nivel_prioridad,
                        "activa": instance.activa
                        }
                
            alertas_programadas=AlertasProgramadas.objects.filter(cod_clase_alerta=instance.cod_clase_alerta)
            print(instance.cod_clase_alerta)
            actualizar_alerta_programada=AlertasProgramadasUpdate()
           
            for alerta_programada in alertas_programadas:
                print(alerta_programada.id_alerta_programada)
                response_alerta_programada=actualizar_alerta_programada.actualizar_alerta_programada(cambios,alerta_programada.id_alerta_programada)
                if response_alerta_programada.status_code!=status.HTTP_200_OK:
                    return response_alerta_programada
                print(response_alerta_programada.data)

        except ValidationError as e:       
            raise ValidationError(e.detail)


        return Response({'success': True, 'detail': 'Se actualizó la configuración de clase de alerta correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)


class ConfiguracionClaseAlertaGetByCod(generics.ListAPIView):

    serializer_class = ConfiguracionClaseAlertaGetSerializer
    queryset = ConfiguracionClaseAlerta.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,cod):

           
        alerta = ConfiguracionClaseAlerta.objects.filter(cod_clase_alerta=cod)
                
        serializer = self.serializer_class(alerta,many=True)
        
        if not alerta:
            raise NotFound("No existe esta alerta.")
        return Response({'success':True,'detail':"Se encontron los siguientes  registros.",'data':serializer.data},status=status.HTTP_200_OK)


class ConfiguracionClaseAlertaGet(generics.ListAPIView):

    serializer_class = ConfiguracionClaseAlertaGetSerializer
    queryset = ConfiguracionClaseAlerta.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,subsis):
        existe=False
        #print(subsistemas_CHOICES)
        for codigo, nombre in subsistemas_CHOICES:
            if codigo==subsis:
                existe =True
                break
        if not existe:
            raise ValidationError("Este codigo no corresponde a ningun subsistema registrado")
        alerta = ConfiguracionClaseAlerta.objects.filter(id_modulo_generador__subsistema=subsis)
                
        serializer = self.serializer_class(alerta,many=True)
        
        if not alerta:
            #alerta = ConfiguracionClaseAlerta.objects.all()
            #serializer = self.serializer_class(alerta,many=True)
            raise NotFound("No existen registros de alerta.")
        return Response({'success':True,'detail':"Se encontron los siguientes  registros.",'data':serializer.data},status=status.HTTP_200_OK)


class FechaClaseAlertaCreate(generics.CreateAPIView):
    serializer_class = FechaClaseAlertaPostSerializer
    permission_classes = [IsAuthenticated]
    queryset = FechaClaseAlerta.objects.all()
    
    def post(self,request):
        data_in = request.data
        dia= data_in.get('dia_cumplimiento')
        mes=data_in.get('mes_cumplimiento')
        agno=data_in.get('age_cumplimiento')

        if not ('age_cumplimiento' in data_in):
            data_in['age_cumplimiento']=None
        try:
            
           
            fechas=FechaClaseAlerta.objects.filter(cod_clase_alerta=data_in['cod_clase_alerta'],dia_cumplimiento=dia, mes_cumplimiento=mes)
            for fecha in fechas:
                if agno is None:
                    raise ValidationError("Esta alerta ya cuenta con fechas dirigidas a estos dias con año especifico.")
                if fecha.age_cumplimiento is None:
                    raise ValidationError("Esta alerta ya se encuentra configurada para esta fecha.")
                elif fecha.age_cumplimiento==agno:
                    raise ValidationError("Esta alerta ya se encuentra configurada para esta fecha.(CON AÑO)")

            serializer = self.serializer_class(data=data_in)
            serializer.is_valid(raise_exception=True)
            instance=serializer.save()

            fecha_alerta={'dia_cumplimiento':instance.dia_cumplimiento,'mes_cumplimiento':instance.mes_cumplimiento,'age_cumplimiento':instance.age_cumplimiento,'cod_clase_alerta':data_in['cod_clase_alerta']}
            crear_alerta=AlertasProgramadasCreate()

            response_alerta=crear_alerta.crear_alerta_programada(fecha_alerta)
            if response_alerta.status_code!=status.HTTP_201_CREATED:
                return response_alerta
           
            return Response({'success':True,'detail':'Se crearon los registros correctamente','data':{'fecha_clase_alerta':serializer.data,'alerta_programada':response_alerta.data['data']}},status=status.HTTP_201_CREATED)
        except ValidationError as e:       
            raise ValidationError(e.detail)
         
        
        
  
class FechaClaseAlertaDelete(generics.DestroyAPIView):

    serializer_class = FechaClaseAlertaDeleteSerializer
    queryset = FechaClaseAlerta.objects.all()
    permission_classes = [IsAuthenticated]
    
    def delete(self,request,cod):
        
        fecha = FechaClaseAlerta.objects.filter(id_fecha=cod).first()
        
        if not fecha:
            raise NotFound("No existe la fecha a eliminar.")
        with transaction.atomic():
            

            if fecha.age_cumplimiento:
                alertas_programadas = AlertasProgramadas.objects.filter(cod_clase_alerta=fecha.cod_clase_alerta,dia_cumplimiento=fecha.dia_cumplimiento, mes_cumplimiento=fecha.mes_cumplimiento, agno_cumplimiento=fecha.age_cumplimiento) 
            else:
                alertas_programadas = AlertasProgramadas.objects.filter(cod_clase_alerta=fecha.cod_clase_alerta,dia_cumplimiento=fecha.dia_cumplimiento, mes_cumplimiento=fecha.mes_cumplimiento, agno_cumplimiento__isnull=True) 

            # for i in alertas_programadas:
            #     print(str(i.dia_cumplimiento)+" "+str(i.mes_cumplimiento)+" "+str(i.agno_cumplimiento))
            serializer = self.serializer_class(fecha) 
            alertas_programadas.delete()
            fecha.delete()


        
        return Response({'success':True,'detail':'Se elimino la fecha correctamente.','data':serializer.data},status=status.HTTP_200_OK)
    

class FechaClaseAlertaGetByConfiguracion(generics.ListAPIView):

    serializer_class = FechaClaseAlertaGetSerializer
    queryset = FechaClaseAlerta.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,cod):

           
        fechas = FechaClaseAlerta.objects.filter(cod_clase_alerta=cod)
                
        
        
        if not fechas:
            raise NotFound("No existe fechas asociadas a esta alerta.")
        
        serializer = self.serializer_class(fechas,many=True)
        return Response({'success':True,'detail':"Se encontron los siguientes  registros.",'data':serializer.data},status=status.HTTP_200_OK)



class PersonasAAlertarCreate(generics.CreateAPIView):
    serializer_class = PersonasAAlertarPostSerializer
    permission_classes = [IsAuthenticated]
    queryset = PersonasAAlertar.objects.all()
    
    def crear_persona_alerta(self, data_in):

        programadas_actualizadas=[]
        if not 'cod_clase_alerta' in data_in:
            raise ValidationError('El código de la clase de alerta es requerido.')

        if not 'es_responsable_directo' in data_in:
            data_in['es_responsable_directo']=False

        data_in['registro_editable']=True
        configuracion = ConfiguracionClaseAlerta.objects.filter(cod_clase_alerta=data_in['cod_clase_alerta']).first()

        if not configuracion:
            raise ValidationError('No existe esta alerta.')

        #validacion si requiere responsable directo
        #raise ValidationError(ConfiguracionClaseAlerta.asignar_responsable)
        if data_in['es_responsable_directo']:
            #raise ValidationError("Esta alerta no requiere responsable directo.")
            if not configuracion.asignar_responsable:
                raise ValidationError("Esta alerta no requiere responsable directo.")

        if not 'id_persona' in data_in:
            data_in['id_persona'] = None
        if not 'id_unidad_org_lider' in data_in:
            data_in['id_unidad_org_lider'] = None
        if not 'perfil_sistema' in data_in:
            data_in['perfil_sistema'] = None   

        if data_in['id_persona'] is None and data_in['id_unidad_org_lider'] is None and data_in['perfil_sistema'] is None:
            raise ValidationError("Debe existir al menos un destinatario.")

        campos_no_nulos = sum([1 for campo in [data_in['id_persona'], data_in['perfil_sistema'], data_in['id_unidad_org_lider']] if campo is not None])

        # Verificamos que solo uno de los campos no sea nulo
        if campos_no_nulos != 1:
            raise ValidationError("Debe existir solo un destinatario válido.")

        # Verificar que no es un registro repetido
        registro_existente = PersonasAAlertar.objects.filter(
            id_persona=data_in['id_persona'],
            id_unidad_org_lider=data_in['id_unidad_org_lider'],
            perfil_sistema=data_in['perfil_sistema'],
            cod_clase_alerta=data_in['cod_clase_alerta']
        ).exists()

        if registro_existente:
            raise ValidationError("El destinatario ya existe en esta alerta.")

        if data_in['es_responsable_directo']:
                
            directo = PersonasAAlertar.objects.filter(es_responsable_directo=True,cod_clase_alerta=configuracion.cod_clase_alerta)
            if directo:
                raise ValidationError("Ya existe un responsable directo")
        
        try:
            serializador = PersonasAAlertarPostSerializer(data=data_in)
            
            serializador.is_valid(raise_exception=True)
            instance=serializador.save()
            #actualiza las personas en la alertas configuradas
            alertas_programadas =AlertasProgramadas.objects.filter(cod_clase_alerta=instance.cod_clase_alerta)
            #alertas_programadas_ids = AlertasProgramadas.objects.filter(cod_clase_alerta=instance.cod_clase_alerta).values_list('id_alerta_programada', flat=True)
            if alertas_programadas:
                actualizar_programadas=AlertasProgramadasUpdate()

                for programada in alertas_programadas:
                    Response_programada=actualizar_programadas.actualizar_alerta_programada({},programada.id_alerta_programada)
                    if Response_programada.status_code!=status.HTTP_200_OK:
                        return Response_programada
                    programadas_actualizadas.append(Response_programada.data['data'])
            #fin

            return Response({'success': True, 'detail': 'Se crearon los registros correctamente', 'data': serializador.data,'alertas_programadas':programadas_actualizadas}, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            raise ValidationError( e.detail)

    def post(self, request, *args, **kwargs):
        data_in = request.data
        response_data = self.crear_persona_alerta(data_in)
        return response_data

class PersonasAAlertarDelete(generics.DestroyAPIView):

    serializer_class = PersonasAAlertarDeleteSerializer
    queryset = PersonasAAlertar.objects.all()
    permission_classes = [IsAuthenticated]
    
    def delete(self,request,pk):
        
        persona = PersonasAAlertar.objects.filter(id_persona_alertar=pk).first()
        cambios_alergas_generadas={}
        programadas_actualizadas=[]
        if not persona:
            raise NotFound("No existe la persona a eliminar.")
        if persona.es_responsable_directo:
                if persona.id_persona: 
                    cambios_alergas_generadas['id_persona_implicada']=None
                if persona.id_unidad_org_lider:
                    cambios_alergas_generadas['id_und_org_lider_implicada']=None
                if persona.perfil_sistema:
                    cambios_alergas_generadas['perfil_sistema_implicado']=None
                print("ES RESPONSABLE DIRECTO Y"+str(cambios_alergas_generadas))
                #cambios_alergas_generadas['tiene_implicado']=False
        serializer = self.serializer_class(persona) 
        persona.delete()
        alertas_programadas =AlertasProgramadas.objects.filter(cod_clase_alerta=persona.cod_clase_alerta)
        #alertas_programadas_ids = AlertasProgramadas.objects.filter(cod_clase_alerta=instance.cod_clase_alerta).values_list('id_alerta_programada', flat=True)
        if alertas_programadas:
                actualizar_programadas=AlertasProgramadasUpdate()

                for programada in alertas_programadas:
                    Response_programada=actualizar_programadas.actualizar_alerta_programada(cambios_alergas_generadas,programada.id_alerta_programada)
                    if Response_programada.status_code!=status.HTTP_200_OK:
                        return Response_programada
                    programadas_actualizadas.append(Response_programada.data['data'])
            #fin




        
        return Response({'success':True,'detail':'Se elimino la fecha correctamente.','data':serializer.data},status=status.HTTP_200_OK)
    
class PersonasAAlertarGetByConfAlerta(generics.ListAPIView):

    serializer_class = PersonasAAlertarGetSerializer
    queryset = PersonasAAlertar.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,cod):
        
        
        #perfiles=[('Dire', 'Director'), ('CViv', 'Coordinador de Viveros'), ('RTra', 'Responsable de Transporte'), ('CAlm', 'Coordinador de Almacén'), ('Alma', 'Almacenista')]
        perfiles=PERFIL_SISTEMA_CHOICES
        #print(perfiles)
        dicccionario=[]
        
        personas_alertar = PersonasAAlertar.objects.filter(cod_clase_alerta=cod)
                
        
        #print(perfiles)
        if not personas_alertar:
            raise NotFound("No existe esta alerta.")
        
        serializer = self.serializer_class(personas_alertar,many=True)
        
        datos=serializer.data
        diccionario_ordenado=[]
        for dato in datos:
 
            
            destinatario=""
            detalle=""
            nombre=""
            principal="No"
            #si es persona especifica
            if dato['id_persona']:
                destinatario="Persona especifica"
                detalle=dato['numero_documento']
                nombre=dato['nombre_completo']
            if dato['perfil_sistema']:
                destinatario="Perfil profesional"
                for cod,nombre_perfil in perfiles:
                    if dato['perfil_sistema']==cod:
                        detalle=nombre_perfil
                        break
            if dato['id_unidad_org_lider']:
                destinatario="Líder de grupo"
                detalle=dato['nombre_unidad']
            
            if dato['es_responsable_directo']:
                principal='Si'
            #print(destinatario +" "+detalle+" "+nombre+" "+" "+str(principal))
            diccionario_ordenado.append({**dato,'datos_reordenados':{'destinatario':destinatario,'detalle':detalle,"nombre":nombre,"principal":principal}})



        return Response({'success':True,'detail':"Se encontron los siguientes  registros.",'data':diccionario_ordenado},status=status.HTTP_200_OK)


 


class AlertasProgramadasCreate(generics.CreateAPIView):
    queryset = AlertasProgramadas.objects.all()
    serializer_class = AlertasProgramadasPostSerializer
    permission_classes = [IsAuthenticated]

    def crear_alerta_programada(self, data_in):
        
            print(data_in)
            configuracion = ConfiguracionClaseAlerta.objects.filter(cod_clase_alerta=data_in['cod_clase_alerta']).first()
            if not configuracion:
                raise ValidationError("No existe configuracion de alerta asociada a este cod")

            data_alerta_programada = {}
            
            if configuracion.cant_dias_previas:
                data_alerta_programada['ctdad_dias_alertas_previas'] = configuracion.cant_dias_previas
            else:
                data_alerta_programada['ctdad_dias_alertas_previas'] = 0    

            if configuracion.frecuencia_previas:
                data_alerta_programada['frecuencia_alertas_previas'] = configuracion.frecuencia_previas
            else:
                data_alerta_programada['frecuencia_alertas_previas'] = 0

            if configuracion.cant_dias_post:
                data_alerta_programada['ctdad_repeticiones_post'] = configuracion.cant_dias_post
            else:
                data_alerta_programada['ctdad_repeticiones_post']=0
            
            if configuracion.frecuencia_post:
                data_alerta_programada['frecuencia_repeticiones_post'] = configuracion.frecuencia_post
            else:
                data_alerta_programada['frecuencia_repeticiones_post'] = 0
                
            data_alerta_programada['nivel_prioridad'] = configuracion.nivel_prioridad
            if 'id_persona_implicada' in data_in:
                data_alerta_programada['id_persona_implicada'] = data_in['id_persona_implicada']

            personas_alertar = PersonasAAlertar.objects.filter(cod_clase_alerta=data_in['cod_clase_alerta'])
            #if not personas_alertar:
            #    raise NotFound('La alerta no tiene personal asignado.')

            cadena = ""
            cadena_lideres = ""
            cadena_personas = ""
            cadena_perfiles = ""
            for persona in personas_alertar:
                if persona.id_persona and persona.es_responsable_directo:
                    data_alerta_programada['id_persona_implicada'] = persona.id_persona.id_persona

                if persona.id_unidad_org_lider and persona.es_responsable_directo:
                    data_alerta_programada['id_und_org_lider_implicada'] = persona.id_unidad_org_lider.id_unidad_organizacional
                #print("#########"+str(persona.perfil_sistema))
                #print("############"+str(persona.es_responsable_directo))
                if persona.perfil_sistema and persona.es_responsable_directo:
                    
                    data_alerta_programada['perfil_sistema_implicado'] = persona.perfil_sistema

                if not(persona.es_responsable_directo):
                    if persona.id_unidad_org_lider:
                        cadena_lideres += str(persona.id_unidad_org_lider.id_unidad_organizacional) + "|"

                    if persona.perfil_sistema:
                        cadena_perfiles += str(persona.perfil_sistema) + "|"

                    if persona.id_persona:
                        cadena_personas += str(persona.id_persona.id_persona) + "|"

            data_alerta_programada['id_und_org_lider_alertar'] = cadena_lideres
            data_alerta_programada['id_perfiles_sistema_alertar'] = cadena_perfiles
            data_alerta_programada['id_personas_alertar'] = cadena_personas
            data_alerta_programada['cod_clase_alerta'] = configuracion.cod_clase_alerta
            data_alerta_programada['nombre_clase_alerta'] = configuracion.nombre_clase_alerta
            #data_alerta_programada['']

            if not 'age_cumplimiento' in data_in:
                data_in['age_cumplimiento']=None
            fecha=FechaClaseAlerta.objects.filter(cod_clase_alerta=data_in['cod_clase_alerta'],dia_cumplimiento=data_in['dia_cumplimiento'], mes_cumplimiento=data_in['mes_cumplimiento'], age_cumplimiento=data_in['age_cumplimiento']).first()
            #raise ValidationError(str(fecha))
            #if  not fecha:
            #    raise ValidationError("la fecha programada no existe.")



            data_alerta_programada['dia_cumplimiento'] = data_in['dia_cumplimiento']
            data_alerta_programada['mes_cumplimiento'] =data_in['mes_cumplimiento']

            if data_in['age_cumplimiento']:
                data_alerta_programada['agno_cumplimiento'] =data_in['age_cumplimiento']
            data_alerta_programada['mensaje_base_del_dia'] = configuracion.mensaje_base_dia
            data_alerta_programada['mensaje_base_previo'] = configuracion.mensaje_base_previo
            data_alerta_programada['mensaje_base_vencido'] = configuracion.mensaje_base_vencido
            

            data_alerta_programada['id_modulo_destino'] = configuracion.id_modulo_destino.id_modulo
            data_alerta_programada['id_modulo_generador'] = configuracion.id_modulo_generador.id_modulo
            data_alerta_programada['cod_categoria_alerta'] = configuracion.cod_categoria_clase_alerta
            data_alerta_programada['tiene_implicado'] = configuracion.asignar_responsable
            data_alerta_programada['nombre_funcion_comple_mensaje']=configuracion.nombre_funcion_comple_mensaje
            data_alerta_programada['activa'] = configuracion.activa

            serializer = AlertasProgramadasPostSerializer(data=data_alerta_programada)
            serializer.is_valid(raise_exception=True)
            serializer.save()

            return Response({'success': True, 'detail': 'Alertas programadas creadas correctamente.','data':serializer.data}, status=status.HTTP_201_CREATED)

    def post(self, request, *args, **kwargs):
        data_in = request.data
        response = self.crear_alerta_programada(data_in)
        return response



class AlertasProgramadasUpdate(generics.UpdateAPIView):
    serializer_class = AlertasProgramadasUpdateSerializer
    queryset = AlertasProgramadas.objects.all()
    permission_classes = [IsAuthenticated]

    def actualizar_alerta_programada(self,data,pk):
        
        data_in=data
        # Obtener la instancia existente para actualizar
        instance =AlertasProgramadas.objects.filter(id_alerta_programada=pk).first()

        # Verificar si la instancia existe
        if not instance:
            return Response({'detail': 'La alerta programada no existe.'}, status=status.HTTP_404_NOT_FOUND)

        # Obtener los datos recibidos en la solicitud
    
        try:
            #Llenado de datos con base de datos
            configuracion = ConfiguracionClaseAlerta.objects.filter(cod_clase_alerta=instance.cod_clase_alerta.cod_clase_alerta).first()
            
            if not configuracion:
                raise ValidationError("No existe configuracion de alerta asociada a este cod")

            data_alerta_programada = {}
            #data_alerta_programada.update(data_in)
            # if not 'cant_dias_previas' in data_in:
            #     data_alerta_programada['ctdad_dias_alertas_previas'] = 0
            # if not 'frecuencia_previas' in data_in:
            #     data_alerta_programada['frecuencia_alertas_previas'] = 0
            # if not 'cant_dias_post' in data_in:
            #     data_alerta_programada['ctdad_repeticiones_post'] = 0
            # if not 'frecuencia_post' in data_in:
            #     data_alerta_programada['frecuencia_repeticiones_post'] = 0

            # data_alerta_programada['requiere_envio_email']=configuracion.envios_email
            # data_alerta_programada['nivel_prioridad'] = configuracion.nivel_prioridad
            # data_alerta_programada['ctdad_dias_alertas_previas']=configuracion.cant_dias_previas
            # data_alerta_programada['frecuencia_alertas_previas']=configuracion.frecuencia_previas
            # data_alerta_programada['ctdad_repeticiones_post']=configuracion.cant_dias_post
            # data_alerta_programada['frecuencia_repeticiones_post']=configuracion.frecuencia_post

            if configuracion.cant_dias_previas:
                data_alerta_programada['ctdad_dias_alertas_previas'] = configuracion.cant_dias_previas
            else:
                data_alerta_programada['ctdad_dias_alertas_previas'] = 0    

            if configuracion.frecuencia_previas:
                data_alerta_programada['frecuencia_alertas_previas'] = configuracion.frecuencia_previas
            else:
                data_alerta_programada['frecuencia_alertas_previas'] = 0

            if configuracion.cant_dias_post:
                data_alerta_programada['ctdad_repeticiones_post'] = configuracion.cant_dias_post
            else:
                data_alerta_programada['ctdad_repeticiones_post']=0
            
            if configuracion.frecuencia_post:
                data_alerta_programada['frecuencia_repeticiones_post'] = configuracion.frecuencia_post
            else:
                data_alerta_programada['frecuencia_repeticiones_post'] = 0
                

            #if 'id_persona_implicada' in data_in:
            #    data_alerta_programada['id_persona_implicada'] = data_in['id_persona_implicada']

            personas_alertar = PersonasAAlertar.objects.filter(cod_clase_alerta=instance.cod_clase_alerta)
            #if not personas_alertar:
            #    raise NotFound('La alerta no tiene personal asignado.')

            cadena = ""
            cadena_lideres = ''
            cadena_personas = ''
            cadena_perfiles = ''
            for persona in personas_alertar:
                #print(persona.perfil_sistema)
                if persona.id_persona and persona.es_responsable_directo:
                    data_alerta_programada['id_persona_implicada'] = persona.id_persona.id_persona

                if persona.id_unidad_org_lider and persona.es_responsable_directo:
                    data_alerta_programada['id_und_org_lider_implicada'] = persona.id_unidad_org_lider.id_unidad_organizacional

                if persona.perfil_sistema and persona.es_responsable_directo:
                    data_alerta_programada['perfil_sistema_implicado'] = persona.perfil_sistema

                if not(persona.es_responsable_directo):
                    if persona.id_unidad_org_lider:
                        cadena_lideres += str(persona.id_unidad_org_lider.id_unidad_organizacional) + "|"

                    if persona.perfil_sistema:
                        cadena_perfiles += str(persona.perfil_sistema) + "|"

                    if persona.id_persona:
                        cadena_personas += str(persona.id_persona.id_persona) + "|"

            data_alerta_programada['id_und_org_lider_alertar'] = cadena_lideres
            data_alerta_programada['id_perfiles_sistema_alertar'] = cadena_perfiles
            data_alerta_programada['id_personas_alertar'] = cadena_personas
            data_alerta_programada['cod_clase_alerta'] = configuracion.cod_clase_alerta
            data_alerta_programada['nombre_clase_alerta'] = configuracion.nombre_clase_alerta
            data_alerta_programada['id_modulo_destino'] = configuracion.id_modulo_destino.id_modulo
            data_alerta_programada['id_modulo_generador'] = configuracion.id_modulo_generador.id_modulo
            data_alerta_programada['cod_categoria_alerta'] = configuracion.cod_categoria_clase_alerta
            data_alerta_programada['tiene_implicado'] = configuracion.asignar_responsable
            data_alerta_programada['activa'] = configuracion.activa

            #fin
            data_alerta_programada.update(data_in)
            # Crear una nueva instancia del serializador utilizando la instancia y los datos recibidos
            serializer =AlertasProgramadasUpdateSerializer(instance, data=data_alerta_programada, partial=True)
            
            # Validar los datos recibidos
            serializer.is_valid(raise_exception=True)
            
            # Guardar los datos actualizados
            serializer.save()
        except ValidationError as e:
            raise ValidationError(e.detail)

        # Respuesta exitosa con los datos actualizados
        return Response({
            'success': True,
            'detail': 'Se actualizó la alerta programada correctamente.',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

    def put(self, request, pk):
        data_in = request.data
        
        response= self.actualizar_alerta_programada(data_in,pk)
        return response
    




##funciones para complementar mensajes

##ALERTA RECURSO HIDICO

class AlertaProyectosVigentesGet(generics.ListAPIView):
    serializer_class=GenerardorMensajeProyectosPORHGetSerializer
    queryset = ProyectosPORH.objects.all()
    permission_classes = [IsAuthenticated]


    def get(self, request):
       
        mensaje=""
        hoy = date.today()
        
        
        #proyectos_vigentes = ProyectosPORH.objects.filter(Q(vigencia_inicial__lte=hoy)  & Q(vigencia_final__lte=hoy))
        proyectos_vigentes = ProyectosPORH.objects.filter(Q(vigencia_inicial__lte=hoy) & Q(vigencia_final__gte=hoy))
        serializador = self.serializer_class(proyectos_vigentes, many=True)
        #for dato in serializador.data:
            
            #mensaje+="Proyecto "+str(dato['id_proyecto'])+" ("+str(dato['nombre'])+")"+" del Programa "+str(dato['id_programa'])+" ("+str(dato['nombre_programa'])+")"+"  del Plan de Ordenamiento de Recurso Hídrico "+str(dato['id_porh'])+" ("+str(dato['nombre_porh'])+")"+".\n"
            #print(mensaje)
        mensaje=alerta_proyectos_vigentes_porh()

            
        return Response({'success': True, 'detail': 'Se encontraron los siguientes registros.', 'data': serializador.data,'mensaje':mensaje}, status=status.HTTP_200_OK)





def mi_vista(request):

    #generar_alerta_segundo_plano()  
    actualizar_conf_agno_sig()
    return HttpResponse("Tarea en segundo plano programada.")