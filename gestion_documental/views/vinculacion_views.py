from rest_framework import generics,status
from rest_framework.response import Response
from conservacion.models.viveros_models import HistoricoResponsableVivero, Vivero
from gestion_documental.serializers.vinculacion_serializers import GetDesvinculacion_persona
from seguridad.models import ClasesTerceroPersona, HistoricoActivacion, HistoricoCargosUndOrgPersona, Personas, User
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
import copy

from seguridad.utils import Util

class Desvinculacion_persona(generics.UpdateAPIView):
    serializer_class = GetDesvinculacion_persona
    queryset = Personas.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self,request,id_persona):
        
        data = request.data
        usuario_logueado = request.user
        persona_logueaddo = request.user.persona
        persona = self.queryset.all().filter(id_persona = id_persona).first()
       
       #VALIDAR DE QUE EL USUARIO SUPER ADMINISTRADOR NO SE ELIMINE
        if persona:
            usuario = User.objects.filter(persona=id_persona,tipo_usuario='I').exclude(id_usuario=1).first()
            
            if not usuario:
                
                return Response({'succes':False,'detail':'La persona no cuenta con un usuario interno en el sistema.'},status=status.HTTP_403_FORBIDDEN)                        
            
            
            if not data['observaciones_desvinculacion']:
                return Response({'succes':False,'detail':'Se debe enviar una observación de desvinculación.'},status=status.HTTP_400_BAD_REQUEST)
            
            fecha_desvinculacion = datetime.now()
            
            if not persona.fecha_a_finalizar_cargo_actual or not persona.fecha_inicio_cargo_actual or not persona.fecha_asignacion_unidad:
                return Response({'succes':False,'detail':'La persona no se encuentra actualmente vinculada a la empresa'},status=status.HTTP_403_FORBIDDEN)                        
              
            if persona.fecha_a_finalizar_cargo_actual < fecha_desvinculacion:
                fecha_desvinculacion = persona.fecha_a_finalizar_cargo_actual
                fecha_desvinculacion.replace(hour=23, minute=59)
              
            if persona.fecha_inicio_cargo_actual < persona.fecha_asignacion_unidad:
                fecha_inicial = persona.fecha_asignacion_unidad
                
            else: 
                fecha_inicial = persona.fecha_inicio_cargo_actual

            #GENERAR EL HISTORICO

            HistoricoCargosUndOrgPersona.objects.create(
                fecha_desvinculacion = fecha_desvinculacion,
                observaciones_desvinculacion = data['observaciones_desvinculacion'],
                id_persona = persona,
                id_cargo = persona.id_cargo,
                id_unidad_organizacional = persona.id_unidad_organizacional_actual,
                fecha_inicial_historico = fecha_inicial,
                fecha_final_historico = fecha_desvinculacion
            )
             #DESOCUPAR LOS DATOS DE LA TABLA DESPUES DE DESACTIVAR EL USUARIO           
            persona.id_cargo = None
            persona.fecha_inicio_cargo_actual = None
            persona.fecha_a_finalizar_cargo_actual = None
            persona.observaciones_vinculacion_cargo_actual = None
            persona.id_unidad_organizacional_actual = None
            persona.fecha_asignacion_unidad = None
            persona.es_unidad_organizacional_actual = False
                        
            #EL PROCESO DE DESVINCULACION DESACTIVA AL USUARIO QUE ESTE ACTIVO Y SEA INTERNO
            
            if usuario:
                if usuario.is_active and usuario.tipo_usuario=='I':
                    usuario.is_active = False
                    
            #HISTORICO ACTIVACION
            
            HistoricoActivacion.objects.create(
                id_usuario_afectado = usuario,
                cod_operacion = 'I',
                fecha_operacion = fecha_desvinculacion,
                justificacion = "Inactivación automática por acción de desvinculación de la corporación desde el módulo de Vinculación de Colaboradores",
                usuario_operador = usuario_logueado                
            )            
            #HISTORICO TABLA VIVEROS SI LA PERSONA ES RESPONSABLE DE ALGUN VIVERO
            
            viveros = Vivero.objects.filter(id_viverista_actual=persona)
            
            dirip = Util.get_client_ip(request)
            
            for vivero in viveros:
                fecha_actual_viverista = vivero.fecha_inicio_viverista_actual
                
                vivero.id_viverista_actual = None
                vivero.fecha_inicio_viverista_actual=None     
                vivero.fecha_cierre_actual = datetime.now()
                vivero.en_funcionamiento = False 
                vivero.id_persona_cierra = usuario_logueado.persona
                vivero.justificacion_cierre = "Cierre por desvinculación del viverista"
            
                #GENERAR HISTORICO CUANDO SE RETIRA A UN RESPONSABLE DE VIVERO
                
                historico = HistoricoResponsableVivero.objects.filter(id_vivero=vivero.id_vivero, id_persona=vivero.id_viverista_actual).last()
                    
                consecutivo = 1
                
                if historico:
                    consecutivo = historico.consec_asignacion + 1         
                print(vivero.fecha_inicio_viverista_actual)
                HistoricoResponsableVivero.objects.create(
                    id_vivero = vivero,
                    id_persona = persona,
                    consec_asignacion = consecutivo,
                    fecha_inicio_periodo = fecha_actual_viverista,
                    fecha_fin_periodo = fecha_desvinculacion,
                    observaciones = "Retiro automático del Viverista por acción de desvinculación de la corporación desde el módulo de Vinculación de Colaboradores",
                    id_persona_cambia = persona_logueaddo,                
                )
                
                vivero.save()
                
                # AUDITORIA
                descripcion = {'nombre': vivero.nombre}
                auditoria_data = {
                    'id_usuario': usuario_logueado.id_usuario,
                    'id_modulo': 43,
                    'cod_permiso': 'CR',
                    'subsistema': 'CONS',
                    'dirip': dirip,
                    'descripcion': descripcion
                }
                Util.save_auditoria(auditoria_data)
    
                
            if persona:
                funcionarios = ClasesTerceroPersona.objects.filter(id_persona=persona,id_clase_tercero=2)
                

                valores_eliminados_detalles=[]
                for funcionario in funcionarios:
                    
                    nombre = funcionario.id_clase_tercero.nombre
                    descripcion_detalle = {'nombre':nombre}
                    valores_eliminados_detalles.append(descripcion_detalle)
                    funcionario.delete()
                
                descripcion = {"TipodeDocumentoID": persona.tipo_documento, "NumeroDocumentoID": persona.numero_documento}
                
                #AUDITORIA DEL SERVICIO DE ACTUALIZADO PARA DETALLES
                auditoria_data = {
                    "id_usuario" : usuario_logueado.id_usuario,
                    "id_modulo" : 1,
                    "cod_permiso": "AC",
                    "subsistema": 'SEGU',
                    "dirip": dirip,
                    "descripcion": descripcion,
                    "valores_eliminados_detalles":valores_eliminados_detalles
                }
                Util.save_auditoria_maestro_detalle(auditoria_data)    
        
            persona.save()
            usuario.save()
        
        return Response({'succes':True,'detail':'Se realiza la desvinculación.'},status=status.HTTP_200_OK)                        

        
        