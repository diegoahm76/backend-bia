import json
from collections import Counter
from django.utils import timezone
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime,date,timedelta
from transversal.models.alertas_models import AlertasProgramadas, ConfiguracionClaseAlerta, FechaClaseAlerta, PersonasAAlertar
from seguridad.models import Personas
from transversal.serializers.alertas_serializers import AlertasProgramadasPostSerializer, AlertasProgramadasUpdateSerializer, ConfiguracionClaseAlertaGetSerializer, ConfiguracionClaseAlertaUpdateSerializer, FechaClaseAlertaDeleteSerializer, FechaClaseAlertaGetSerializer, FechaClaseAlertaPostSerializer, PersonasAAlertarDeleteSerializer, PersonasAAlertarGetSerializer, PersonasAAlertarPostSerializer
from django.db import transaction 
from django.db.models import Q

class ConfiguracionClaseAlertaUpdate(generics.UpdateAPIView):
    serializer_class = ConfiguracionClaseAlertaUpdateSerializer
    queryset = ConfiguracionClaseAlerta.objects.all()
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        instance = self.get_object()
        data_in=request.data
        # Verificar si la instancia existe
        if not instance:
            return Response({'detail': 'La configuración de clase de alerta no existe.'}, status=status.HTTP_404_NOT_FOUND)

        try:
            serializer = self.serializer_class(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
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
    
    def get(self,request):

           
        alerta = ConfiguracionClaseAlerta.objects.all()
                
        serializer = self.serializer_class(alerta,many=True)
        
        if not alerta:
            raise NotFound("No existen registros de alerta.")
        return Response({'success':True,'detail':"Se encontron los siguientes  registros.",'data':serializer.data},status=status.HTTP_200_OK)


class FechaClaseAlertaCreate(generics.CreateAPIView):
    serializer_class = FechaClaseAlertaPostSerializer
    permission_classes = [IsAuthenticated]
    queryset = FechaClaseAlerta.objects.all()
    
    def post(self,request):
        data_in = request.data

        if not ('age_cumplimiento' in data_in):
            data_in['age_cumplimiento']=None
        try:
            if 'age_cumplimiento' in data_in and data_in['age_cumplimiento']:
                fechas=FechaClaseAlerta.objects.filter(cod_clase_alerta=data_in['cod_clase_alerta'],dia_cumplimiento=data_in['dia_cumplimiento'], mes_cumplimiento=data_in['mes_cumplimiento'], age_cumplimiento=data_in['age_cumplimiento'])
            else:

                fechas=FechaClaseAlerta.objects.filter(cod_clase_alerta=data_in['cod_clase_alerta'],dia_cumplimiento=data_in['dia_cumplimiento'], mes_cumplimiento=data_in['mes_cumplimiento'], age_cumplimiento__isnull=True)
            if fechas:
                raise ValidationError("Ya existe esta fecha en la alerta.")
            serializer = self.serializer_class(data=data_in)
            serializer.is_valid(raise_exception=True)
            instance=serializer.save()
            # Obtener todas las fechas de la tabla FechaClaseAlerta
            alertas = AlertasProgramadas.objects.filter(dia_cumplimiento=instance.dia_cumplimiento,mes_cumplimiento=instance.mes_cumplimiento,agno_cumplimiento=instance.age_cumplimiento)
            #print(alertas)
      
            fecha_alerta={'dia_cumplimiento':instance.dia_cumplimiento,'mes_cumplimiento':instance.mes_cumplimiento,'agno_cumplimiento':instance.age_cumplimiento,'cod_clase_alerta':data_in['cod_clase_alerta']}
            crear_alerta=AlertasProgramadasCreate()
            print(instance)
            #raise ValidationError(instance)
            response_alerta=crear_alerta.crear_alerta_programada(fecha_alerta)
            if response_alerta.status_code!=status.HTTP_201_CREATED:
                return response_alerta
            #Fin
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

        configuracion = ConfiguracionClaseAlerta.objects.filter(cod_clase_alerta=data_in['cod_clase_alerta']).first()

        if not configuracion:
            raise ValidationError('No existe esta alerta.')

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
                
            directo = PersonasAAlertar.objects.filter(es_responsable_directo=True)
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
        
        if not persona:
            raise NotFound("No existe la persona a eliminar.")
        serializer = self.serializer_class(persona) 
        persona.delete()

        
        return Response({'success':True,'detail':'Se elimino la fecha correctamente.','data':serializer.data},status=status.HTTP_200_OK)
    
class PersonasAAlertarGetByConfAlerta(generics.ListAPIView):

    serializer_class = PersonasAAlertarGetSerializer
    queryset = PersonasAAlertar.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,cod):
        perfiles=[('Dire', 'Director'), ('CViv', 'Coordinador de Viveros'), ('RTra', 'Responsable de Transporte'), ('CAlm', 'Coordinador de Almacén'), ('Alma', 'Almacenista')]
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
                detalle=dato['nombre_completo']
            if dato['perfil_sistema']:
                destinatario="Perfil profesional"
                for perfil in perfiles:
                    if dato['perfil_sistema']==perfil[0]:
                        detalle=perfil[1]
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
        

            configuracion = ConfiguracionClaseAlerta.objects.filter(cod_clase_alerta=data_in['cod_clase_alerta']).first()
            if not configuracion:
                raise ValidationError("No existe configuracion de alerta asociada a este cod")

            data_alerta_programada = {}
            if not 'cant_dias_previas' in data_in:
                data_alerta_programada['ctdad_dias_alertas_previas'] = 0
            if not 'frecuencia_previas' in data_in:
                data_alerta_programada['frecuencia_alertas_previas'] = 0
            if not 'cant_dias_post' in data_in:
                data_alerta_programada['ctdad_repeticiones_post'] = 0
            if not 'frecuencia_post' in data_in:
                data_alerta_programada['frecuencia_repeticiones_post'] = 0

            data_alerta_programada['nivel_prioridad'] = configuracion.nivel_prioridad
            if 'id_persona_implicada' in data_in:
                data_alerta_programada['id_persona_implicada'] = data_in['id_persona_implicada']

            personas_alertar = PersonasAAlertar.objects.filter(cod_clase_alerta=data_in['cod_clase_alerta'])
            if not personas_alertar:
                raise NotFound('La alerta no tiene personal asignado.')

            cadena = ""
            cadena_lideres = ''
            cadena_personas = ''
            cadena_perfiles = ''
            for persona in personas_alertar:
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

            if not 'age_cumplimiento' in data_in:
                data_in['age_cumplimiento']=None
            fecha=FechaClaseAlerta.objects.filter(cod_clase_alerta=data_in['cod_clase_alerta'],dia_cumplimiento=data_in['dia_cumplimiento'], mes_cumplimiento=data_in['mes_cumplimiento'], age_cumplimiento=data_in['age_cumplimiento']).first()
            if  not fecha:
                raise ValidationError("la fecha programada no existe.")



            data_alerta_programada['dia_cumplimiento'] = fecha.dia_cumplimiento
            data_alerta_programada['mes_cumplimiento'] = fecha.mes_cumplimiento

            if fecha.age_cumplimiento:
                data_alerta_programada['agno_cumplimiento'] = fecha.age_cumplimiento
            data_alerta_programada['mensaje_base_del_dia'] = configuracion.mensaje_base_dia

            data_alerta_programada['id_modulo_destino'] = configuracion.id_modulo_destino.id_modulo
            data_alerta_programada['id_modulo_generador'] = configuracion.id_modulo_generador.id_modulo
            data_alerta_programada['cod_categoria_alerta'] = configuracion.cod_categoria_clase_alerta
            data_alerta_programada['tiene_implicado'] = configuracion.asignar_responsable

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

            data_alerta_programada['nivel_prioridad'] = configuracion.nivel_prioridad
            if 'id_persona_implicada' in data_in:
                data_alerta_programada['id_persona_implicada'] = data_in['id_persona_implicada']

            personas_alertar = PersonasAAlertar.objects.filter(cod_clase_alerta=instance.cod_clase_alerta)
            if not personas_alertar:
                raise NotFound('La alerta no tiene personal asignado.')

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