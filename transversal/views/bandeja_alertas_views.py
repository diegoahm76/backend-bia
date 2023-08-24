import copy
from datetime import datetime

from rest_framework import generics
from transversal.models.alertas_models import FechaClaseAlerta
from transversal.models.entidades_models import ConfiguracionEntidad
from transversal.models.lideres_models import LideresUnidadesOrg

from transversal.serializers.alertas_serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

class BandejaAlertaPersonaGetByPersona(generics.ListAPIView):

    serializer_class = BandejaAlertaPersonaGetSerializer
    queryset = BandejaAlertaPersona.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,pk):

           
        bandeja = BandejaAlertaPersona.objects.filter(id_persona=pk)
                
        
        
        if not bandeja:
            raise NotFound("La persona no tiene bandeja de alertas porfavor comunicarse con un administrador.")
        
        serializer = self.serializer_class(bandeja,many=True)
        return Response({'success':True,'detail':"Se encontron los siguientes  registros.",'data':serializer.data},status=status.HTTP_200_OK)

class AlertasBandejaAlertaPersonaGetByBandeja(generics.ListAPIView):

    serializer_class = AlertasBandejaAlertaPersonaGetSerializer
    queryset = AlertasBandejaAlertaPersona.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request,pk):

           
        items = AlertasBandejaAlertaPersona.objects.filter(id_bandeja_alerta_persona=pk)
                
        
        if not items:
            raise NotFound("La bandeja no tiene items de alertas porfavor comunicarse con un administrador.")
        
        serializer = self.serializer_class(items,many=True)
        return Response({'success':True,'detail':"Se encontron los siguientes  registros.",'data':serializer.data},status=status.HTTP_200_OK)


class AlertasBandejaAlertaPersonaUpdate(generics.UpdateAPIView):
    serializer_class = AlertasBandejaAlertaPersonaPutSerializer
    queryset = AlertasBandejaAlertaPersona.objects.all()
    permission_classes = [IsAuthenticated]

    # def buscar_id_perfil(self,perfil):
    #     perfiles_actuales=ConfiguracionEntidad.objects.first()
    #     id=None
    #     if perfil == 'Dire':
    #         if perfiles_actuales.id_persona_director_actual:
    #             id=perfiles_actuales.id_persona_director_actual.id_persona
    #     elif perfil == 'CAlm':
    #         if perfiles_actuales.id_persona_coord_almacen_actual:
    #             id=perfiles_actuales.id_persona_coord_almacen_actual.id_persona
    #     elif perfil == 'RTra':
    #         if perfiles_actuales.id_persona_respon_transporte_actual:
    #             id=perfiles_actuales.id_persona_respon_transporte_actual.id_persona
    #     elif perfil == 'CViv':
    #         if perfiles_actuales.id_persona_coord_viveros_actual:
    #             id=perfiles_actuales.id_persona_coord_viveros_actual.id_persona
    #     elif perfil == 'Alma':
    #         if perfiles_actuales.id_persona_almacenista:
    #             id=perfiles_actuales.id_persona_almacenista.id_persona
    #     return id
    def buscar_codigo_por_id(self, id_persona):
        perfiles_actuales = ConfiguracionEntidad.objects.first()
        
        perfiles = {
            'Dire': perfiles_actuales.id_persona_director_actual,
            'CAlm': perfiles_actuales.id_persona_coord_almacen_actual,
            'RTra': perfiles_actuales.id_persona_respon_transporte_actual,
            'CViv': perfiles_actuales.id_persona_coord_viveros_actual,
            'Alma': perfiles_actuales.id_persona_almacenista,
        }
        
        for perfil, persona in perfiles.items():
            if persona and persona.id_persona == id_persona:
                return perfil
        
        return None
    
    
    def eliminar_elemento_en_arreglo(self,arreglo, id_a_eliminar):
        elemento_eliminado = False
        nuevo_arreglo = ''
        for elemento in arreglo:
            if str(elemento) != str(id_a_eliminar):
                nuevo_arreglo += elemento + '|'
            else:
                elemento_eliminado = True
        return nuevo_arreglo, elemento_eliminado
    
    def put(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        instance = self.get_object()
        previus=copy.copy(instance)
        data_in=request.data
        # Verificar si la instancia existe
        if not instance:
            return Response({'detail': 'El item de bandeja  no existe.'}, status=status.HTTP_404_NOT_FOUND)
        id_persona=instance.id_bandeja_alerta_persona.id_persona.id_persona
        #print("personaaa")
        #print(id_persona)
        try:
                        
            if 'repeticiones_suspendidas' in data_in:
                if previus.repeticiones_suspendidas != data_in['repeticiones_suspendidas']  and data_in['repeticiones_suspendidas']==True:
                    print('SUSPENDIDA DE FALSO A VERDADERO')
                    alerta_programada=AlertasProgramadas.objects.filter(id_alerta_programada=instance.id_alerta_generada.id_alerta_programada_origen).first()
                    if not alerta_programada:
                        raise NotFound('No existe alerta programada')
                    
                    if alerta_programada.agno_cumplimiento:
                        
                        if instance.responsable_directo:

                            if alerta_programada.perfil_sistema_implicado:
                                print("PERFIL DEL SISTEMA")
                                print(alerta_programada.perfil_sistema_implicado)
                                alerta_programada.perfil_sistema_implicado=None
                               
                            elif alerta_programada.id_und_org_lider_implicada:
                                print('lider de unidad')
                                print(alerta_programada.id_und_org_lider_implicada)    
                                alerta_programada.id_und_org_lider_implicada=None
                            elif alerta_programada.id_persona_implicada:
                                print('persona')
                                print(alerta_programada.id_persona_implicada)
                                alerta_programada.id_persona_implicada=None
                            alerta_programada.tiene_implicado=False
                            alerta_programada.save()
                        else:
                            lista_personas_directas=(alerta_programada.id_personas_alertar.rstrip("|")).split('|')
                            perfiles_alertar=(alerta_programada.id_perfiles_sistema_alertar.rstrip("|")).split('|')
                            lista_lideres_unidad=(alerta_programada.id_und_org_lider_alertar.rstrip("|")).split('|')

                            nueva_cadena_persona_directa, elemento_eliminado = self.eliminar_elemento_en_arreglo(lista_personas_directas, id_persona)
                            
                            #print("NUEVA CADENA DE PERSONAS")
                            #print(lista_personas_directas)
                            #print(nueva_cadena_persona_directa)
                            alerta_programada.id_personas_alertar=nueva_cadena_persona_directa

                            #Busca si la id esta asociada a un perfil profesional
                            perfil_pro=self.buscar_codigo_por_id(id_persona)
                            #print(perfil_pro)
                            if perfil_pro:
                                nueva_cadena_perfiles_directa, elemento_eliminado = self.eliminar_elemento_en_arreglo(perfiles_alertar, perfil_pro)
                                #print("NUEVA CADENA DE PERFILES")
                                #print(nueva_cadena_perfiles_directa)
                                #print(perfiles_alertar)
                                alerta_programada.id_perfiles_sistema_alertar=nueva_cadena_perfiles_directa
                            #En caso de ser un lider de unidad
                            lideres_unidad_orga=LideresUnidadesOrg.objects.filter(id_persona=id_persona).first()
                            
                            if lideres_unidad_orga:
                                id_unidad_el=(lideres_unidad_orga.id_unidad_organizacional)
                                nueva_cadena_lideres, elemento_eliminado=self.eliminar_elemento_en_arreglo(lista_lideres_unidad, id_unidad_el)
                                #print("CADENA LIDERES DE UNIDAD")
                                #print(id_unidad_el)
                                #print(nueva_cadena_lideres)
                                alerta_programada.id_und_org_lider_alertar=nueva_cadena_lideres


                            alerta_programada.save()

                        #print("CONDICION CON AÑO")
                    else:#si es programada sin año asignado
                        id_persona_suspender=str(instance.id_bandeja_alerta_persona.id_persona.id_persona)
                        #print(alerta_programada.id_personas_suspen_alertar_sin_agno)
                        if alerta_programada.id_personas_suspen_alertar_sin_agno:
                            cadena=alerta_programada.id_personas_suspen_alertar_sin_agno.split('|')
                            for id in cadena:
                                if id==id_persona_suspender:
                                    raise ValidationError("Esta notificacion ya se encuentra suspendida")
                            cadena_en_base=str(alerta_programada.id_personas_suspen_alertar_sin_agno)
                            alerta_programada.id_personas_suspen_alertar_sin_agno=cadena_en_base+id_persona_suspender+"|"
                            alerta_programada.save()
                        else:
                            alerta_programada.id_personas_suspen_alertar_sin_agno=str(id_persona_suspender)+"|"
                            alerta_programada.save()

                        print(instance.id_bandeja_alerta_persona.id_persona.id_persona)
                        print(alerta_programada.id_personas_suspen_alertar_sin_agno)

                    fecha_suspencion= datetime.now()

                    data_in['fecha_suspencion_repeticion']=fecha_suspencion
            
            
            
            if 'leido' in data_in:
                if previus.leido==False and data_in['leido']:
                    data_in['fecha_leido']=datetime.now()

            if 'archivado' in data_in:
                if previus.archivado==False and data_in['archivado']:
                    data_in['fecha_archivado']=datetime.now()


            serializer = self.serializer_class(instance, data=data_in, partial=True)
            serializer.is_valid(raise_exception=True)
            instance=serializer.save()



            if 'leido' in data_in:
                if data_in['leido']:
                    #print((instance.id_bandeja_alerta_persona))
                    elementos_sin_leer=AlertasBandejaAlertaPersona.objects.filter(id_bandeja_alerta_persona=instance.id_bandeja_alerta_persona,leido=False)
                    
                    if not elementos_sin_leer:
                        #print('LA BANDEJA NO TIENE ELEMENTOS PENDIENTES POR LEER')
                        bandeja=instance.id_bandeja_alerta_persona
                        bandeja.pendientes_leer=False
                        bandeja.save()
                        #print(bandeja)



        except ValidationError as e:       
            raise ValidationError(e.detail)


        return Response({'success': True, 'detail': 'Se actualizó la configuración de clase de alerta correctamente.', 'data': serializer.data}, status=status.HTTP_200_OK)
