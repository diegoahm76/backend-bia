from rest_framework import status
from django.db.models import Q
import copy
from datetime import datetime
from rest_framework import generics
from rest_framework.response import Response
from seguridad.utils import Util
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, permission_classes
from seguridad.models import Personas
from gestion_documental.serializers.trd_serializers import (
    TRDSerializer,
    FormatosTiposMedioSerializer
)
from gestion_documental.serializers.ccd_serializers import (
    CCDSerializer
)

from gestion_documental.models.ccd_models import (
    CuadrosClasificacionDocumental,
)
from almacen.models.organigrama_models import (
    Organigramas,
    UnidadesOrganizacionales
    
)
from gestion_documental.models.trd_models import (
    TablaRetencionDocumental,
    TipologiasDocumentales,
    SeriesSubSUnidadOrgTRDTipologias,
    FormatosTiposMedio
)


class GetCCDTerminadoByPk(generics.ListAPIView):
    serializer_class = CCDSerializer
    queryset = CuadrosClasificacionDocumental.objects.filter(~Q(fecha_terminado = None) & Q(fecha_retiro_produccion=None))

    def get(self, request, pk):
        orgamigrama = Organigramas.objects.filter(id_organigrama = pk).first()
        if not orgamigrama:
            return Response({'success': False, 'detail': 'El organigrama ingresado no existe'}, status=status.HTTP_400_BAD_REQUEST)

        if orgamigrama.fecha_terminado == None or orgamigrama.fecha_retiro_produccion != None:
            return Response({'success': False, 'detail': 'El organigrama ingresado ya está retirado o no está terminado'}, status=status.HTTP_400_BAD_REQUEST)
        ccds = CuadrosClasificacionDocumental.objects.filter(~Q(fecha_terminado = None) & Q(fecha_retiro_produccion=None)).filter(id_organigrama = int(orgamigrama.id_organigrama)).values()
        return Response({'success': True, 'detail': 'CCD', 'data': ccds}, status=status.HTTP_201_CREATED)

class GetTRDTerminadoByPk(generics.ListAPIView):
    serializer_class = TRDSerializer
    queryset = TablaRetencionDocumental.objects.filter(~Q(fecha_terminado = None) & Q(fecha_retiro_produccion=None))

    def get(self, request, pk):
        ccd = CuadrosClasificacionDocumental.objects.filter(id_organigrama = pk).first()
        if not ccd:
            return Response({'success': False, 'detail': 'El ccd ingresado no existe'}, status=status.HTTP_400_BAD_REQUEST)

        if ccd.fecha_terminado == None or ccd.fecha_retiro_produccion != None:
            return Response({'success': False, 'detail': 'El ccd ingresado ya está retirado o no está terminado'}, status=status.HTTP_400_BAD_REQUEST)
        trds = TablaRetencionDocumental.objects.filter(~Q(fecha_terminado = None) & Q(fecha_retiro_produccion=None)).filter(id_ccd = int(ccd.id_ccd)).values()
        return Response({'success': True, 'detail': 'CCD', 'data': trds}, status=status.HTTP_201_CREATED)

class Activar(generics.UpdateAPIView):
    parser_classes = (MultiPartParser, FormParser)
    serializer_class =TRDSerializer
    queryset=TablaRetencionDocumental.objects.all()
    permission_classes = [IsAuthenticated]
    def put(self,request):
        json_recibido = request.data
        if not json_recibido:
            return Response({'success': False, 'detail': 'Ingrese información'}, status=status.HTTP_400_BAD_REQUEST)
        if json_recibido['id_organigrama'] == '' or json_recibido['id_organigrama'] == None:
            return Response({'success': False, 'detail': 'Ingrese un organigrama'}, status=status.HTTP_400_BAD_REQUEST)
        if json_recibido['id_ccd'] == '' or json_recibido['id_ccd'] == None:
            return Response({'success': False, 'detail': 'Ingrese cuadro de clasificación documental'}, status=status.HTTP_400_BAD_REQUEST)
        if json_recibido['id_trd'] == '' or json_recibido['id_trd'] == None:
            return Response({'success': False, 'detail': 'Ingrese tabla de retención documental'}, status=status.HTTP_400_BAD_REQUEST)
        if json_recibido['justificacion'] == '' or json_recibido['justificacion'] == None:
            return Response({'success': False, 'detail': 'Ingrese justificación'}, status=status.HTTP_400_BAD_REQUEST)
        if json_recibido['archivo'] == '' or json_recibido['archivo'] == None:
            return Response({'success': False, 'detail': 'Ingrese archivo'}, status=status.HTTP_400_BAD_REQUEST)
    
        #VALIDAR LA EXISTENCIA DE LOS DATOS
        organigrama = Organigramas.objects.filter(~Q(fecha_terminado=None) & Q(fecha_retiro_produccion=None)).filter(id_organigrama = json_recibido['id_organigrama']).first()
        if not organigrama:
            return Response({'success': False, 'detail': 'El organigrama ingresado no se puede activar'}, status=status.HTTP_400_BAD_REQUEST)
        ccd = CuadrosClasificacionDocumental.objects.filter(~Q(fecha_terminado=None) & Q(fecha_retiro_produccion=None)).filter(id_ccd = json_recibido['id_ccd']).first()
        if not ccd:
            return Response({'success': False, 'detail': 'El CCD ingresado no se puede activar'}, status=status.HTTP_400_BAD_REQUEST)
        trd = TablaRetencionDocumental.objects.filter(~Q(fecha_terminado=None) & Q(fecha_retiro_produccion=None)).filter(id_trd = json_recibido['id_trd']).first()
        if not trd:
            return Response({'success': False, 'detail': 'La TRD ingresada no se puede activar'}, status=status.HTTP_400_BAD_REQUEST)
        #VALIDAR LA RELACION DE LA CCD CON EL ORGANIGRAMA, Y DE LA CCD CON LA TRD
        if ccd.id_organigrama.id_organigrama != organigrama.id_organigrama:
            return Response({'success': False, 'detail': 'El organigrama ingresado no tiene relación con el ccd ingresado'}, status=status.HTTP_400_BAD_REQUEST)
        if trd.id_ccd.id_ccd != ccd.id_ccd:
            return Response({'success': False, 'detail': 'El ccd ingresado no tiene relación con la trd ingresada'}, status=status.HTTP_400_BAD_REQUEST)        
        #CONSULTAR LA PREEXISTENCIA DE DE TABLAS ACTIVADAS
        trd_a_remplazar=TablaRetencionDocumental.objects.filter(actual=True).first()
        ccd_a_remplazar=CuadrosClasificacionDocumental.objects.filter(actual=True).first()
        organigrama_a_remplazar=Organigramas.objects.filter(actual=True).first()
        user_logeado = request.user.id_usuario
        dirip = Util.get_client_ip(request)
        previous_remplazante_trd=copy.copy(trd)
        previous_a_remplazar_trd=copy.copy(trd_a_remplazar)
        previous_remplazante_ccd=copy.copy(ccd)
        previous_a_remplazar_ccd=copy.copy(ccd_a_remplazar)
        previous_remplazante_org=copy.copy(organigrama)
        previous_a_remplazar_org=copy.copy(organigrama_a_remplazar)

        if trd_a_remplazar and ccd_a_remplazar and organigrama_a_remplazar:
            if organigrama.actual == True and ccd.actual == True and trd.actual == True:
                return Response({'success': False, 'detail': 'Esta combinación ya se encuentra activa'}, status=status.HTTP_400_BAD_REQUEST)
            if  organigrama.actual == False and ccd.actual == False and trd.actual == False:
                tipologias_trd = TipologiasDocumentales.objects.filter(id_trd=trd_a_remplazar.id_trd).values()
                id_tipologias_trd = [i['id_tipologia_documental'] for i in tipologias_trd]
                tipologias_usadas = SeriesSubSUnidadOrgTRDTipologias.objects.filter(id_tipologia_doc__in = id_tipologias_trd).values()
                id_tipologias_usadas = [i['id_tipologia_doc_id'] for i in tipologias_usadas]
                tipologias_sin_usar = TipologiasDocumentales.objects.filter(~Q(id_tipologia_documental__in = id_tipologias_usadas)).filter(id_trd=trd_a_remplazar.id_trd)
                if tipologias_sin_usar:
                    tipologias_sin_usar.delete()
                
                #unidades de personas desactivar
                unidades_utilizadas=UnidadesOrganizacionales.objects.filter(id_organigrama=organigrama_a_remplazar)
                unidades_list=[id.id_unidad_organizacional for id in unidades_utilizadas]
                persona_organigrama_a_remplazar=Personas.objects.filter(id_unidad_organizacional_actual__in=unidades_list)
                for object in persona_organigrama_a_remplazar:
                    object.es_unidad_organizacional_actual=False
                    object.save()
                    
                organigrama_a_remplazar.actual =  False
                organigrama.actual = True
                ccd_a_remplazar.actual = False
                ccd.actual = True
                trd_a_remplazar.actual = False
                trd.actual =True
                organigrama.fecha_puesta_produccion = datetime.now()
                ccd.fecha_puesta_produccion = datetime.now()
                trd.fecha_puesta_produccion = datetime.now()
                organigrama.justificacion_nueva_version = json_recibido['justificacion']
                ccd.justificacion = json_recibido['justificacion']
                trd.justificacion = json_recibido['justificacion']
                organigrama_a_remplazar.fecha_retiro_produccion = datetime.now()
                ccd_a_remplazar.fecha_retiro_produccion = datetime.now()
                trd_a_remplazar.fecha_retiro_produccion = datetime.now()
                organigrama.ruta_resolucion = json_recibido['archivo']
                ccd.ruta_soporte = json_recibido['archivo']
                trd.ruta_soporte = json_recibido['archivo']
                trd_a_remplazar.save()
                trd.save()
                ccd_a_remplazar.save()
                ccd.save()
                organigrama_a_remplazar.save()
                organigrama.save()

                #auditoria organigrama desactivado
                descripcion = {"nombre":str(organigrama_a_remplazar.nombre),"versión":str(organigrama_a_remplazar.version)}
                valores_actualizados={'previous':previous_a_remplazar_org, 'current':organigrama_a_remplazar}
                auditoria_data = {'id_usuario': user_logeado,'id_modulo': 16,'cod_permiso': 'AC','subsistema': 'TRSV','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
                Util.save_auditoria(auditoria_data)

                 #auditoria CCD desactivado
                descripcion = {"nombre":str(ccd_a_remplazar.nombre),"versión":str(ccd_a_remplazar.version)}
                valores_actualizados={'previous':previous_a_remplazar_ccd, 'current':ccd_a_remplazar}
                auditoria_data = {'id_usuario': user_logeado,'id_modulo': 28,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
                Util.save_auditoria(auditoria_data)

                 #auditoria TRD desactivado
                descripcion = {"nombre":str(trd_a_remplazar.nombre),"versión":str(trd_a_remplazar.version)}
                valores_actualizados={'previous':previous_a_remplazar_trd, 'current':trd_a_remplazar}
                auditoria_data = {'id_usuario': user_logeado,'id_modulo': 30,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
                Util.save_auditoria(auditoria_data)

                #auditoria organigrama activado
                descripcion = {"nombre":str(organigrama.nombre),"versión":str(organigrama.version)}
                valores_actualizados={'previous':previous_remplazante_org, 'current':organigrama}
                auditoria_data = {'id_usuario': user_logeado,'id_modulo': 16,'cod_permiso': 'AC','subsistema': 'TRSV','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
                Util.save_auditoria(auditoria_data)

                 #auditoria CCD activado
                descripcion = {"nombre":str(ccd.nombre),"versión":str(ccd.version)}
                valores_actualizados={'previous':previous_remplazante_ccd, 'current':ccd}
                auditoria_data = {'id_usuario': user_logeado,'id_modulo': 28,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
                Util.save_auditoria(auditoria_data)

                 #auditoria TRD activado
                descripcion = {"nombre":str(trd.nombre),"versión":str(trd.version)}
                valores_actualizados={'previous':previous_remplazante_trd, 'current':trd}
                auditoria_data = {'id_usuario': user_logeado,'id_modulo': 30,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
                Util.save_auditoria(auditoria_data)

                return Response({'success': True, 'detail': 'Activación exitosa'}, status=status.HTTP_201_CREATED)

            if organigrama.actual == True and ccd.actual == False and trd.actual == False:
                ccd_a_remplazar.actual = False
                ccd.actual = True
                trd_a_remplazar.actual = False
                trd.actual =True
                ccd.fecha_puesta_produccion = datetime.now()
                trd.fecha_puesta_produccion = datetime.now()
                ccd.justificacion = json_recibido['justificacion']
                trd.justificacion = json_recibido['justificacion']
                ccd_a_remplazar.fecha_retiro_produccion = datetime.now()
                trd_a_remplazar.fecha_retiro_produccion = datetime.now()
                ccd.ruta_soporte = json_recibido['archivo']
                trd.ruta_soporte = json_recibido['archivo']
                trd_a_remplazar.save()
                trd.save()
                ccd_a_remplazar.save()
                ccd.save()

                 #auditoria CCD desactivado
                descripcion = {"nombre":str(ccd_a_remplazar.nombre),"versión":str(ccd_a_remplazar.version)}
                valores_actualizados={'previous':previous_a_remplazar_ccd, 'current':ccd_a_remplazar}
                auditoria_data = {'id_usuario': user_logeado,'id_modulo': 28,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
                Util.save_auditoria(auditoria_data)

                 #auditoria TRD desactivado
                descripcion = {"nombre":str(trd_a_remplazar.nombre),"versión":str(trd_a_remplazar.version)}
                valores_actualizados={'previous':previous_a_remplazar_trd, 'current':trd_a_remplazar}
                auditoria_data = {'id_usuario': user_logeado,'id_modulo': 30,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
                Util.save_auditoria(auditoria_data)

                 #auditoria CCD activado
                descripcion = {"nombre":str(ccd.nombre),"versión":str(ccd.version)}
                valores_actualizados={'previous':previous_remplazante_ccd, 'current':ccd}
                auditoria_data = {'id_usuario': user_logeado,'id_modulo': 28,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
                Util.save_auditoria(auditoria_data)

                 #auditoria TRD activado
                descripcion = {"nombre":str(trd.nombre),"versión":str(trd.version)}
                valores_actualizados={'previous':previous_remplazante_trd, 'current':trd}
                auditoria_data = {'id_usuario': user_logeado,'id_modulo': 30,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
                Util.save_auditoria(auditoria_data)

                return Response({'success': True, 'detail': 'Activación exitosa'}, status=status.HTTP_201_CREATED)

            if organigrama.actual == True and ccd.actual == True and trd.actual == False:
                trd_a_remplazar.actual = False
                trd.actual =True
                trd.fecha_puesta_produccion = datetime.now()
                trd.justificacion = json_recibido['justificacion']
                trd_a_remplazar.fecha_retiro_produccion = datetime.now()
                trd.ruta_soporte = json_recibido['archivo']
                trd_a_remplazar.save()
                trd.save()

                 #auditoria TRD desactivado
                descripcion = {"nombre":str(trd_a_remplazar.nombre),"versión":str(trd_a_remplazar.version)}
                valores_actualizados={'previous':previous_a_remplazar_trd, 'current':trd_a_remplazar}
                auditoria_data = {'id_usuario': user_logeado,'id_modulo': 30,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
                Util.save_auditoria(auditoria_data)

                 #auditoria TRD activado
                descripcion = {"nombre":str(trd.nombre),"versión":str(trd.version)}
                valores_actualizados={'previous':previous_remplazante_trd, 'current':trd}
                auditoria_data = {'id_usuario': user_logeado,'id_modulo': 30,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
                Util.save_auditoria(auditoria_data)

                return Response({'success': True, 'detail': 'Activación exitosa'}, status=status.HTTP_201_CREATED)

            return Response({'success': False, 'detail': 'No se pudo llevar a cabo la activación. Contraste la información ingresada con la que está en la base de datos'}, status=status.HTTP_400_BAD_REQUEST)

        if (trd_a_remplazar == None) and (ccd_a_remplazar == None) and (organigrama_a_remplazar == None):
                organigrama.actual = True
                ccd.actual = True
                trd.actual =True
                organigrama.fecha_puesta_produccion = datetime.now()
                ccd.fecha_puesta_produccion = datetime.now()
                trd.fecha_puesta_produccion = datetime.now()
                organigrama.justificacion_nueva_version = json_recibido['justificacion']
                ccd.justificacion = json_recibido['justificacion']
                trd.justificacion = json_recibido['justificacion']
                organigrama.ruta_resolucion = json_recibido['archivo']
                ccd.ruta_soporte = json_recibido['archivo']
                trd.ruta_soporte = json_recibido['archivo']
                trd.save()
                ccd.save()
                organigrama.save()

                #auditoria organigrama activado
                descripcion = {"nombre":str(organigrama.nombre),"versión":str(organigrama.version)}
                valores_actualizados={'previous':previous_remplazante_org, 'current':organigrama}
                auditoria_data = {'id_usuario': user_logeado,'id_modulo': 16,'cod_permiso': 'AC','subsistema': 'TRSV','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
                Util.save_auditoria(auditoria_data)

                 #auditoria CCD activado
                descripcion = {"nombre":str(ccd.nombre),"versión":str(ccd.version)}
                valores_actualizados={'previous':previous_remplazante_ccd, 'current':ccd}
                auditoria_data = {'id_usuario': user_logeado,'id_modulo': 28,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
                Util.save_auditoria(auditoria_data)

                 #auditoria TRD activado
                descripcion = {"nombre":str(trd.nombre),"versión":str(trd.version)}
                valores_actualizados={'previous':previous_remplazante_trd, 'current':trd}
                auditoria_data = {'id_usuario': user_logeado,'id_modulo': 30,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
                Util.save_auditoria(auditoria_data)

                return Response({'success': True, 'detail': 'Activación exitosa'}, status=status.HTTP_201_CREATED)
        return Response({'success': False, 'detail': 'Error de base de datos'}, status=status.HTTP_400_BAD_REQUEST)


