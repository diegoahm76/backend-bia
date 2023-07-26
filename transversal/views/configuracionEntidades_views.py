import copy
from django.forms import ValidationError
from django.db.models import Max
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from seguridad.utils import Util

from transversal.serializers.entidades_serializers import ConfiguracionEntidadSerializer, HistoricoPerfilesEntidadGetSerializer, PersonaEntidadCormacarenaGetSerializer
from transversal.models import ConfiguracionEntidad,HistoricoPerfilesEntidad
from seguridad.models import Personas


class PersonaEntidadCormacarenaGetView(generics.GenericAPIView):
    serializer_class = PersonaEntidadCormacarenaGetSerializer 
    permission_classes = [IsAuthenticated]   
    
    def get(self, resquest):
        queryset = Personas.objects.get(id_persona=3)
        if not queryset:
            raise NotFound('No se encontró entidad registrada con el parámetro ingresado')
        serializer = self.serializer_class(queryset)
        return Response({'success': True, 'detail':'Se muestra los datos de la entidad', 'data': serializer.data}, status=status.HTTP_200_OK) 


class GetConfiguracionEntidadByID(generics.GenericAPIView):

    serializer_class = ConfiguracionEntidadSerializer
    queryset = ConfiguracionEntidad.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,pk):
        
        confEntidad = ConfiguracionEntidad.objects.filter(id_persona_entidad=pk)
        serializer = self.serializer_class(confEntidad,many=True)
        
        if not confEntidad:
            raise NotFound("El registro de configuracion  que busca no existe")
        
        return Response({'success':True,'detail':"Se encontro el siguiente registro.",'data':serializer.data},status=status.HTTP_200_OK)
            

class UpdateConfiguracionEntidad(generics.UpdateAPIView):
    serializer_class = ConfiguracionEntidadSerializer
    queryset = ConfiguracionEntidad.objects.all()
    lookup_field = 'id_persona_entidad'
    permission_classes = [IsAuthenticated]
    def buscarConsecutivo(self,cod_perfil_histo):
        max_valor = HistoricoPerfilesEntidad.objects.filter(cod_tipo_perfil_histo=cod_perfil_histo).aggregate(max_valor=Max('consec_asignacion_perfil_histo'))
        print("dato maximo de "+str(cod_perfil_histo))
        print(max_valor)
        if not max_valor['max_valor']:
            print("NO EXISTE REGISTRO")
            return(0)
        else:

            print(max_valor['max_valor'])
            return max_valor['max_valor']
        

    
    def registrarHistoricoPerfilesEntidad(self,cod_tipo_perfil,consec,id_persona,fecha_inicio_periodo,observaciones,funcionario):
        
        consecutivo=self.buscarConsecutivo(cod_tipo_perfil)
        print(consecutivo)
        historico_perfil = HistoricoPerfilesEntidad(
                            id_persona_entidad_id=3,
                            cod_tipo_perfil_histo=cod_tipo_perfil,
                            consec_asignacion_perfil_histo=consecutivo+1,
                            id_persona_perfil_histo_id=id_persona.id_persona,
                            fecha_inicio_periodo=fecha_inicio_periodo,
                            fecha_fin_periodo=timezone.now(),
                            observaciones_cambio=observaciones,
                            id_persona_cambia_id=funcionario
                            )
        historico_perfil.save()

        

    
    def put(self, request, *args, **kwargs):
        instance = self.get_object()  # Obtener la instancia del objeto a actualizar
        data_nueva = request.data
        data_in = request.data
        funcionario = request.user.persona.id_persona
        instance_previous=copy.copy(instance)
        ##si el dato que cambia es el director
        if instance.id_persona_director_actual:##si existe
            
            #si existe verifica que sea diferente
            if int(instance.id_persona_director_actual.id_persona) != int(data_nueva['id_persona_director_actual']) :
                #instance.fecha_inicio_dir_actual = timezone.now()
                data_nueva['fecha_inicio_dir_actual']=timezone.now()
                print(instance.fecha_inicio_dir_actual)

                 #realiza el registro en historial
                cod_tipo_perfil='Dire'   
                consec=0
                id_persona=instance.id_persona_director_actual
                fecha_inicio_periodo=instance.fecha_inicio_dir_actual
                observaciones=request.data.get('observaciones_de_cambio_director')
                self.registrarHistoricoPerfilesEntidad(cod_tipo_perfil,consec,id_persona,fecha_inicio_periodo,observaciones,funcionario)

            else:#sino no no cambia la fecha
                data_nueva['fecha_inicio_dir_actual']=instance.fecha_inicio_dir_actual
        else:#sino existe lo crea 
        
                if data_nueva['id_persona_director_actual']:
                    instance.fecha_inicio_dir_actual = timezone.now()
                    data_nueva['fecha_inicio_dir_actual']=timezone.now()
              
        ##si es el coordinador de almacen
        if instance.id_persona_coord_almacen_actual:##si existe
            
            #si existe verifica que sea diferente
            if int(instance.id_persona_coord_almacen_actual.id_persona) != int(data_nueva['id_persona_coord_almacen_actual']) :
                #instance.fecha_inicio_coord_alm_actual = timezone.now()
                data_nueva['fecha_inicio_coord_alm_actual']=timezone.now()
                print(instance.fecha_inicio_coord_alm_actual)

                 #realiza el registro en historial
                cod_tipo_perfil='CAlm'   
                consec=0
                id_persona=instance.id_persona_coord_almacen_actual
                fecha_inicio_periodo=instance.fecha_inicio_coord_alm_actual
                observaciones=request.data.get('observaciones_de_cambio_coord_almacen')
                self.registrarHistoricoPerfilesEntidad(cod_tipo_perfil,consec,id_persona,fecha_inicio_periodo,observaciones,funcionario)

            else:#sino no no cambia la fecha
                data_nueva['fecha_inicio_coord_alm_actual']=instance.fecha_inicio_coord_alm_actual
        else:#sino existe lo crea 
        
                if data_nueva['id_persona_coord_almacen_actual']:
                    instance.fecha_inicio_coord_alm_actual = timezone.now()
                    data_nueva['fecha_inicio_coord_alm_actual']=timezone.now()
        

        #si es responsable de transporte
        if instance.id_persona_respon_transporte_actual:##si existe
            
            #si existe verifica que sea diferente
            if int(instance.id_persona_respon_transporte_actual.id_persona) != int(data_nueva['id_persona_respon_transporte_actual']) :
                #instance.fecha_inicio_respon_trans_actual = timezone.now()
                data_nueva['fecha_inicio_respon_trans_actual']=timezone.now()
                print(instance.fecha_inicio_respon_trans_actual)

                 #realiza el registro en historial
                cod_tipo_perfil='RTra'   
                consec=0
                id_persona=instance.id_persona_respon_transporte_actual
                fecha_inicio_periodo=instance.fecha_inicio_respon_trans_actual
                observaciones=request.data.get('observaciones_de_cambio_respon_transporte')
                self.registrarHistoricoPerfilesEntidad(cod_tipo_perfil,consec,id_persona,fecha_inicio_periodo,observaciones,funcionario)

            else:#sino no no cambia la fecha
                data_nueva['fecha_inicio_respon_trans_actual']=instance.fecha_inicio_respon_trans_actual
        else:#sino existe lo crea 
        
                if data_nueva['id_persona_respon_transporte_actual']:
                    instance.fecha_inicio_respon_trans_actual = timezone.now()
                    data_nueva['fecha_inicio_respon_trans_actual']=timezone.now()

        #si el coordinador de vivero

        if instance.id_persona_coord_viveros_actual:##si existe
            
            #si existe verifica que sea diferente
            if int(instance.id_persona_coord_viveros_actual.id_persona) != int(data_nueva['id_persona_coord_viveros_actual']) :
                #instance.fecha_inicio_coord_viv_actual = timezone.now()
                data_nueva['fecha_inicio_coord_viv_actual']=timezone.now()
                print(instance.fecha_inicio_coord_viv_actual)

                 #realiza el registro en historial
                cod_tipo_perfil='CViv'   
                consec=0
                id_persona=instance.id_persona_coord_viveros_actual
                fecha_inicio_periodo=instance.fecha_inicio_coord_viv_actual
                observaciones=request.data.get('observaciones_de_cambio_coord_viveros')
                self.registrarHistoricoPerfilesEntidad(cod_tipo_perfil,consec,id_persona,fecha_inicio_periodo,observaciones,funcionario)

            else:#sino no no cambia la fecha
                data_nueva['fecha_inicio_coord_viv_actual']=instance.fecha_inicio_coord_viv_actual
        else:#sino existe lo crea 
        
                if data_nueva['id_persona_coord_viveros_actual']:
                    instance.fecha_inicio_coord_viv_actual = timezone.now()
                    data_nueva['fecha_inicio_coord_viv_actual']=timezone.now()

    ##si el dato que cambia es el almacenista

        if instance.id_persona_almacenista:##si existe
            
            #si existe verifica que sea diferente
            if int(instance.id_persona_almacenista.id_persona) != int(data_nueva['id_persona_almacenista']) :
                #instance.fecha_inicio_almacenista = timezone.now()
                data_nueva['fecha_inicio_almacenista']=timezone.now()
                print(instance.fecha_inicio_almacenista)

                 #realiza el registro en historial
                cod_tipo_perfil='Alma'   
                consec=0
                id_persona=instance.id_persona_almacenista
                fecha_inicio_periodo=instance.fecha_inicio_almacenista
                observaciones=request.data.get('observaciones_de_cambio_almacenista')
                self.registrarHistoricoPerfilesEntidad(cod_tipo_perfil,consec,id_persona,fecha_inicio_periodo,observaciones,funcionario)

            else:#sino no no cambia la fecha
                data_nueva['fecha_inicio_almacenista']=instance.fecha_inicio_almacenista
        else:#sino existe lo crea 
        
                if data_nueva['id_persona_almacenista']:
                    instance.fecha_inicio_almacenista = timezone.now()
                    data_nueva['fecha_inicio_almacenista']=timezone.now()


        serializer = self.get_serializer(instance, data=data_nueva, partial=True)
        serializer.is_valid(raise_exception=True)
        
        self.perform_update(serializer)  # Guardar los cambios
        
        #AUDITORÍA
        usuario = request.user.id_usuario
        direccion=Util.get_client_ip(request)
        descripcion = {"NombreEntidad": str(3) }
        valores_actualizados = {'current': instance, 'previous': instance_previous}

        auditoria_data = {
            "id_usuario" : usuario,
            "id_modulo" : 109,
            "cod_permiso": "AC",
            "subsistema": 'TRSV',
            "dirip": direccion,
            "descripcion": descripcion, 
            "valores_actualizados": valores_actualizados
        }
        Util.save_auditoria(auditoria_data)        

        return Response({'success':True,'detail':"Se realizo la configuracion  correctamente.","data":serializer.data},status=status.HTTP_200_OK)


class HistoricoPerfilesEntidadGet(generics.GenericAPIView):

    serializer_class = HistoricoPerfilesEntidadGetSerializer
    queryset = HistoricoPerfilesEntidad.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,para):
        
        confEntidad = HistoricoPerfilesEntidad.objects.filter(cod_tipo_perfil_histo=para)
        serializer = self.serializer_class(confEntidad,many=True)
        
        if not confEntidad:
            raise NotFound("El registro de configuracion  que busca no existe")
        
        return Response({'success':True,'detail':"Se encontraron los siguientes  registros.",'data':serializer.data},status=status.HTTP_200_OK)
            