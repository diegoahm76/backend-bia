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

from transversal.serializers.alertas_serializers import AlertasProgramadasPostSerializer, ConfiguracionClaseAlertaGetSerializer, ConfiguracionClaseAlertaUpdateSerializer, FechaClaseAlertaDeleteSerializer, FechaClaseAlertaGetSerializer, FechaClaseAlertaPostSerializer, PersonasAAlertarDeleteSerializer, PersonasAAlertarGetSerializer, PersonasAAlertarPostSerializer

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



class FechaClaseAlertaCreate(generics.CreateAPIView):
    serializer_class = FechaClaseAlertaPostSerializer
    permission_classes = [IsAuthenticated]
    queryset = FechaClaseAlerta.objects.all()
    
    def post(self,request):
        data_in = request.data

        if not ('age_cumplimiento' in data_in):
            data_in['age_cumplimiento']=None
        try:
            fechas=FechaClaseAlerta.objects.filter(dia_cumplimiento=data_in['dia_cumplimiento'], mes_cumplimiento=data_in['mes_cumplimiento'], age_cumplimiento__isnull=True)
            if fechas:
                raise ValidationError("Ya existe esta fecha en la alerta.")
            serializer = self.serializer_class(data=data_in)
            serializer.is_valid(raise_exception=True)
            serializer.save()
        except ValidationError as e:       
            raise ValidationError(e.detail)
         
        
        return Response({'success':True,'detail':'Se crearon los registros correctamente','data':serializer.data},status=status.HTTP_201_CREATED)
  
class FechaClaseAlertaDelete(generics.DestroyAPIView):

    serializer_class = FechaClaseAlertaDeleteSerializer
    queryset = FechaClaseAlerta.objects.all()
    permission_classes = [IsAuthenticated]
    
    def delete(self,request,cod):
        
        fecha = FechaClaseAlerta.objects.filter(id_fecha=cod).first()
        
        if not fecha:
            raise NotFound("No existe la fecha a eliminar.")
        serializer = self.serializer_class(fecha) 
        fecha.delete()

        
        return Response({'success':True,'detail':'Se elimino la fecha correctamente.','data':serializer.data},status=status.HTTP_200_OK)
    

class FechaClaseAlertaGetByConfiguracion(generics.ListAPIView):

    serializer_class = FechaClaseAlertaGetSerializer
    queryset = FechaClaseAlerta.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,cod):

           
        fechas = FechaClaseAlerta.objects.filter(cod_clase_alerta=cod)
                
        serializer = self.serializer_class(fechas,many=True)
        
        if not fechas:
            raise NotFound("No existe fechas asociadas a esta alerta.")
        return Response({'success':True,'detail':"Se encontron los siguientes  registros.",'data':serializer.data},status=status.HTTP_200_OK)



class PersonasAAlertarCreate(generics.CreateAPIView):
    serializer_class = PersonasAAlertarPostSerializer
    permission_classes = [IsAuthenticated]
    queryset = PersonasAAlertar.objects.all()
    
    def crear_persona_alerta(self, data_in):
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
            raise ValidationError("El destinatario ya existe en la base de datos.")

        if data_in['es_responsable_directo']:
                
            directo = PersonasAAlertar.objects.filter(es_responsable_directo=True)
            if directo:
                raise ValidationError("Ya existe un responsable directo")
        
        try:
            serializador = PersonasAAlertarPostSerializer(data=data_in)
            
            serializador.is_valid(raise_exception=True)
            serializador.save()
            return Response({'success': True, 'detail': 'Se crearon los registros correctamente', 'data': serializador.data}, status=status.HTTP_201_CREATED)
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

           
        alerta = PersonasAAlertar.objects.filter(cod_clase_alerta=cod)
                
        serializer = self.serializer_class(alerta,many=True)
        
        if not alerta:
            raise NotFound("No existe esta alerta.")
        return Response({'success':True,'detail':"Se encontron los siguientes  registros.",'data':serializer.data},status=status.HTTP_200_OK)


 
class AlertasProgramadasCreate(generics.CreateAPIView):
    queryset = AlertasProgramadas.objects.all()
    serializer_class = AlertasProgramadasPostSerializer
    permission_classes = [IsAuthenticated]

    def crear_alerta_programada(self, data):
        
        try:


            serializer = AlertasProgramadasPostSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            print(serializer.data)
            return Response({'success': True, 'detail': 'Alerta programada creada correctamente.', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        
        except ValidationError as e:
            # Manejo de errores si algo sale mal en la lógica personalizada
             raise ValidationError  (e.detail)  
            

    def post(self, request, *args, **kwargs):
        data_in = request.data
        data_alerta_programada={}
        fechas=FechaClaseAlerta.objects.filter(cod_clase_alerta=data_in['cod_clase_alerta'])

        if not fechas:
            ValidationError("No tiene fechas programadas.")
        
        for fecha in fechas:
            print(fecha)

        configuracion=ConfiguracionClaseAlerta.objects.filter(cod_clase_alerta=data_in['cod_clase_alerta']).first()

        if not configuracion:
            raise ValidationError("No existe configuracion de alerta asociada a este cod")
        # alerta_programada=AlertasProgramadasCreate()
        
        if not 'cant_dias_previas' in data_in:
            data_alerta_programada['ctdad_dias_alertas_previas']=0
        if not 'frecuencia_previas' in data_in:
            data_alerta_programada['frecuencia_alertas_previas']=0
        if not 'cant_dias_post' in data_in:
            data_alerta_programada['ctdad_repeticiones_post']=0
        if not 'frecuencia_post' in data_in:
            data_alerta_programada['frecuencia_repeticiones_post']=0

        data_alerta_programada['nivel_prioridad']=data_in['nivel_prioridad']
        if 'id_persona_implicada' in data_in:
            data_alerta_programada['id_persona_implicada']=data_in['id_persona_implicada']
        
        
        for fecha in fechas:
            data_alerta_programada['cod_clase_alerta']=configuracion.cod_clase_alerta
            data_alerta_programada['nombre_clase_alerta']=configuracion.nombre_clase_alerta
            data_alerta_programada['dia_cumplimiento']=fecha.dia_cumplimiento
            data_alerta_programada['mes_cumplimiento']=fecha.mes_cumplimiento
            
            if fecha.age_cumplimiento:
                 data_alerta_programada['agno_cumplimiento']=fecha.agno_cumplimiento
            data_alerta_programada['mensaje_base_del_dia']=configuracion.mensaje_base_dia
            #nombre de la funcion
            #nivel_prioridad#formulario
            data_alerta_programada['id_modulo_destino']=configuracion.id_modulo_destino.id_modulo
            data_alerta_programada['id_modulo_generador']=configuracion.id_modulo_generador.id_modulo
            data_alerta_programada['cod_categoria_alerta']=configuracion.cod_categoria_clase_alerta
            #requiere_envio_email#formulario
            data_alerta_programada['tiene_implicado']=configuracion.asignar_responsable
            #id_und_org_lider_implicada#pendiente
            #perfil_sistema_implicado#pendiente
            #id_und_org_lider_alertar#pendiente
            data_alerta_programada['activa']=configuracion.activa
            
            print(data_alerta_programada)
                
            response = self.crear_alerta_programada(data_alerta_programada)
            #data_alerta_programada.clear()
        return response