from datetime import date
from django.db.models import Q
from django.forms import ValidationError
from django.forms.models import model_to_dict
from recurso_hidrico.models.programas_models import ProyectosPORH
from recurso_hidrico.serializers.programas_serializers import GenerardorMensajeProyectosPORHGetSerializer
from transversal.models.alertas_models import AlertasProgramadas, BandejaAlertaPersona
from transversal.models.entidades_models import ConfiguracionEntidad
from transversal.models.lideres_models import LideresUnidadesOrg
from transversal.serializers.alertas_serializers import AlertasBandejaAlertaPersonaPostSerializer, AlertasGeneradasPostSerializer
from datetime import datetime, timedelta

def separar_cadena(cadena):

    arreglo = []

    for elemento in cadena.split('|'):
        try:
            # Intenta convertir el elemento a un entero
            #valor = int(elemento)

            if elemento!='':
                arreglo.append(elemento)
        except ValueError:
            # Si no se puede convertir a entero, simplemente ignora este elemento
            pass

    return(arreglo)



def alerta_proyectos_vigentes_porh():
        mensaje=""
        hoy = date.today()
        proyectos_vigentes = ProyectosPORH.objects.filter(Q(vigencia_inicial__lte=hoy) & Q(vigencia_final__gte=hoy))
        serializador = GenerardorMensajeProyectosPORHGetSerializer(proyectos_vigentes, many=True)
        for dato in serializador.data:
            mensaje+="Proyecto "+str(dato['id_proyecto'])+" ("+str(dato['nombre'])+")"+" del Programa "+str(dato['id_programa'])+" ("+str(dato['nombre_programa'])+")"+"  del Plan de Ordenamiento de Recurso Hídrico "+str(dato['id_porh'])+" ("+str(dato['nombre_porh'])+")"+".\n"

        return(mensaje)



#@background(schedule=None) 
def generar_alerta_segundo_plano():
    # Coloca aquí el código de la tarea que deseas ejecutar en segundo plano
    print("Tarea en segundo plano ejecutada.")
    cadena=""
    id_responsable=None
    hoy = date.today()
    fecha_actual = datetime.now().date()
    numero_dia = hoy.day
    numero_mes = hoy.month
    numero_agno = hoy.year

    alertas_generadas=AlertasProgramadas.objects.all()
   
    #Alerta en Fecha Fija - Programadas con o sin Repeticiones anteriores o posteriores  (con y sin año).
    
    for programada in alertas_generadas:
            
            agno_alerta=numero_agno

            if   programada.agno_cumplimiento:
                agno_alerta=programada.agno_cumplimiento

            if  programada.activa :
                dias_pre=programada.ctdad_dias_alertas_previas

                frecuencia_pre=programada.frecuencia_alertas_previas
                
                cantidad_repeticiones_post=programada.ctdad_repeticiones_post
                
                frecuencia_dias_post=programada.frecuencia_repeticiones_post

                dias_posteriores=cantidad_repeticiones_post*frecuencia_dias_post
                fecha_alerta_base = date(agno_alerta, programada.mes_cumplimiento,programada.dia_cumplimiento)
                fecha_lim_inferior = fecha_alerta_base - timedelta(days=dias_pre)
                fecha_lim_superior = fecha_alerta_base + timedelta(days=dias_posteriores)
                print("LIMINTE INFERIOR: "+str(fecha_lim_inferior))
                print("LIMINTE SUPERIOR: "+str(fecha_lim_superior))
                print("FECHA BASE: "+str(fecha_alerta_base))
                print("FRECUENCIA INFERIOR: "+str(frecuencia_pre))
                print("FRECUENCIA SUPERIORES: "+str(frecuencia_dias_post))
                
                if fecha_actual >= fecha_lim_inferior and fecha_actual <= fecha_lim_superior:
                    print("BIEN ESTA DENTRO DEL RANGO")
                    #ALERTAS PRE
                    fecha_frecuencia=fecha_lim_inferior
                    if frecuencia_pre !=0 and frecuencia_pre > 0:
                        while (fecha_frecuencia < fecha_alerta_base):
                            print("GENERA ALERTAS PRE:"+str(fecha_frecuencia))
                            if fecha_frecuencia==fecha_actual:
                                  programar_alerta(programada,"ANTES")
                                  print("LA ALERTA SE GENERO ANTES DE LA FECHA: "+ str(fecha_frecuencia))

                            fecha_frecuencia= fecha_frecuencia + timedelta(days=frecuencia_pre)
                        
                    if  fecha_alerta_base==fecha_actual:
                         programar_alerta(programada,"AHORA")
                         print("ES HOY LA ALERTA BASE")
                         return 0

                    #ALERTAS POST
                    
                    if frecuencia_dias_post!=0 and cantidad_repeticiones_post!=0:
                        fecha_frecuencia=fecha_alerta_base +timedelta(days=frecuencia_dias_post)
                        for _ in range(cantidad_repeticiones_post):
                             #print("ALERTAS GENERADAS DESPUES: "+str(fecha_frecuencia))

                             if fecha_frecuencia==fecha_actual:
                                  print("LA ALERTA SE GENERO DESPUES DE LA FECHA: "+ str(fecha_frecuencia))
                                  programar_alerta(programada,"DESPUES")
                             fecha_frecuencia +=  timedelta(days=frecuencia_dias_post)
                            
                    
                    

                    print("##############################")
                    

def programar_alerta(programada,clasificacion):
        perfiles_actuales=ConfiguracionEntidad.objects.first()
        nombre_funcion = programada.nombre_funcion_comple_mensaje
        funcion = globals().get(nombre_funcion)
        cadena=""
        print(clasificacion)
        id_responsable=None
        if funcion:
            cadena=funcion()
            #print(cadena)
        else:
            print("La función no fue encontrada.")

        data_alerga_generada={}
        data_alerga_generada['nombre_clase_alerta']=programada.nombre_clase_alerta
        #PENDIENTE COMPLEMENTO DE MENSAJES
        data_alerga_generada['mensaje']=programada.mensaje_base_del_dia+"\n"+cadena#VALIDAR CAMPO <1000
        #FIN
        data_alerga_generada['cod_categoria_alerta']=programada.cod_categoria_alerta
        data_alerga_generada['nivel_prioridad']=programada.nivel_prioridad
        data_alerga_generada['id_modulo_destino']=programada.id_modulo_destino.id_modulo
        data_alerga_generada['id_modulo_generador']=programada.id_modulo_generador.id_modulo
        data_alerga_generada['id_elemento_implicado']=programada.id_elemento_implicado
        data_alerga_generada['id_alerta_programada_origen']=programada.id_alerta_programada
        data_alerga_generada['envio_email']=programada.requiere_envio_email
        #PENDIENTE LEER ENTREGA 38

        data_alerga_generada['es_ultima_repeticion']=True
        serializer_alerta_generada=AlertasGeneradasPostSerializer(data=data_alerga_generada)
        instace=None

        try:
            serializer_alerta_generada.is_valid(raise_exception=True)
            instance_alerta_generada=serializer_alerta_generada.save()

        except ValidationError  as e:
            error_message = {'error': e.detail}
            print(len(data_alerga_generada['mensaje']))
            raise ValidationError  (e.detail)


        #En el caso de tener personal implicado ,este puede ser una persona,un perfil profesional o un lider de unidad organizacional implicado
        id_implicado=''
        if programada.tiene_implicado:
            if programada.id_persona_implicada:
                id_responsable=programada.id_persona_implicada.id_persona
            if programada.perfil_sistema_implicado:

                if programada.perfil_sistema_implicado == 'Dire':
                    if perfiles_actuales.id_persona_director_actual:
                        id_responsable=(perfiles_actuales.id_persona_director_actual.id_persona)
                elif programada.perfil_sistema_implicado == 'CAlm':
                    if perfiles_actuales.id_persona_coord_almacen_actual:
                        id_responsable=(perfiles_actuales.id_persona_coord_almacen_actual.id_persona)
                elif programada.perfil_sistema_implicado == 'RTra':
                    if perfiles_actuales.id_persona_respon_transporte_actual:
                        id_responsable=(perfiles_actuales.id_persona_respon_transporte_actual.id_persona)
                elif programada.perfil_sistema_implicado == 'CViv':
                    if perfiles_actuales.id_persona_coord_viveros_actual:
                        id_responsable=(perfiles_actuales.id_persona_coord_viveros_actual.id_persona)
                elif programada.perfil_sistema_implicado == 'Alma':
                    if perfiles_actuales.id_persona_almacenista:
                        id_responsable=(perfiles_actuales.id_persona_almacenista.id_persona)
                #print(id_responsable)
            if programada.id_und_org_lider_implicada:
                print("LIDER DE UNIDAD")
                lideres_unidad_orga=LideresUnidadesOrg.objects.filter(id_unidad_organizacional=programada.id_und_org_lider_implicada).first()
                id_responsable=lideres_unidad_orga.id_persona.id_persona
                print(id_responsable)


        #Se optienen las personas a alertar
        str_personas_alertar=programada.id_personas_alertar
        str_perfiles_alertar=programada.id_perfiles_sistema_alertar
        str_lideres_unidades_alertar=programada.id_und_org_lider_alertar
        #para los perfiles del sistema se requiere buscar las ids de las personas responsables actualmente en ese cargo 

        personas_alertar=separar_cadena(str_personas_alertar)
        perfiles_alertar=separar_cadena(str_perfiles_alertar)
        ids_perfiles_alertar=[]
        for perfil in perfiles_alertar:

            if perfil == 'Dire':
                if perfiles_actuales.id_persona_director_actual:
                    ids_perfiles_alertar.append(perfiles_actuales.id_persona_director_actual.id_persona)
            elif perfil == 'CAlm':
                if perfiles_actuales.id_persona_coord_almacen_actual:
                    ids_perfiles_alertar.append(perfiles_actuales.id_persona_coord_almacen_actual.id_persona)
            elif perfil == 'RTra':
                if perfiles_actuales.id_persona_respon_transporte_actual:
                    ids_perfiles_alertar.append(perfiles_actuales.id_persona_respon_transporte_actual.id_persona)
            elif perfil == 'CViv':
                if perfiles_actuales.id_persona_coord_viveros_actual:
                    ids_perfiles_alertar.append(perfiles_actuales.id_persona_coord_viveros_actual.id_persona)
            elif perfil == 'Alma':
                if perfiles_actuales.id_persona_almacenista:
                    ids_perfiles_alertar.append(perfiles_actuales.id_persona_almacenista.id_persona)


        lideres_unidades_alertar=separar_cadena(str_lideres_unidades_alertar)
        ids_lideres_unidades_alertar_alertar=[]

        #se requiere las ids de las personas asignadas como lideres de unidades organizacionales actuales
        for lider in lideres_unidades_alertar:
            lideres_unidad_orga=LideresUnidadesOrg.objects.filter(id_unidad_organizacional=lider)
            for lider in lideres_unidad_orga:
                ids_lideres_unidades_alertar_alertar.append(lider.id_persona.id_persona)
            #pentiente por verificar
        #Pendiente validacion con T043idPersonasSuspendEnAlerSinAgno 
        #Pendiente T010emailNotificacion 
        destinatarios=[]

        destinatarios.extend(ids_lideres_unidades_alertar_alertar)
        destinatarios.extend(ids_perfiles_alertar)
        destinatarios.extend(personas_alertar)
        if id_responsable:
            destinatarios.append(str(id_responsable))


        elementos_unicos = {}
        # ELEMENTOS REPETIDOS
        for elemento in destinatarios:
            clave = str(elemento)
            elementos_unicos[clave] = elemento

        # Obtener los elementos únicos del diccionario como una lista
        arreglo_sin_repetidos = list(elementos_unicos.values())


        for destino in arreglo_sin_repetidos:
            if not destino:
                raise ValidationError("NULOO")
            print(destinatarios)
            bandejas_notificaciones=BandejaAlertaPersona.objects.filter(id_persona=destino).first()
            if bandejas_notificaciones:
            #print(bandejas_notificaciones.id_persona.id_persona)
                alerta_bandeja={}
                alerta_bandeja['leido']=False
                alerta_bandeja['archivado']=False
                #alerta_bandeja['fecha_archivado']=False
                alerta_bandeja['email_usado']='correo@conhora.com'
                if id_responsable and  destino == str(id_responsable):
                    alerta_bandeja['responsable_directo']=True
                else:
                    alerta_bandeja['responsable_directo']=False
                alerta_bandeja['id_alerta_generada']=instance_alerta_generada.id_alerta_generada
                alerta_bandeja['id_bandeja_alerta_persona']=bandejas_notificaciones.id_bandeja_alerta
                #correo
                print(alerta_bandeja)
                
                serializer_alerta_bandeja=AlertasBandejaAlertaPersonaPostSerializer(data=alerta_bandeja)
                bandejas_notificaciones.pendientes_leer=True
                bandejas_notificaciones.save()
                serializer_alerta_bandeja.is_valid(raise_exception=True)
            else:
                print("###DESTINATARIO")
                print(destino)
            instance_alerta_bandeja=serializer_alerta_bandeja.save()
        #     #DATOS SUFICIENTES PARA ENTREGA 35 PENDIENTE FINALIZAR

                