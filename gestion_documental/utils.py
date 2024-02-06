# from xhtml2pdf import pisa
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from gestion_documental.models.permisos_models import PermisosUndsOrgActualesSerieExpCCD
from gestion_documental.views.archivos_digitales_views import ArchivosDgitalesCreate
from rest_framework import status
#from weasyprint import HTML
from reportlab.pdfgen import canvas
from io import BytesIO
from gestion_documental.models.ctrl_acceso_models import CtrlAccesoClasificacionExpCCD
from gestion_documental.models.tca_models import CatSeriesUnidadOrgCCD_TRD_TCA
from gestion_documental.views.permisos_views import UnidadesPermisosGetView
from transversal.models.organigrama_models import UnidadesOrganizacionales
from rest_framework import status
from django.db.models import F
from django.template.loader import render_to_string

class UtilsGestor:


    def generar_archivo_blanco(data, nombre_archivo="black.pdf", ruta="home,BIA,Otros,PQRSDF,Complementos"):
        
        
  
        # buffer = HttpResponse(content_type='application/pdf')
        # buffer['Content-Disposition'] = 'attachment; filename="output.pdf"'

        # # Crear el objeto PDF utilizando xhtml2pdf.
        # #pisa_status = pisa.CreatePDF(template, dest=buffer)


        # pdf_bytes = buffer.getvalue()

        buffer = BytesIO()
    #Archivo No Digitalizado Solo Almacenado en Fisico (Buscar en Carpeta Física)
        # Crear el objeto PDF utilizando ReportLab.
        p = canvas.Canvas(buffer)
        p.drawString(100, 800, 'Archivo No Digitalizado Solo Almacenado en Fisico (Buscar en Carpeta Física)')  # Agregar contenido al PDF, puedes omitir esto si todo el contenido está en el HTML
       
        y_position = 780  # Posición inicial en el eje Y

        for key, value in data.items():
            # Agregar cada clave y valor al PDF
            p.drawString(100, y_position, f"{key}: {value}")
            y_position -= 20  # Moverse hacia arriba para la siguiente línea
            


        p.showPage()
        p.save()

    # Obtener el contenido del buffer como bytes
        pdf_bytes = buffer.getvalue()
        
        # response = HttpResponse(pdf_bytes, content_type='application/pdf')
        # response['Content-Disposition'] = 'attachment; filename="output.pdf"'

        # return response



        # Crear un objeto ContentFile con el contenido del PDF.
        # nombre_archivo = "black.pdf"
        pdf_content_file = ContentFile(pdf_bytes,name=nombre_archivo)
        vista_archivos = ArchivosDgitalesCreate()
        # Verificar si la generación del PDF fue exitosa.
        # ruta = "home,BIA,Otros,PQRSDF,Complementos"
        respuesta_archivo = vista_archivos.crear_archivo({"ruta":ruta,'es_Doc_elec_archivo':False},pdf_content_file)
        data_archivo = respuesta_archivo.data['data']
        if respuesta_archivo.status_code != status.HTTP_201_CREATED:
            return respuesta_archivo
 
        return respuesta_archivo
        
        
        
    @staticmethod
    def validar_permiso_consulta_exp(persona, expediente):
        # Si la Unidad es la actual responsable del expediente
        unidad_persona = persona.id_unidad_organizacional_actual
        unidad_respon_expediente = expediente.id_und_org_oficina_respon_actual.id_unidad_organizacional
        
        if unidad_persona.id_unidad_organizacional == unidad_respon_expediente:
            return True
        
        # Si la Unidad no es la actual responsable del expediente
        cat_serie_und_org_exp = expediente.id_cat_serie_und_org_ccd_trd_prop.id_cat_serie_und.id_cat_serie_und
        cat_serie_und_org_ctrl_acceso = CtrlAccesoClasificacionExpCCD.objects.filter(id_cat_serie_und_org_ccd=cat_serie_und_org_exp).first()
        
        # Verificar si existe alguno en donde el ID T222Id_CatSerie_UndOrg_CCD sea el mismo del Catálogo del Expediente seleccionado
        # En caso de que sí exista
        if cat_serie_und_org_ctrl_acceso:
            # Si los atributos en TRUE son T222entidadEntera_Consultar
            if cat_serie_und_org_ctrl_acceso.entidad_entera_consultar:
                return True
            # Si los atributos en TRUE son cualquiera de los demás atributos de la tabla
            else:
                # Se debe verificar si la Unidad a la cual pertenece la persona que está logueada en ese momento es la Sección Actual Responsable de la Serie Documental del Expediente seleccionado
                if unidad_persona.cod_agrupacion_documental and cat_serie_und_org_ctrl_acceso.seccion_actual_respon_serie_doc_consultar:
                    if expediente.id_und_seccion_propietaria_serie.id_unidad_org_actual_admin_series.id_unidad_organizacional == unidad_persona.id_unidad_organizacional:
                        return True
                # Se debe verificar si la Unidad a la cual pertenece la persona que está logueada en ese momento es la Sección Raíz del Organigrama actual
                elif unidad_persona.cod_agrupacion_documental and cat_serie_und_org_ctrl_acceso.seccion_raiz_organi_actual_consultar:
                    if unidad_persona.unidad_raiz:
                        return True
                # Se debe verificar si mi Unidad es del mismo nivel o uno superior al de la Unidad Sección Actual responsable del Expediente seleccionado en el módulo para su consulta
                elif unidad_persona.cod_agrupacion_documental and cat_serie_und_org_ctrl_acceso.secciones_actuales_mismo_o_sup_nivel_respon_consulta:
                    orden_unidad_org_respon_exp = expediente.id_und_seccion_propietaria_serie.id_unidad_org_actual_admin_series.id_nivel_organigrama.orden_nivel
                    unidades_org_actual = UnidadesOrganizacionales.objects.filter(id_organigrama__actual=True, id_nivel_organigrama__orden_nivel__gte=orden_unidad_org_respon_exp).exclude(cod_agrupacion_documental=None).values_list('id_unidad_organizacional', flat=True)
                    if unidad_persona.id_unidad_organizacional in unidades_org_actual:
                        return True
                # Se debe verificar si la Unidad a la cual pertenece la persona que está logueada en ese momento es de un nivel inferior al de la Unidad responsable del Expediente seleccionado en el módulo para su consulta
                elif unidad_persona.cod_agrupacion_documental and cat_serie_und_org_ctrl_acceso.secciones_actuales_inf_nivel_respon_consultar:
                    orden_unidad_org_respon_exp = expediente.id_und_seccion_propietaria_serie.id_unidad_org_actual_admin_series.id_nivel_organigrama.orden_nivel
                    unidades_org_actual = UnidadesOrganizacionales.objects.filter(id_organigrama__actual=True, id_nivel_organigrama__orden_nivel__lt=orden_unidad_org_respon_exp).exclude(cod_agrupacion_documental=None).values_list('id_unidad_organizacional', flat=True)
                    if unidad_persona.id_unidad_organizacional in unidades_org_actual:
                        return True
                # Se debe verificar si la Unidad a la cual pertenece la persona que está logueada en ese momento es hija de la Unidad Responsable de la Serie Documental del Expediente seleccionado y adicionalmente es del mismo nivel o uno superior al de la Unidad Responsable del mismo Expediente
                elif cat_serie_und_org_ctrl_acceso.unds_org_sec_respon_mismo_o_sup_nivel_resp_exp_consultar:
                    unidad_org_oficina_respon_actual_exp = expediente.id_und_org_oficina_respon_actual
                    unidad_org_respon_exp = expediente.id_und_seccion_propietaria_serie.id_unidad_org_actual_admin_series
                    
                    unidades_org_respon_exp_hijas = UnidadesOrganizacionales.objects.filter(id_unidad_org_padre=unidad_org_respon_exp.id_unidad_organizacional).values(
                        'activo',
                        'cod_agrupacion_documental',
                        id_und_organizacional_actual = F('id_unidad_organizacional'),
                        nombre_und_organizacional_actual = F('nombre'),
                        codigo_und_organizacional_actual = F('codigo')
                    )
                    
                    unidades_primera_seccion = UnidadesPermisosGetView()
                    unidades_primera_seccion_family = unidades_primera_seccion.get_family(unidades_org_respon_exp_hijas)
                    
                    unidades_org_respon_exp_hijas_list = [unidad['id_unidad_organizacional'] for unidad in unidades_org_respon_exp_hijas]
                    unidades_family_list = [unidad['id_unidad_organizacional'] for unidad in unidades_primera_seccion_family]
                    
                    unidades_list = unidades_org_respon_exp_hijas_list + unidades_family_list
                    unidades_family_instances = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional__in=unidades_list, id_nivel_organigrama__orden_nivel__gte=unidad_org_oficina_respon_actual_exp.id_nivel_organigrama.orden_nivel).values_list('id_unidad_organizacional', flat=True)
                    
                    if unidad_persona.id_unidad_organizacional in unidades_family_instances:
                        return True
                # Se debe verificar si la Unidad a la cual pertenece la persona que está logueada en ese momento es hija de la Unidad Responsable de la Serie Documental del Expediente seleccionado y adicionalmente es de un nivel inferior al de la Unidad Responsable del mismo Expediente
                elif cat_serie_und_org_ctrl_acceso.unds_org_sec_respon_inf_nivel_resp_exp_consultar:
                    unidad_org_oficina_respon_actual_exp = expediente.id_und_org_oficina_respon_actual
                    unidad_org_respon_exp = expediente.id_und_seccion_propietaria_serie.id_unidad_org_actual_admin_series
                    
                    unidades_org_respon_exp_hijas = UnidadesOrganizacionales.objects.filter(id_unidad_org_padre=unidad_org_respon_exp.id_unidad_organizacional).values(
                        'activo',
                        'cod_agrupacion_documental',
                        id_und_organizacional_actual = F('id_unidad_organizacional'),
                        nombre_und_organizacional_actual = F('nombre'),
                        codigo_und_organizacional_actual = F('codigo')
                    )
                    
                    unidades_primera_seccion = UnidadesPermisosGetView()
                    unidades_primera_seccion_family = unidades_primera_seccion.get_family(unidades_org_respon_exp_hijas)
                    
                    unidades_org_respon_exp_hijas_list = [unidad['id_unidad_organizacional'] for unidad in unidades_org_respon_exp_hijas]
                    unidades_family_list = [unidad['id_unidad_organizacional'] for unidad in unidades_primera_seccion_family]
                    
                    unidades_list = unidades_org_respon_exp_hijas_list + unidades_family_list
                    unidades_family_instances = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional__in=unidades_list, id_nivel_organigrama__orden_nivel__lt=unidad_org_oficina_respon_actual_exp.id_nivel_organigrama.orden_nivel).values_list('id_unidad_organizacional', flat=True)
                    
                    if unidad_persona.id_unidad_organizacional in unidades_family_instances:
                        return True
        # En caso de que no exista
        else:
            tripleta_tca = CatSeriesUnidadOrgCCD_TRD_TCA.objects.filter(id_cat_serie_und_ccd_trd=expediente.id_cat_serie_und_org_ccd_trd_prop.id_catserie_unidadorg).first()
            if tripleta_tca:
                conf_general_ctrl_acceso = CtrlAccesoClasificacionExpCCD.objects.filter(id_ccd=expediente.id_cat_serie_und_org_ccd_trd_prop.id_cat_serie_und.id_catalogo_serie.id_serie_doc.id_ccd, cod_clasificacion_exp=tripleta_tca.cod_clas_expediente.cod_clas_expediente).first()
                
                if conf_general_ctrl_acceso:
                    
                    # Si los atributos en TRUE son T222entidadEntera_Consultar
                    if conf_general_ctrl_acceso.entidad_entera_consultar:
                        return True
                    # Si los atributos en TRUE son cualquiera de los demás atributos de la tabla
                    else:
                        # Se debe verificar si la Unidad a la cual pertenece la persona que está logueada en ese momento es la Sección Actual Responsable de la Serie Documental del Expediente seleccionado
                        if unidad_persona.cod_agrupacion_documental and conf_general_ctrl_acceso.seccion_actual_respon_serie_doc_consultar:
                            if expediente.id_und_seccion_propietaria_serie.id_unidad_org_actual_admin_series.id_unidad_organizacional == unidad_persona.id_unidad_organizacional:
                                return True
                        # Se debe verificar si la Unidad a la cual pertenece la persona que está logueada en ese momento es la Sección Raíz del Organigrama actual
                        elif unidad_persona.cod_agrupacion_documental and conf_general_ctrl_acceso.seccion_raiz_organi_actual_consultar:
                            if unidad_persona.unidad_raiz:
                                return True
                        # Se debe verificar si mi Unidad es del mismo nivel o uno superior al de la Unidad Sección Actual responsable del Expediente seleccionado en el módulo para su consulta
                        elif unidad_persona.cod_agrupacion_documental and conf_general_ctrl_acceso.secciones_actuales_mismo_o_sup_nivel_respon_consulta:
                            orden_unidad_org_respon_exp = expediente.id_und_seccion_propietaria_serie.id_unidad_org_actual_admin_series.id_nivel_organigrama.orden_nivel
                            unidades_org_actual = UnidadesOrganizacionales.objects.filter(id_organigrama__actual=True, id_nivel_organigrama__orden_nivel__gte=orden_unidad_org_respon_exp).exclude(cod_agrupacion_documental=None).values_list('id_unidad_organizacional', flat=True)
                            if unidad_persona.id_unidad_organizacional in unidades_org_actual:
                                return True
                        # Se debe verificar si la Unidad a la cual pertenece la persona que está logueada en ese momento es de un nivel inferior al de la Unidad responsable del Expediente seleccionado en el módulo para su consulta
                        elif unidad_persona.cod_agrupacion_documental and conf_general_ctrl_acceso.secciones_actuales_inf_nivel_respon_consultar:
                            orden_unidad_org_respon_exp = expediente.id_und_seccion_propietaria_serie.id_unidad_org_actual_admin_series.id_nivel_organigrama.orden_nivel
                            unidades_org_actual = UnidadesOrganizacionales.objects.filter(id_organigrama__actual=True, id_nivel_organigrama__orden_nivel__lt=orden_unidad_org_respon_exp).exclude(cod_agrupacion_documental=None).values_list('id_unidad_organizacional', flat=True)
                            if unidad_persona.id_unidad_organizacional in unidades_org_actual:
                                return True
                        # Se debe verificar si la Unidad a la cual pertenece la persona que está logueada en ese momento es hija de la Unidad Responsable de la Serie Documental del Expediente seleccionado y adicionalmente es del mismo nivel o uno superior al de la Unidad Responsable del mismo Expediente
                        elif conf_general_ctrl_acceso.unds_org_sec_respon_mismo_o_sup_nivel_resp_exp_consultar:
                            unidad_org_oficina_respon_actual_exp = expediente.id_und_org_oficina_respon_actual
                            unidad_org_respon_exp = expediente.id_und_seccion_propietaria_serie.id_unidad_org_actual_admin_series
                            
                            unidades_org_respon_exp_hijas = UnidadesOrganizacionales.objects.filter(id_unidad_org_padre=unidad_org_respon_exp.id_unidad_organizacional).values(
                                'activo',
                                'cod_agrupacion_documental',
                                id_und_organizacional_actual = F('id_unidad_organizacional'),
                                nombre_und_organizacional_actual = F('nombre'),
                                codigo_und_organizacional_actual = F('codigo')
                            )
                            
                            unidades_primera_seccion = UnidadesPermisosGetView()
                            unidades_primera_seccion_family = unidades_primera_seccion.get_family(unidades_org_respon_exp_hijas)
                            
                            unidades_org_respon_exp_hijas_list = [unidad['id_unidad_organizacional'] for unidad in unidades_org_respon_exp_hijas]
                            unidades_family_list = [unidad['id_unidad_organizacional'] for unidad in unidades_primera_seccion_family]
                            
                            unidades_list = unidades_org_respon_exp_hijas_list + unidades_family_list
                            unidades_family_instances = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional__in=unidades_list, id_nivel_organigrama__orden_nivel__gte=unidad_org_oficina_respon_actual_exp.id_nivel_organigrama.orden_nivel).values_list('id_unidad_organizacional', flat=True)
                            
                            if unidad_persona.id_unidad_organizacional in unidades_family_instances:
                                return True
                        # Se debe verificar si la Unidad a la cual pertenece la persona que está logueada en ese momento es hija de la Unidad Responsable de la Serie Documental del Expediente seleccionado y adicionalmente es de un nivel inferior al de la Unidad Responsable del mismo Expediente
                        elif conf_general_ctrl_acceso.unds_org_sec_respon_inf_nivel_resp_exp_consultar:
                            unidad_org_oficina_respon_actual_exp = expediente.id_und_org_oficina_respon_actual
                            unidad_org_respon_exp = expediente.id_und_seccion_propietaria_serie.id_unidad_org_actual_admin_series
                            
                            unidades_org_respon_exp_hijas = UnidadesOrganizacionales.objects.filter(id_unidad_org_padre=unidad_org_respon_exp.id_unidad_organizacional).values(
                                'activo',
                                'cod_agrupacion_documental',
                                id_und_organizacional_actual = F('id_unidad_organizacional'),
                                nombre_und_organizacional_actual = F('nombre'),
                                codigo_und_organizacional_actual = F('codigo')
                            )
                            
                            unidades_primera_seccion = UnidadesPermisosGetView()
                            unidades_primera_seccion_family = unidades_primera_seccion.get_family(unidades_org_respon_exp_hijas)
                            
                            unidades_org_respon_exp_hijas_list = [unidad['id_unidad_organizacional'] for unidad in unidades_org_respon_exp_hijas]
                            unidades_family_list = [unidad['id_unidad_organizacional'] for unidad in unidades_primera_seccion_family]
                            
                            unidades_list = unidades_org_respon_exp_hijas_list + unidades_family_list
                            unidades_family_instances = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional__in=unidades_list, id_nivel_organigrama__orden_nivel__lt=unidad_org_oficina_respon_actual_exp.id_nivel_organigrama.orden_nivel).values_list('id_unidad_organizacional', flat=True)
                            
                            if unidad_persona.id_unidad_organizacional in unidades_family_instances:
                                return True
        return False
    
    @staticmethod
    def validar_permiso_descarga_exp(persona, expediente):
        # Si la Unidad es la actual responsable del expediente
        unidad_persona = persona.id_unidad_organizacional_actual
        unidad_respon_expediente = expediente.id_und_org_oficina_respon_actual.id_unidad_organizacional
        
        if unidad_persona.id_unidad_organizacional == unidad_respon_expediente:
            return True
        
        # Si la Unidad no es la actual responsable del expediente
        cat_serie_und_org_exp = expediente.id_cat_serie_und_org_ccd_trd_prop.id_cat_serie_und.id_cat_serie_und
        cat_serie_und_org_ctrl_acceso = CtrlAccesoClasificacionExpCCD.objects.filter(id_cat_serie_und_org_ccd=cat_serie_und_org_exp).first()
        
        # Verificar si existe alguno en donde el ID T222Id_CatSerie_UndOrg_CCD sea el mismo del Catálogo del Expediente seleccionado
        # En caso de que sí exista
        if cat_serie_und_org_ctrl_acceso:
            # Si los atributos en TRUE son T222entidadEntera_Descargar
            if cat_serie_und_org_ctrl_acceso.entidad_entera_descargar:
                return True
            # Si los atributos en TRUE son cualquiera de los demás atributos de la tabla
            else:
                # Se debe verificar si la Unidad a la cual pertenece la persona que está logueada en ese momento es la Sección Actual Responsable de la Serie Documental del Expediente seleccionado
                if unidad_persona.cod_agrupacion_documental and cat_serie_und_org_ctrl_acceso.seccion_actual_respon_serie_doc_descargar:
                    if expediente.id_und_seccion_propietaria_serie.id_unidad_org_actual_admin_series.id_unidad_organizacional == unidad_persona.id_unidad_organizacional:
                        return True
                # Se debe verificar si la Unidad a la cual pertenece la persona que está logueada en ese momento es la Sección Raíz del Organigrama actual
                elif unidad_persona.cod_agrupacion_documental and cat_serie_und_org_ctrl_acceso.seccion_raiz_organi_actual_descargar:
                    if unidad_persona.unidad_raiz:
                        return True
                # Se debe verificar si mi Unidad es del mismo nivel o uno superior al de la Unidad Sección Actual responsable del Expediente seleccionado en el módulo para su descarga
                elif unidad_persona.cod_agrupacion_documental and cat_serie_und_org_ctrl_acceso.secciones_actuales_mismo_o_sup_nivel_respon_descargar:
                    orden_unidad_org_respon_exp = expediente.id_und_seccion_propietaria_serie.id_unidad_org_actual_admin_series.id_nivel_organigrama.orden_nivel
                    unidades_org_actual = UnidadesOrganizacionales.objects.filter(id_organigrama__actual=True, id_nivel_organigrama__orden_nivel__gte=orden_unidad_org_respon_exp).exclude(cod_agrupacion_documental=None).values_list('id_unidad_organizacional', flat=True)
                    if unidad_persona.id_unidad_organizacional in unidades_org_actual:
                        return True
                # Se debe verificar si la Unidad a la cual pertenece la persona que está logueada en ese momento es de un nivel inferior al de la Unidad responsable del Expediente seleccionado en el módulo para su descarga
                elif unidad_persona.cod_agrupacion_documental and cat_serie_und_org_ctrl_acceso.secciones_actuales_inf_nivel_respon_descargar:
                    orden_unidad_org_respon_exp = expediente.id_und_seccion_propietaria_serie.id_unidad_org_actual_admin_series.id_nivel_organigrama.orden_nivel
                    unidades_org_actual = UnidadesOrganizacionales.objects.filter(id_organigrama__actual=True, id_nivel_organigrama__orden_nivel__lt=orden_unidad_org_respon_exp).exclude(cod_agrupacion_documental=None).values_list('id_unidad_organizacional', flat=True)
                    if unidad_persona.id_unidad_organizacional in unidades_org_actual:
                        return True
                # Se debe verificar si la Unidad a la cual pertenece la persona que está logueada en ese momento es hija de la Unidad Responsable de la Serie Documental del Expediente seleccionado y adicionalmente es del mismo nivel o uno superior al de la Unidad Responsable del mismo Expediente
                elif cat_serie_und_org_ctrl_acceso.unds_org_sec_respon_mismo_o_sup_nivel_resp_exp_descargar:
                    unidad_org_oficina_respon_actual_exp = expediente.id_und_org_oficina_respon_actual
                    unidad_org_respon_exp = expediente.id_und_seccion_propietaria_serie.id_unidad_org_actual_admin_series
                    
                    unidades_org_respon_exp_hijas = UnidadesOrganizacionales.objects.filter(id_unidad_org_padre=unidad_org_respon_exp.id_unidad_organizacional).values(
                        'activo',
                        'cod_agrupacion_documental',
                        id_und_organizacional_actual = F('id_unidad_organizacional'),
                        nombre_und_organizacional_actual = F('nombre'),
                        codigo_und_organizacional_actual = F('codigo')
                    )
                    
                    unidades_primera_seccion = UnidadesPermisosGetView()
                    unidades_primera_seccion_family = unidades_primera_seccion.get_family(unidades_org_respon_exp_hijas)
                    
                    unidades_org_respon_exp_hijas_list = [unidad['id_unidad_organizacional'] for unidad in unidades_org_respon_exp_hijas]
                    unidades_family_list = [unidad['id_unidad_organizacional'] for unidad in unidades_primera_seccion_family]
                    
                    unidades_list = unidades_org_respon_exp_hijas_list + unidades_family_list
                    unidades_family_instances = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional__in=unidades_list, id_nivel_organigrama__orden_nivel__gte=unidad_org_oficina_respon_actual_exp.id_nivel_organigrama.orden_nivel).values_list('id_unidad_organizacional', flat=True)
                    
                    if unidad_persona.id_unidad_organizacional in unidades_family_instances:
                        return True
                # Se debe verificar si la Unidad a la cual pertenece la persona que está logueada en ese momento es hija de la Unidad Responsable de la Serie Documental del Expediente seleccionado y adicionalmente es de un nivel inferior al de la Unidad Responsable del mismo Expediente
                elif cat_serie_und_org_ctrl_acceso.unds_org_sec_respon_inf_nivel_resp_exp_descargar:
                    unidad_org_oficina_respon_actual_exp = expediente.id_und_org_oficina_respon_actual
                    unidad_org_respon_exp = expediente.id_und_seccion_propietaria_serie.id_unidad_org_actual_admin_series
                    
                    unidades_org_respon_exp_hijas = UnidadesOrganizacionales.objects.filter(id_unidad_org_padre=unidad_org_respon_exp.id_unidad_organizacional).values(
                        'activo',
                        'cod_agrupacion_documental',
                        id_und_organizacional_actual = F('id_unidad_organizacional'),
                        nombre_und_organizacional_actual = F('nombre'),
                        codigo_und_organizacional_actual = F('codigo')
                    )
                    
                    unidades_primera_seccion = UnidadesPermisosGetView()
                    unidades_primera_seccion_family = unidades_primera_seccion.get_family(unidades_org_respon_exp_hijas)
                    
                    unidades_org_respon_exp_hijas_list = [unidad['id_unidad_organizacional'] for unidad in unidades_org_respon_exp_hijas]
                    unidades_family_list = [unidad['id_unidad_organizacional'] for unidad in unidades_primera_seccion_family]
                    
                    unidades_list = unidades_org_respon_exp_hijas_list + unidades_family_list
                    unidades_family_instances = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional__in=unidades_list, id_nivel_organigrama__orden_nivel__lt=unidad_org_oficina_respon_actual_exp.id_nivel_organigrama.orden_nivel).values_list('id_unidad_organizacional', flat=True)
                    
                    if unidad_persona.id_unidad_organizacional in unidades_family_instances:
                        return True
        # En caso de que no exista
        else:
            tripleta_tca = CatSeriesUnidadOrgCCD_TRD_TCA.objects.filter(id_cat_serie_und_ccd_trd=expediente.id_cat_serie_und_org_ccd_trd_prop.id_catserie_unidadorg).first()
            if tripleta_tca:
                conf_general_ctrl_acceso = CtrlAccesoClasificacionExpCCD.objects.filter(id_ccd=expediente.id_cat_serie_und_org_ccd_trd_prop.id_cat_serie_und.id_catalogo_serie.id_serie_doc.id_ccd, cod_clasificacion_exp=tripleta_tca.cod_clas_expediente.cod_clas_expediente).first()
                
                if conf_general_ctrl_acceso:
                    
                    # Si los atributos en TRUE son T222entidadEntera_Descargar
                    if conf_general_ctrl_acceso.entidad_entera_descargar:
                        return True
                    # Si los atributos en TRUE son cualquiera de los demás atributos de la tabla
                    else:
                        # Se debe verificar si la Unidad a la cual pertenece la persona que está logueada en ese momento es la Sección Actual Responsable de la Serie Documental del Expediente seleccionado
                        if unidad_persona.cod_agrupacion_documental and conf_general_ctrl_acceso.seccion_actual_respon_serie_doc_descargar:
                            if expediente.id_und_seccion_propietaria_serie.id_unidad_org_actual_admin_series.id_unidad_organizacional == unidad_persona.id_unidad_organizacional:
                                return True
                        # Se debe verificar si la Unidad a la cual pertenece la persona que está logueada en ese momento es la Sección Raíz del Organigrama actual
                        elif unidad_persona.cod_agrupacion_documental and conf_general_ctrl_acceso.seccion_raiz_organi_actual_descargar:
                            if unidad_persona.unidad_raiz:
                                return True
                        # Se debe verificar si mi Unidad es del mismo nivel o uno superior al de la Unidad Sección Actual responsable del Expediente seleccionado en el módulo para su descarga
                        elif unidad_persona.cod_agrupacion_documental and conf_general_ctrl_acceso.secciones_actuales_mismo_o_sup_nivel_respon_descargar:
                            orden_unidad_org_respon_exp = expediente.id_und_seccion_propietaria_serie.id_unidad_org_actual_admin_series.id_nivel_organigrama.orden_nivel
                            unidades_org_actual = UnidadesOrganizacionales.objects.filter(id_organigrama__actual=True, id_nivel_organigrama__orden_nivel__gte=orden_unidad_org_respon_exp).exclude(cod_agrupacion_documental=None).values_list('id_unidad_organizacional', flat=True)
                            if unidad_persona.id_unidad_organizacional in unidades_org_actual:
                                return True
                        # Se debe verificar si la Unidad a la cual pertenece la persona que está logueada en ese momento es de un nivel inferior al de la Unidad responsable del Expediente seleccionado en el módulo para su consulta
                        elif unidad_persona.cod_agrupacion_documental and conf_general_ctrl_acceso.secciones_actuales_inf_nivel_respon_descargar:
                            orden_unidad_org_respon_exp = expediente.id_und_seccion_propietaria_serie.id_unidad_org_actual_admin_series.id_nivel_organigrama.orden_nivel
                            unidades_org_actual = UnidadesOrganizacionales.objects.filter(id_organigrama__actual=True, id_nivel_organigrama__orden_nivel__lt=orden_unidad_org_respon_exp).exclude(cod_agrupacion_documental=None).values_list('id_unidad_organizacional', flat=True)
                            if unidad_persona.id_unidad_organizacional in unidades_org_actual:
                                return True
                        # Se debe verificar si la Unidad a la cual pertenece la persona que está logueada en ese momento es hija de la Unidad Responsable de la Serie Documental del Expediente seleccionado y adicionalmente es del mismo nivel o uno superior al de la Unidad Responsable del mismo Expediente
                        elif conf_general_ctrl_acceso.unds_org_sec_respon_mismo_o_sup_nivel_resp_exp_descargar:
                            unidad_org_oficina_respon_actual_exp = expediente.id_und_org_oficina_respon_actual
                            unidad_org_respon_exp = expediente.id_und_seccion_propietaria_serie.id_unidad_org_actual_admin_series
                            
                            unidades_org_respon_exp_hijas = UnidadesOrganizacionales.objects.filter(id_unidad_org_padre=unidad_org_respon_exp.id_unidad_organizacional).values(
                                'activo',
                                'cod_agrupacion_documental',
                                id_und_organizacional_actual = F('id_unidad_organizacional'),
                                nombre_und_organizacional_actual = F('nombre'),
                                codigo_und_organizacional_actual = F('codigo')
                            )
                            
                            unidades_primera_seccion = UnidadesPermisosGetView()
                            unidades_primera_seccion_family = unidades_primera_seccion.get_family(unidades_org_respon_exp_hijas)
                            
                            unidades_org_respon_exp_hijas_list = [unidad['id_unidad_organizacional'] for unidad in unidades_org_respon_exp_hijas]
                            unidades_family_list = [unidad['id_unidad_organizacional'] for unidad in unidades_primera_seccion_family]
                            
                            unidades_list = unidades_org_respon_exp_hijas_list + unidades_family_list
                            unidades_family_instances = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional__in=unidades_list, id_nivel_organigrama__orden_nivel__gte=unidad_org_oficina_respon_actual_exp.id_nivel_organigrama.orden_nivel).values_list('id_unidad_organizacional', flat=True)
                            
                            if unidad_persona.id_unidad_organizacional in unidades_family_instances:
                                return True
                        # Se debe verificar si la Unidad a la cual pertenece la persona que está logueada en ese momento es hija de la Unidad Responsable de la Serie Documental del Expediente seleccionado y adicionalmente es de un nivel inferior al de la Unidad Responsable del mismo Expediente
                        elif conf_general_ctrl_acceso.unds_org_sec_respon_inf_nivel_resp_exp_descargar:
                            unidad_org_oficina_respon_actual_exp = expediente.id_und_org_oficina_respon_actual
                            unidad_org_respon_exp = expediente.id_und_seccion_propietaria_serie.id_unidad_org_actual_admin_series
                            
                            unidades_org_respon_exp_hijas = UnidadesOrganizacionales.objects.filter(id_unidad_org_padre=unidad_org_respon_exp.id_unidad_organizacional).values(
                                'activo',
                                'cod_agrupacion_documental',
                                id_und_organizacional_actual = F('id_unidad_organizacional'),
                                nombre_und_organizacional_actual = F('nombre'),
                                codigo_und_organizacional_actual = F('codigo')
                            )
                            
                            unidades_primera_seccion = UnidadesPermisosGetView()
                            unidades_primera_seccion_family = unidades_primera_seccion.get_family(unidades_org_respon_exp_hijas)
                            
                            unidades_org_respon_exp_hijas_list = [unidad['id_unidad_organizacional'] for unidad in unidades_org_respon_exp_hijas]
                            unidades_family_list = [unidad['id_unidad_organizacional'] for unidad in unidades_primera_seccion_family]
                            
                            unidades_list = unidades_org_respon_exp_hijas_list + unidades_family_list
                            unidades_family_instances = UnidadesOrganizacionales.objects.filter(id_unidad_organizacional__in=unidades_list, id_nivel_organigrama__orden_nivel__lt=unidad_org_oficina_respon_actual_exp.id_nivel_organigrama.orden_nivel).values_list('id_unidad_organizacional', flat=True)
                            
                            if unidad_persona.id_unidad_organizacional in unidades_family_instances:
                                return True
        return False
    
    @staticmethod
    def validar_permisos_unds_org_actuales_consulta_exp(persona, expediente):
        unidad_persona = persona.id_unidad_organizacional_actual
        
        permisos_unds_org_actuales = PermisosUndsOrgActualesSerieExpCCD.objects.filter(id_cat_serie_und_org_ccd__id_catalogo_serie__id_serie_doc=expediente.id_cat_serie_und_org_ccd_trd_prop.id_cat_serie_und.id_serie_doc.id_serie_doc, id_und_organizacional_actual=unidad_persona).first()
        if permisos_unds_org_actuales.consultar_expedientes_no_propios:
            return True
        
        return False
    
    @staticmethod
    def validar_permisos_unds_org_actuales_crear_exp(persona, seccion_subseccion, tripleta):
        unidad_persona = persona.id_unidad_organizacional_actual
        
        if unidad_persona.id_unidad_organizacional == seccion_subseccion.id_unidad_organizacional:
            return True
        
        permisos_unds_org_actuales = PermisosUndsOrgActualesSerieExpCCD.objects.filter(id_cat_serie_und_org_ccd=tripleta.id_cat_serie_und_org_ccd).first()
        if permisos_unds_org_actuales.crear_expedientes:
            return True
        
        return False
    
    @staticmethod
    def validar_permisos_unds_org_actuales_descarga_exp(persona, expediente):
        unidad_persona = persona.id_unidad_organizacional_actual
        
        permisos_unds_org_actuales = PermisosUndsOrgActualesSerieExpCCD.objects.filter(id_cat_serie_und_org_ccd__id_catalogo_serie__id_serie_doc=expediente.id_cat_serie_und_org_ccd_trd_prop.id_cat_serie_und.id_serie_doc.id_serie_doc, id_und_organizacional_actual=unidad_persona).first()
        if permisos_unds_org_actuales.descargar_expedientes_no_propios:
            return True
        
        return False