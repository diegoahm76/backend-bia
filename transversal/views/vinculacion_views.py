from rest_framework import generics,status
from rest_framework.response import Response
from conservacion.models.viveros_models import HistoricoResponsableVivero, Vivero
from almacen.models.generics_models import Bodegas
from transversal.models.entidades_models import ConfiguracionEntidad
from transversal.serializers.vinculacion_serializers import BusquedaHistoricoCargoUndSerializer, GetDesvinculacion_persona, VinculacionColaboradorSerializer, ConsultaVinculacionColaboradorSerializer, UpdateVinculacionColaboradorSerializer
from seguridad.models import HistoricoActivacion, OperacionesSobreUsuario, User
from transversal.models.base_models import (
    ClasesTerceroPersona,
    Cargos,
    HistoricoCargosUndOrgPersona
)
from transversal.models.personas_models import Personas
from rest_framework.permissions import IsAuthenticated
from datetime import datetime, date, timedelta, timezone
import copy
from transversal.models import UnidadesOrganizacionales
from seguridad.utils import Util
from transversal.views.configuracionEntidades_views import UpdateConfiguracionEntidad

class VinculacionColaboradorView(generics.UpdateAPIView):
    serializer_class = VinculacionColaboradorSerializer
    queryset = Personas.objects.filter(tipo_persona='N')
    permission_classes = [IsAuthenticated]

    def put(self, request, id_persona):
        persona = self.queryset.all().filter(id_persona=id_persona).first()
        data = request.data

        id_cargo = data.get('id_cargo')
        id_unidad_organizacional_actual = data.get('id_unidad_organizacional_actual')
        fecha_a_finalizar_cargo_actual = data.get('fecha_a_finalizar_cargo_actual')

        if persona:
            previous_persona = copy.copy(persona)
            cargo_inst = Cargos.objects.filter(id_cargo=id_cargo).first()

            if not all([id_cargo, id_unidad_organizacional_actual, fecha_a_finalizar_cargo_actual]):
                return Response({'success': False, 'detail': 'Todos los campos son requeridos'}, status=status.HTTP_400_BAD_REQUEST)

            # VALIDACIÓN UNIDAD ORG PERTENECE A ORGANIGRAMA ACTUAL
            unidad_organizacional = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional=id_unidad_organizacional_actual).first()
            
            if not unidad_organizacional:
                return Response({'success': False, 'detail': 'La unidad organizacional no existe'}, status=status.HTTP_400_BAD_REQUEST)
            organigrama = unidad_organizacional.id_organigrama
            
            if not organigrama.actual:
                return Response({'success': False, 'detail': 'El organigrama al que pertenece la unidad organizacional no es actual'}, status=status.HTTP_400_BAD_REQUEST)
                
             # CAMBIAR UNIDAD ORGANIZACIONAL
            persona.id_unidad_organizacional_actual = unidad_organizacional

            # CAMBIAR DE CARGO
            if not cargo_inst:
                return Response({'success': False, 'detail': 'El cargo no existe'}, status=status.HTTP_400_BAD_REQUEST)
            
            # VALIDACIÓN CARGO ACTIVO
            if not cargo_inst.activo:
                return Response({'success': False, 'detail': 'El cargo seleccionado está inactivo'}, status=status.HTTP_400_BAD_REQUEST)
        
            persona.id_cargo = cargo_inst

            # VALIDACIÓN FECHA A FINALIZAR POSTERIOR A LA ACTUAL

            fecha_minima = (datetime.today() + timedelta(days=1)).date()
            fecha_finalizar_cargo = (datetime.strptime(fecha_a_finalizar_cargo_actual, '%Y-%m-%d')).date()

            if fecha_finalizar_cargo < fecha_minima:
                return Response({'success': False, 'detail':'La fecha de finalización debe ser posterior a la fecha actual, mínimo el día siguiente'}, status=status.HTTP_403_FORBIDDEN)

            else:
                persona.fecha_a_finalizar_cargo_actual = fecha_finalizar_cargo

            # GUARDAR CAMPOS ASIGNADOS
            persona.es_unidad_organizacional_actual = True
            persona.fecha_inicio_cargo_actual = datetime.now()
            persona.observaciones_vinculacion_cargo_actual = data.get('observaciones_vinculacion_cargo_actual')
            persona.fecha_asignacion_unidad = datetime.now()
            
            persona.save()
        
            # AUDITORÍA
            usuario = request.user.id_usuario
            direccion=Util.get_client_ip(request)
            descripcion = {"TipodeDocumentoID": str(persona.tipo_documento), "NumeroDocumentoID": str(persona.numero_documento)}
            valores_actualizados = {'current': persona, 'previous': previous_persona}

            auditoria_data = {
                "id_usuario" : usuario,
                "id_modulo" : 72,
                "cod_permiso": "AC",
                "subsistema": 'GEST',
                "dirip": direccion,
                "descripcion": descripcion, 
                "valores_actualizados": valores_actualizados
            }
            Util.save_auditoria(auditoria_data)

            return Response({'success': True, 'detail': 'La persona ha sido vinculada como colaborador y sus datos han sido actualizados'}, status=status.HTTP_200_OK)
        else:
            return Response({'success': False, 'detail': 'La persona no existe o es jurídica'},status=status.HTTP_404_NOT_FOUND)

class ConsultaVinculacionColaboradorView(generics.ListAPIView):
    serializer_class = ConsultaVinculacionColaboradorSerializer 
    permission_classes = [IsAuthenticated]

    def get(self, request, id_persona):
        consulta_personas = Personas.objects.filter(id_persona=id_persona, tipo_persona='N', id_cargo__isnull=False, id_unidad_organizacional_actual__isnull=False).first()

        if not consulta_personas:
            return Response({'success':False, 'detail': 'La persona no esta vinculada como colaborador o no existe'}, status=status.HTTP_404_NOT_FOUND)

        serializador = self.serializer_class(consulta_personas)
        data = serializador.data

        fecha_a_finalizar_cargo_actual = consulta_personas.fecha_a_finalizar_cargo_actual if consulta_personas.id_cargo else None
        fecha_vencida = True if fecha_a_finalizar_cargo_actual < datetime.now().date() else False
        data['fecha_vencida'] = fecha_vencida

        return Response({'success':True, 'detail': 'La persona existe y está vinculada como colaborador', 'data':data}, status=status.HTTP_200_OK)
    
class UpdateVinculacionColaboradorView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UpdateVinculacionColaboradorSerializer
    queryset = Personas.objects.all()
    permission_classes = [IsAuthenticated]

    def put(self, request, id_persona):

        persona = self.queryset.filter(id_persona=id_persona).first()
        print(persona)
        print(persona.tipo_persona)
        
        if persona.tipo_persona != 'N':
            return Response( {'sucess': False, 'detail':'La persona que va a actualizar debe ser natural'},status=status.HTTP_403_FORBIDDEN)
        
        if persona.id_cargo is None or persona.id_unidad_organizacional_actual is None:
            return Response({'sucess': False, 'detail': 'La persona no se encuentra vinculada'}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        cargo = data.get('id_cargo')
        fecha_finalizar_cargo = data.get('fecha_a_finalizar_cargo_actual')
        unidad = data.get('id_unidad_organizacional_actual')
        observacion = data.get('observaciones_vinculacion_cargo_actual')
        justificacion = data.get('justificacion_cambio_und_org')
        fecha_actual = datetime.today()

        if persona:

            cargo_inst_current = Cargos.objects.filter(id_cargo=cargo).first()
            cargo_inst = persona.id_cargo
            unidad_inst = persona.id_unidad_organizacional_actual
            observacion_old = persona.observaciones_vinculacion_cargo_actual
            unidad_inst_current = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional=unidad).first()
            previous_persona = copy.copy(persona) 

            if not fecha_finalizar_cargo:
                return Response( {'success':False, 'detail':'Debe enviar la fecha de finalización'}, status=status.HTTP_403_FORBIDDEN)

            fecha_finalizar_cargo = datetime.strptime(fecha_finalizar_cargo, '%Y-%m-%d').date()

            if cargo == persona.id_cargo.id_cargo and unidad == persona.id_unidad_organizacional_actual.id_unidad_organizacional and fecha_finalizar_cargo == persona.fecha_a_finalizar_cargo_actual:
                return Response({'success': False, 'detail': 'No se ha realizado ninguna actualización'}, status=status.HTTP_403_FORBIDDEN)

            fecha_inicio_cargo = persona.fecha_inicio_cargo_actual
            fecha_asignacion_unidad = persona.fecha_asignacion_unidad

            if persona.fecha_a_finalizar_cargo_actual > fecha_actual.date():
                if unidad != persona.id_unidad_organizacional_actual.id_unidad_organizacional or cargo != persona.id_cargo.id_cargo:
                    if fecha_finalizar_cargo != persona.fecha_a_finalizar_cargo_actual:
                        fecha_minima = (datetime.today() + timedelta(days=1)).date()
                        if fecha_finalizar_cargo < fecha_minima:
                            return Response({'success': False, 'detail':'La fecha de finalización debe ser posterior a la fecha actual, mínimo el día siguiente'}, status=status.HTTP_403_FORBIDDEN)
                        else:
                            persona.fecha_a_finalizar_cargo_actual = fecha_finalizar_cargo
                        
                    if cargo and cargo != persona.id_cargo.id_cargo:
                        persona.id_cargo = cargo_inst_current
                        persona.fecha_inicio_cargo_actual = fecha_actual

                        if not fecha_finalizar_cargo or fecha_actual.date() > fecha_finalizar_cargo:
                            return Response({'success': False, 'detail':'Se debe enviar la fecha de finalización del cargo y tiene que ser mayor a la de inicio del cargo'}, status=status.HTTP_403_FORBIDDEN)
                        
                        if not observacion or observacion == '':
                            return Response({'success': False, 'detail':'Se debe ingresar una observación'}, status=status.HTTP_403_FORBIDDEN)
                        else:
                            persona.observaciones_vinculacion_cargo_actual = observacion

                    if unidad != persona.id_unidad_organizacional_actual.id_unidad_organizacional:
                        persona.id_unidad_organizacional_actual = unidad_inst_current
                        persona.fecha_asignacion_unidad = fecha_actual
        
                        if not justificacion or justificacion == '':
                            return Response({'success': False, 'detail':'Se debe ingresar una justificación'}, status=status.HTTP_403_FORBIDDEN)

                    if fecha_inicio_cargo < fecha_asignacion_unidad:
                        fecha_final = fecha_asignacion_unidad
                    else:
                        fecha_final=fecha_inicio_cargo
                    
                    HistoricoCargosUndOrgPersona.objects.create(
                        id_persona = persona,
                        id_unidad_organizacional = unidad_inst,
                        id_cargo = cargo_inst,
                        fecha_inicial_historico = fecha_final,
                        fecha_final_historico = fecha_actual,
                        justificacion_cambio_und_org = justificacion if unidad != unidad_inst.id_unidad_organizacional else None,
                        observaciones_vinculni_cargo = observacion_old if fecha_inicio_cargo >= fecha_asignacion_unidad else None,
                        desvinculado = False,
                    )
                
            else:
                if fecha_finalizar_cargo != persona.fecha_a_finalizar_cargo_actual:
                    fecha_minima = (datetime.today() + timedelta(days=1)).date()
                    if fecha_finalizar_cargo < fecha_minima:
                        return Response({'success': False, 'detail':'La fecha de finalización debe ser posterior a la fecha actual, mínimo el día siguiente'}, status=status.HTTP_403_FORBIDDEN)
                    else:
                        persona.fecha_a_finalizar_cargo_actual = fecha_finalizar_cargo
                else:
                    return Response({'success':False,'detail':'La fecha a finalizar está vencida, por lo tanto debe extender la fecha de finalización o desvincular a la persona'},status=status.HTTP_403_FORBIDDEN)
         
            persona.save()

            #AUDITORÍA
            usuario = request.user.id_usuario
            direccion=Util.get_client_ip(request)
            descripcion = {"TipodeDocumentoID": str(persona.tipo_documento), "NumeroDocumentoID": str(persona.numero_documento) }
            valores_actualizados = {'current': persona, 'previous': previous_persona}

            auditoria_data = {
                "id_usuario" : usuario,
                "id_modulo" : 72,
                "cod_permiso": "AC",
                "subsistema": 'GEST',
                "dirip": direccion,
                "descripcion": descripcion, 
                "valores_actualizados": valores_actualizados
            }
            Util.save_auditoria(auditoria_data)
        else:
            return Response({'success':False,'detail':'La persona no existe'}, status=status.HTTP_403_FORBIDDEN)
       
        return Response({'success':True,'detail':'Actualización exitosa'}, status=status.HTTP_200_OK)


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
            print(persona.id_persona)
            usuario = User.objects.filter(persona=id_persona,tipo_usuario='I').exclude(id_usuario=1).first()
            
            if not data['observaciones_desvinculacion']:
                return Response({'succes':False,'detail':'Se debe enviar una observación de desvinculación.'},status=status.HTTP_400_BAD_REQUEST)
            
            fecha_desvinculacion = datetime.now()
            
            if not persona.fecha_a_finalizar_cargo_actual or not persona.fecha_inicio_cargo_actual or not persona.fecha_asignacion_unidad:
                return Response({'succes':False,'detail':'La persona no se encuentra actualmente vinculada a la empresa'},status=status.HTTP_403_FORBIDDEN)                        
              
            if persona.fecha_a_finalizar_cargo_actual < fecha_desvinculacion.date():
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
                observaciones_vinculni_cargo = persona.observaciones_vinculacion_cargo_actual,
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
                cod_operacion_instance = OperacionesSobreUsuario.objects.filter(cod_operacion='I').first()
                
                HistoricoActivacion.objects.create(
                    id_usuario_afectado = usuario,
                    cod_operacion = cod_operacion_instance,
                    fecha_operacion = fecha_desvinculacion,
                    justificacion = "Inactivación automática por acción de desvinculación de la corporación desde el módulo de Vinculación de Colaboradores",
                    usuario_operador = usuario_logueado                
                )
                
                usuario.save()
                
            #HISTORICO TABLA VIVEROS SI LA PERSONA ES RESPONSABLE DE ALGUN VIVERO
            
            viveros = Vivero.objects.filter(id_viverista_actual=persona)
            
            dirip = Util.get_client_ip(request)
            
            # for vivero in viveros:
            #     fecha_actual_viverista = vivero.fecha_inicio_viverista_actual
                
            #     vivero.id_viverista_actual = None
            #     vivero.fecha_inicio_viverista_actual=None     
            #     vivero.fecha_cierre_actual = datetime.now()
            #     vivero.en_funcionamiento = False 
            #     vivero.id_persona_cierra = usuario_logueado.persona
            #     vivero.justificacion_cierre = "Cierre por desvinculación del viverista"
            
                #GENERAR HISTORICO CUANDO SE RETIRA A UN RESPONSABLE DE VIVERO
                
                # historico = HistoricoResponsableVivero.objects.filter(id_vivero=vivero.id_vivero, id_persona=vivero.id_viverista_actual).last()
                    
                # consecutivo = 1
                
                # if historico:
                #     consecutivo = historico.consec_asignacion + 1         
                # print(vivero.fecha_inicio_viverista_actual)
                # HistoricoResponsableVivero.objects.create(
                #     id_vivero = vivero,
                #     id_persona = persona,
                #     consec_asignacion = consecutivo,
                #     fecha_inicio_periodo = fecha_actual_viverista,
                #     fecha_fin_periodo = fecha_desvinculacion,
                #     observaciones = "Retiro automático del Viverista por acción de desvinculación de la corporación desde el módulo de Vinculación de Colaboradores",
                #     id_persona_cambia = persona_logueaddo,                
                # )
                
                # vivero.save()
                
                # # AUDITORIA
                # descripcion = {'nombre': vivero.nombre}
                # auditoria_data = {
                #     'id_usuario': usuario_logueado.id_usuario,
                #     'id_modulo': 43,
                #     'cod_permiso': 'CR',
                #     'subsistema': 'CONS',
                #     'dirip': dirip,
                #     'descripcion': descripcion
                # }
                # Util.save_auditoria(auditoria_data)
    
            #SI LA PERSONA ES RESPONSABLE DE ALGUNA BODEGA

            bodegas = Bodegas.objects.filter(id_responsable=persona)

            for bodega in bodegas:
                bodega.id_responsable = None
                bodega.save()

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


            #SI LA PERSONA SE ENCUENTRA EN LA CONFIGURACION DE LA ENTIDAD
            fecha_hora_actual =datetime.now()
            actualizar_configuracion=UpdateConfiguracionEntidad()

            perfiles_actuales=ConfiguracionEntidad.objects.first()
            

            if perfiles_actuales.id_persona_director_actual and perfiles_actuales.id_persona_director_actual.id_persona == persona.id_persona:
                  
                  fecha_inicio=perfiles_actuales.fecha_inicio_dir_actual
                  perfiles_actuales.id_persona_director_actual = None
                  perfiles_actuales.fecha_inicio_dir_actual = None 
                  perfiles_actuales.save()
                  actualizar_configuracion.registrarHistoricoPerfilesEntidad('Dire',1,persona,fecha_inicio,"Desvinculacion laboral",usuario_logueado.id_usuario)

            if perfiles_actuales.id_persona_coord_almacen_actual and perfiles_actuales.id_persona_coord_almacen_actual.id_persona == persona.id_persona:
                
                fecha_inicio = perfiles_actuales.fecha_inicio_coord_alm_actual
                perfiles_actuales.id_persona_coord_almacen_actual = None
                perfiles_actuales.fecha_inicio_coord_alm_actual = None 
                perfiles_actuales.save()
                actualizar_configuracion.registrarHistoricoPerfilesEntidad('CAlm', 1, persona, fecha_inicio, "Desvinculación laboral", usuario_logueado.id_usuario)

            if perfiles_actuales.id_persona_respon_transporte_actual and perfiles_actuales.id_persona_respon_transporte_actual.id_persona == persona.id_persona:
            
                fecha_inicio = perfiles_actuales.fecha_inicio_respon_trans_actual
                perfiles_actuales.id_persona_respon_transporte_actual = None
                perfiles_actuales.fecha_inicio_respon_trans_actual = None 
                perfiles_actuales.save()
                actualizar_configuracion.registrarHistoricoPerfilesEntidad('RTra', 1, persona, fecha_inicio, "Desvinculación laboral", usuario_logueado.id_usuario)

            if perfiles_actuales.id_persona_coord_viveros_actual and perfiles_actuales.id_persona_coord_viveros_actual.id_persona == persona.id_persona:
             
                fecha_inicio = perfiles_actuales.fecha_inicio_coord_viv_actual
                perfiles_actuales.id_persona_coord_viveros_actual = None
                perfiles_actuales.fecha_inicio_coord_viv_actual = None 
                perfiles_actuales.save()
                actualizar_configuracion.registrarHistoricoPerfilesEntidad('CViv', 1, persona, fecha_inicio, "Desvinculación laboral", usuario_logueado.id_usuario)
            
            if perfiles_actuales.id_persona_almacenista and perfiles_actuales.id_persona_almacenista.id_persona == persona.id_persona:
             
                fecha_inicio = perfiles_actuales.fecha_inicio_almacenista
                perfiles_actuales.id_persona_almacenista = None
                perfiles_actuales.fecha_inicio_almacenista = None 
                perfiles_actuales.save()
                actualizar_configuracion.registrarHistoricoPerfilesEntidad('Alma', 1, persona, fecha_inicio, "Desvinculación laboral", usuario_logueado.id_usuario)


                        
                    
        return Response({'succes':True,'detail':'Se realiza la desvinculación.'},status=status.HTTP_200_OK)
    
class BusquedaHistoricoCargoUnd(generics.ListAPIView):
    serializer_class = BusquedaHistoricoCargoUndSerializer
    queryset = HistoricoCargosUndOrgPersona.objects.all()
    permission_classes = [IsAuthenticated]

    def get(self, request, id_persona):
        try:
            persona = HistoricoCargosUndOrgPersona.objects.filter(id_persona=id_persona).first()
            if not persona:
                return Response({'success':False, 'detail': 'La persona elegida no tiene ningún historico asociado'}, status=status.HTTP_404_NOT_FOUND)
        except HistoricoCargosUndOrgPersona.DoesNotExist:
            return Response({'success':False, 'detail': 'La persona elegida no tiene ningún historico asociado'}, status=status.HTTP_404_NOT_FOUND)

        historicos = HistoricoCargosUndOrgPersona.objects.filter(id_persona=id_persona)
        cargos = Cargos.objects.all()
        unidades_organizacionales = UnidadesOrganizacionales.objects.all()
        data = []
        for historico in historicos:
            cargo = cargos.filter(id_cargo=historico.id_cargo.id_cargo).first()
            unidad_organizacional = unidades_organizacionales.filter(id_unidad_organizacional=historico.id_unidad_organizacional.id_unidad_organizacional).first()
            data.append({
                'id_cargo': historico.id_cargo.id_cargo,
                'nombre_cargo': cargo.nombre if cargo else None,
                'id_unidad_organizacional': historico.id_unidad_organizacional.id_unidad_organizacional,
                'nombre_unidad_organizacional': unidad_organizacional.nombre if unidad_organizacional else None,
                'fecha_inicial_historico': historico.fecha_inicial_historico,
                'fecha_final_historico': historico.fecha_final_historico,
                'observaciones_vinculni_cargo': historico.observaciones_vinculni_cargo,
                'justificacion_cambio_und_org': historico.justificacion_cambio_und_org,
                'desvinculado': historico.desvinculado,
                'fecha_desvinculacion' : historico.fecha_desvinculacion,
                'observaciones_desvinculacion' : historico.observaciones_desvinculacion
            })
        serializador = self.serializer_class(historicos,many=True)
        return Response({'success':True, 'detail': 'La persona elegida tiene los siguientes historicos asociados', 'data':serializador.data}, status=status.HTTP_200_OK)
