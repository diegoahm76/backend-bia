from datetime import date
from django.db.models import Q
from django.forms import ValidationError
from django.forms.models import model_to_dict
from almacen.models.hoja_de_vida_models import DocumentosVehiculo, HojaDeVidaVehiculos
from almacen.models.mantenimientos_models import ProgramacionMantenimientos
from gestion_documental.choices.cod_estado_eliminacion_choices import COD_ESTADO_ELIMINACION_CHOICES
from gestion_documental.models.expedientes_models import EliminacionDocumental
from gestion_documental.models.radicados_models import PQRSDF, ConfigTiposRadicadoAgno
from recurso_hidrico.models.programas_models import ProyectosPORH
from recurso_hidrico.serializers.programas_serializers import GenerardorMensajeProyectosPORHGetSerializer
from seguridad.utils import Util
from transversal.models.alertas_models import AlertasProgramadas, BandejaAlertaPersona
from transversal.models.entidades_models import ConfiguracionEntidad
from transversal.models.lideres_models import LideresUnidadesOrg
from transversal.serializers.alertas_serializers import AlertasBandejaAlertaPersonaPostSerializer, AlertasGeneradasPostSerializer
from datetime import datetime, timedelta
from django.template.loader import render_to_string
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
        mensaje="<ul>"
        hoy = date.today()
        proyectos_vigentes = ProyectosPORH.objects.filter(Q(vigencia_inicial__lte=hoy) & Q(vigencia_final__gte=hoy))
        serializador = GenerardorMensajeProyectosPORHGetSerializer(proyectos_vigentes, many=True)
        for dato in serializador.data:
            mensaje+="<li>Proyecto "+str(dato['id_proyecto'])+" ("+str(dato['nombre'])+")"+" del Programa "+str(dato['id_programa'])+" ("+str(dato['nombre_programa'])+")"+"  del Plan de Ordenamiento de Recurso Hídrico "+str(dato['id_porh'])+" ("+str(dato['nombre_porh'])+")"+".</li>"
        mensaje+="</ul>"
        return(mensaje)
def complemento_mensaje_Gest_TRPqr(id_elemento):
    fecha_actual = datetime.now()
    pqrsdf = PQRSDF.objects.filter(id_PQRSDF=id_elemento).first()
    radicado = ""

    if not pqrsdf:

        return ""

    if pqrsdf.id_radicado:
        instance_config_tipo_radicado = ConfigTiposRadicadoAgno.objects.filter(agno_radicado=pqrsdf.id_radicado.agno_radicado,cod_tipo_radicado=pqrsdf.id_radicado.cod_tipo_radicado).first()
        numero_con_ceros = str(pqrsdf.id_radicado.nro_radicado).zfill(instance_config_tipo_radicado.cantidad_digitos)
        radicado= instance_config_tipo_radicado.prefijo_consecutivo+'-'+str(instance_config_tipo_radicado.agno_radicado)+'-'+numero_con_ceros

    fecha_radicado = pqrsdf.fecha_radicado
    fecha_respuesta = fecha_actual + timedelta(days=pqrsdf.dias_para_respuesta)
    fecha_diferencia = fecha_respuesta - fecha_actual
    dias_respuesta = fecha_diferencia.days

    texto_html = f"Radicado: {radicado}<br>Fecha de radicado: {fecha_radicado}<br>Días para responder: {dias_respuesta}"
    return texto_html

def complemento_mensaje_Ges_EliDoc(id_elemento):
    mensaje = ""
    eliminacion = EliminacionDocumental.objects.filter(id_eliminacion_documental=id_elemento).first()
    cod_estado = eliminacion.estado
    nombre_estado =""
    if not eliminacion:
        return ""
    for  x in COD_ESTADO_ELIMINACION_CHOICES:
        if cod_estado== x[0]:
            nombre_estado = x[1]
    fecha = eliminacion.fecha_publicacion
    fecha_actual = datetime.now()
    fecha_respuesta = fecha_actual + timedelta(days=eliminacion.dias_publicacion)
    fecha_dias_respuesta = fecha_respuesta - fecha_actual
    entero_dias = fecha_dias_respuesta.days
    texto_html= f"Estado: {nombre_estado} <br> Fecha publicacion: {fecha} <br>Dias Respuesta: {entero_dias}"
    return texto_html

def complemento_mensaje_Alm_VeDocV(id_elemento):
    id_documento = id_elemento #
    documento = DocumentosVehiculo.objects.filter(id_documentos_vehiculos=id_documento).first()

    if not documento:
        return ""
    
    vehiculo = documento.id_articulo

    mensaje = "<ul>"
   
    
    mensaje += f"<li><b>Nombre del Vehículo: </b>{vehiculo.nombre}</li>"
    mensaje += f"<li><b>Marca: </b>{vehiculo.id_marca.nombre}</li>"
    mensaje += f"<li><b>Placa: </b>{vehiculo.doc_identificador_nro}</li>"
    mensaje += f"<li><b>Tipo de documento: </b>{documento.get_cod_tipo_documento_display()}</li>"
    mensaje += f"<li><b>Numero del documento: </b>{documento.nro_documento}</li>"
    mensaje += f"<li><b>Fecha inicio de vigencia del documento: </b>{documento.fecha_inicio_vigencia}</li>"
    mensaje += f"<li><b>Fecha fin de vigencia del documento: </b>{documento.fecha_expiracion}</li>"
    mensaje += f"<li><b>Empresa proveedora: </b>{documento.id_empresa_proveedora.nombre_comercial}</li>"

    #DIAS RESTANTES
    hoy = date.today()
    hoy = date.today()
    dias = documento.fecha_expiracion - hoy
    mensaje += f"<li><b>Dias restantes: </b>{dias.days}</li>"

    return mensaje + "</ul>"

def complemento_mensaje_Alm_MtoVeh(id_elemento):
    mensaje="<ul>"
    mto_vehiculo = ProgramacionMantenimientos.objects.filter(id_programacion_mtto=id_elemento).first()
    if not mto_vehiculo:
        return ""
    

    mensaje += f"<li><b>Nombre del Vehículo: </b>{mto_vehiculo.id_articulo.nombre}</li>"

    if mto_vehiculo.id_articulo.id_marca:
        mensaje += f"<li><b>Marca: </b>{mto_vehiculo.id_articulo.id_marca.nombre}</li>"
    mensaje += f"<li><b>Placa del Vehículo: </b>{mto_vehiculo.id_articulo.doc_identificador_nro}</li>"
    mensaje += f"<li><b>Tipo de mantenimiento: </b>{mto_vehiculo.get_cod_tipo_mantenimiento_display()}</li>"
    mensaje += f"<li><b>Fecha de mantenimiento: </b>{mto_vehiculo.fecha_programada}</li>"
    mensaje += f"<li><b>Motivo de mantenimiento: </b>{mto_vehiculo.motivo_mantenimiento}</li>"
    #dias restantes
    hoy = date.today()
    dias = mto_vehiculo.fecha_programada - hoy
    mensaje += f"<li><b>Dias restantes: </b>{dias.days}</li>"

    mensaje +="</ul>"
    print(mensaje)
    return mensaje


def complemento_mensaje_Alm_MtoAct(id_elemento):
    mensaje="<ul>"
    mto_activo = ProgramacionMantenimientos.objects.filter(id_programacion_mtto=id_elemento).first()
    if not mto_activo:
        return ""
    

    mensaje += f"<li><b>Nombre del activo: </b>{mto_activo.id_articulo.nombre}</li>"

    if mto_activo.id_articulo.id_marca:
        mensaje += f"<li><b>Marca: </b>{mto_activo.id_articulo.id_marca.nombre}</li>"
    mensaje += f"<li><b>Serial del activo: </b>{mto_activo.id_articulo.doc_identificador_nro}</li>"
    mensaje += f"<li><b>Tipo de mantenimiento: </b>{mto_activo.get_cod_tipo_mantenimiento_display()}</li>"
    mensaje += f"<li><b>Fecha de mantenimiento: </b>{mto_activo.fecha_programada}</li>"
    mensaje += f"<li><b>Motivo de mantenimiento: </b>{mto_activo.motivo_mantenimiento}</li>"
    #dias restantes
    hoy = date.today()
    dias = mto_activo.fecha_programada - hoy
    mensaje += f"<li><b>Dias restantes: </b>{dias.days}</li>"

    mensaje +="</ul>"
    print(mensaje)
    return mensaje


def complemento_mensaje_Alm_MtoCom(id_elemento):

    mensaje="<ul>"
    mto_activo = ProgramacionMantenimientos.objects.filter(id_programacion_mtto=id_elemento).first()
    if not mto_activo:
        return ""
    

    mensaje += f"<li><b>Nombre del Computador: </b>{mto_activo.id_articulo.nombre}</li>"

    if mto_activo.id_articulo.id_marca:
        mensaje += f"<li><b>Marca: </b>{mto_activo.id_articulo.id_marca.nombre}</li>"
    mensaje += f"<li><b>Serial del activo: </b>{mto_activo.id_articulo.doc_identificador_nro}</li>"
    mensaje += f"<li><b>Tipo de mantenimiento: </b>{mto_activo.get_cod_tipo_mantenimiento_display()}</li>"
    mensaje += f"<li><b>Fecha de mantenimiento: </b>{mto_activo.fecha_programada}</li>"
    mensaje += f"<li><b>Motivo de mantenimiento: </b>{mto_activo.motivo_mantenimiento}</li>"
    #dias restantes
    hoy = date.today()
    dias = mto_activo.fecha_programada - hoy
    mensaje += f"<li><b>Dias restantes: </b>{dias.days}</li>"

    mensaje +="</ul>"
    print(mensaje)
    return mensaje




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
    print(alertas_generadas)
    #Alerta en Fecha Fija - Programadas con o sin Repeticiones anteriores o posteriores  (con y sin año).
    
    for programada in alertas_generadas:
            
        
            if   programada.agno_cumplimiento:
                agno_alerta=programada.agno_cumplimiento
                agno_fijo=True
            else:
                agno_alerta=numero_agno
                agno_fijo=False


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
                                  programar_alerta(programada,"ANTES",False,agno_fijo)
                                  print("LA ALERTA SE GENERO ANTES DE LA FECHA: "+ str(fecha_frecuencia))

                            fecha_frecuencia= fecha_frecuencia + timedelta(days=frecuencia_pre)
                        
                    if  fecha_alerta_base==fecha_actual:
                         programar_alerta(programada,"AHORA",False,agno_fijo)
                         print("ES HOY LA ALERTA BASE")
                         

                    #ALERTAS POST
                    
                    if frecuencia_dias_post!=0 and cantidad_repeticiones_post!=0:
                        fecha_frecuencia=fecha_alerta_base +timedelta(days=frecuencia_dias_post)
                        for _ in range(cantidad_repeticiones_post):
                             #print("ALERTAS GENERADAS DESPUES: "+str(fecha_frecuencia))

                             if fecha_frecuencia==fecha_actual:
                                  ultima_rep=False
                                  if fecha_lim_superior==fecha_frecuencia:
                                      ultima_rep=True
                                  print("LA ALERTA SE GENERO DESPUES DE LA FECHA: "+ str(fecha_frecuencia))
                                  programar_alerta(programada,"DESPUES",ultima_rep,agno_fijo)
                             fecha_frecuencia +=  timedelta(days=frecuencia_dias_post)
                            
                    
                    

                    print("##############################")
                    

def programar_alerta(programada,clasificacion,ultima_rep,agno_fijo):
        perfiles_actuales=ConfiguracionEntidad.objects.first()
        nombre_funcion = programada.nombre_funcion_comple_mensaje
        funcion = globals().get(nombre_funcion)

        print('FUNCION ES :')
        print(funcion)
        print('###########################################')
        cadena=""
        print(clasificacion)
        print(programada)
        id_responsable=None
        if funcion:
            if programada.cod_clase_alerta.cod_clase_alerta == 'Gest_TRPqr' or programada.cod_clase_alerta.cod_clase_alerta == 'Alm_MtoAct' or  programada.cod_clase_alerta.cod_clase_alerta == 'Ges_EliDoc' or programada.cod_clase_alerta.cod_clase_alerta == 'Alm_VeDocV' or  programada.cod_clase_alerta.cod_clase_alerta =='Alm_MtoCom' or programada.cod_clase_alerta.cod_clase_alerta == 'Alm_MtoVeh':
                cadena=funcion(programada.id_elemento_implicado)
            else:
                
                cadena=funcion()
                #print(cadena)
        else:
            print("La función no fue encontrada.")

        data_alerga_generada={}
        data_alerga_generada['nombre_clase_alerta']=programada.nombre_clase_alerta
   
        data_alerga_generada['mensaje']=""
        if clasificacion=="ANTES":
            data_alerga_generada['mensaje']+=programada.mensaje_base_previo#VALIDAR CAMPO <1000
        elif clasificacion=="AHORA":
            data_alerga_generada['mensaje']+=programada.mensaje_base_del_dia#VALIDAR CAMPO <1000
        elif clasificacion=="DESPUES":
            data_alerga_generada['mensaje']+=programada.mensaje_base_vencido#VALIDAR CAMPO <1000

        if programada.complemento_mensaje:
            data_alerga_generada['mensaje']+=" "+programada.complemento_mensaje
        
        data_alerga_generada['mensaje']+=" "+cadena
        #FIN
        data_alerga_generada['cod_categoria_alerta']=programada.cod_categoria_alerta
        data_alerga_generada['nivel_prioridad']=programada.nivel_prioridad
        if programada.id_modulo_destino:

            data_alerga_generada['id_modulo_destino']=programada.id_modulo_destino.id_modulo
        data_alerga_generada['id_modulo_generador']=programada.id_modulo_generador.id_modulo
        data_alerga_generada['id_elemento_implicado']=programada.id_elemento_implicado
        data_alerga_generada['id_alerta_programada_origen']=programada.id_alerta_programada
        data_alerga_generada['envio_email']=programada.requiere_envio_email
        #PENDIENTE LEER ENTREGA 38

        data_alerga_generada['es_ultima_repeticion']=ultima_rep
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
        #Pendiente validacion con T043idPersonasSuspendEnAlerSinAgno 

        arreglo_resultante=[]
        if  not agno_fijo:
            lista_suspendidos=[]
            if(programada.id_personas_suspen_alertar_sin_agno):
                lista_suspendidos=(programada.id_personas_suspen_alertar_sin_agno.rstrip("|")).split('|')
                #raise ValidationError(lista_suspendidos)
                arreglo_resultante = [x for x in arreglo_sin_repetidos if x not in lista_suspendidos]
                #raise ValidationError(arreglo_resultante)
            else:
                arreglo_resultante=arreglo_sin_repetidos
        else:
              arreglo_resultante=arreglo_sin_repetidos
        for destino in arreglo_resultante:
            if not destino:
                raise ValidationError("NULOO")
            print(destinatarios)
            bandejas_notificaciones=BandejaAlertaPersona.objects.filter(id_persona=destino).first()
            if bandejas_notificaciones:
            #print(bandejas_notificaciones.id_persona.id_persona)
                alerta_bandeja={}
                alerta_bandeja['leido']=False
                alerta_bandeja['archivado']=False
                email_persona=bandejas_notificaciones.id_persona
                #print("HOLAAAAAAAAAAAAAAAAAAA SI ENTRO ACA")
                print( programada.requiere_envio_email)
                if programada.requiere_envio_email:
                    if  email_persona and email_persona.email:
                        alerta_bandeja['email_usado'] = email_persona.email
                        subject = programada.nombre_clase_alerta
                        
                        template = "alerta.html"

                        context = {'Nombre_alerta':programada.nombre_clase_alerta,'primer_nombre': email_persona.primer_nombre,"mensaje":data_alerga_generada['mensaje']}
                        template = render_to_string((template), context)
                        email_data = {'template': template, 'email_subject': subject, 'to_email':email_persona.email}
                        Util.send_email(email_data)
                        #print(email_data)
                        alerta_bandeja['fecha_envio_email']=datetime.now()

                    else:
                        alerta_bandeja['email_usado'] = None
                else:
                    alerta_bandeja['email_usado'] = None
                if id_responsable and  destino == str(id_responsable):
                        alerta_bandeja['responsable_directo']=True
                else:
                    alerta_bandeja['responsable_directo']=False
                alerta_bandeja['id_alerta_generada']=instance_alerta_generada.id_alerta_generada
                alerta_bandeja['id_bandeja_alerta_persona']=bandejas_notificaciones.id_bandeja_alerta
                
                print(alerta_bandeja)
                
                print(" TIENE AÑO : "+str(agno_fijo))
                print("ES ULTIMA REPETICION: " +str(ultima_rep))
                #raise ValueError("ÑAO")
                serializer_alerta_bandeja=AlertasBandejaAlertaPersonaPostSerializer(data=alerta_bandeja)
                bandejas_notificaciones.pendientes_leer=True
                bandejas_notificaciones.save()
                serializer_alerta_bandeja.is_valid(raise_exception=True)
                instance_alerta_bandeja=serializer_alerta_bandeja.save()
            else:
                print("###DESTINATARIO")
                print(destino)
            #instance_alerta_bandeja=serializer_alerta_bandeja.save()

        #Mantenimiento
        #SI ES DE AÑO  FIJO Y ES LA ULTIMA RETETICION SE ELIMINA
        if ultima_rep:
            if agno_fijo:
                print("AÑO FIJO")
                programada.delete()
            else:
                print("SIN AÑO DEFINIDO")
                programada.id_personas_suspen_alertar_sin_agno=None
                programada.save()


                