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
from transversal.models.personas_models import Personas
from gestion_documental.models.tca_models import TablasControlAcceso
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from gestion_documental.serializers.trd_serializers import (
    TRDSerializer,
    FormatosTiposMedioSerializer,
    TipologiasDoc
)
from gestion_documental.serializers.tca_serializers import (
    TCASerializer
)
from gestion_documental.serializers.ccd_serializers import (
    CCDPosiblesSerializer,
    CCDSerializer
)

from gestion_documental.models.ccd_models import (
    CuadrosClasificacionDocumental,
)
from transversal.models.organigrama_models import (
    Organigramas,
    UnidadesOrganizacionales
    
)
from gestion_documental.models.trd_models import (
    TablaRetencionDocumental,
    TipologiasDoc,
    SeriesSubSUnidadOrgTRDTipologias,
    FormatosTiposMedio
)
from gestion_documental.models.tca_models import (
    TablasControlAcceso
)

class GetCCDPosiblesActivar(generics.ListAPIView):
    serializer_class = CCDPosiblesSerializer
    queryset = CuadrosClasificacionDocumental.objects.filter(fecha_retiro_produccion=None, actual=False).exclude(fecha_terminado=None)

    def get(self, request):
        id_organigrama = request.query_params.get('id_organigrama')
        
        ccd_posibles = []
        
        ccd_queryset = self.queryset.filter(id_organigrama__actual=True) if not id_organigrama else self.queryset.filter(id_organigrama=id_organigrama)
        
        for ccd in ccd_queryset:
            trd = ccd.tablaretenciondocumental
            tca = trd.tablascontrolacceso
            
            if tca:
                ccd_posibles.append(ccd)
        
        serializer = self.serializer_class(ccd_posibles, many=True)
            
        return Response({'success':True, 'detail':'Los CCD posibles que se pueden activar son los siguientes', 'data': serializer.data}, status=status.HTTP_200_OK)

class GetCCDTerminadoByORG(generics.ListAPIView):
    serializer_class = CCDSerializer
    queryset = CuadrosClasificacionDocumental.objects.filter(~Q(fecha_terminado = None) & Q(fecha_retiro_produccion=None))

    def get(self, request, id_organigrama):
        orgamigrama = Organigramas.objects.filter(id_organigrama = id_organigrama).first()
        if not orgamigrama:
            raise NotFound('El organigrama ingresado no existe')

        if orgamigrama.fecha_terminado == None or orgamigrama.fecha_retiro_produccion != None:
            raise PermissionDenied('El organigrama ingresado ya está retirado o no está terminado')
        ccds = CuadrosClasificacionDocumental.objects.filter(~Q(fecha_terminado = None) & Q(fecha_retiro_produccion=None)).filter(id_organigrama = int(orgamigrama.id_organigrama)).values()
        return Response({'success':True, 'detail':'CCD', 'data': ccds}, status=status.HTTP_200_OK)

class GetTRDTerminadoByCCD(generics.ListAPIView):
    serializer_class = TRDSerializer
    queryset = TablaRetencionDocumental.objects.filter(~Q(fecha_terminado = None) & Q(fecha_retiro_produccion=None))

    def get(self, request, id_ccd):
        ccd = CuadrosClasificacionDocumental.objects.filter(id_ccd = id_ccd).first()
        if not ccd:
            raise NotFound('El ccd ingresado no existe')

        if ccd.fecha_terminado == None or ccd.fecha_retiro_produccion != None:
            raise PermissionDenied('El ccd ingresado ya está retirado o no está terminado')
        trds = TablaRetencionDocumental.objects.filter(~Q(fecha_terminado = None) & Q(fecha_retiro_produccion=None)).filter(id_ccd = int(ccd.id_ccd)).values()
        return Response({'success':True, 'detail':'TRD', 'data': trds}, status=status.HTTP_200_OK)
    
class GetTCATerminadoByCCD(generics.ListAPIView):
    serializer_class = TCASerializer
    queryset = TablasControlAcceso.objects.filter(~Q(fecha_terminado = None) & Q(fecha_retiro_produccion=None))

    def get(self, request, id_ccd):
        ccd = CuadrosClasificacionDocumental.objects.filter(id_ccd = id_ccd).first()
        if not ccd:
            raise NotFound('El ccd ingresado no existe')

        if ccd.fecha_terminado == None or ccd.fecha_retiro_produccion != None:
            raise PermissionDenied('El ccd ingresado ya está retirado o no está terminado')
        tca = TablasControlAcceso.objects.filter(~Q(fecha_terminado = None) & Q(fecha_retiro_produccion=None)).filter(id_ccd = int(ccd.id_ccd)).values()
        return Response({'success':True, 'detail':'TCA', 'data': tca}, status=status.HTTP_200_OK)

class Activar(generics.UpdateAPIView):
    serializer_class =TRDSerializer
    queryset=TablaRetencionDocumental.objects.all()
    permission_classes = [IsAuthenticated]
    
    def put(self,request):
        data = request.data
        if not data.get('id_ccd'):
            raise ValidationError('Ingrese cuadro de clasificación documental')
        if not data.get('justificacion') or data.get('justificacion') == '':
            raise ValidationError('Ingrese justificación')
    
        #VALIDAR LA EXISTENCIA DE LOS DATOS
        ccd = CuadrosClasificacionDocumental.objects.filter(~Q(fecha_terminado=None) & Q(fecha_retiro_produccion=None)).filter(id_ccd = data['id_ccd']).first()
        if not ccd:
            raise ValidationError('El CCD ingresado no se puede activar porque no se encuentra terminado o ya fue retirado de producción')
        elif not ccd.id_organigrama.actual:
            raise ValidationError('No puede activar el CCD elegido porque no está basado en el organigrama actual')
        
        trd = ccd.tablaretenciondocumental
        if not trd or (not trd.fecha_terminado or trd.fecha_retiro_produccion) :
            raise ValidationError('La TRD asociada a la CCD no se encuentra terminada o ya fue retirado de producción')
        
        tca = trd.tablascontrolacceso
        if not tca or (not tca.fecha_terminado or tca.fecha_retiro_produccion):
            raise ValidationError('La TCA asociada a la TRD no se encuentra terminada o ya fue retirado de producción')
              
        #CONSULTAR LA PREEXISTENCIA DE DE TABLAS ACTIVADAS
        tca_a_remplazar=TablasControlAcceso.objects.filter(actual=True).first()
        trd_a_remplazar=TablaRetencionDocumental.objects.filter(actual=True).first()
        ccd_a_remplazar=CuadrosClasificacionDocumental.objects.filter(actual=True).first()

        user_logeado = request.user.id_usuario
        dirip = Util.get_client_ip(request)
        previous_remplazante_tca=copy.copy(tca)
        previous_a_remplazar_tca=copy.copy(tca_a_remplazar)
        previous_remplazante_trd=copy.copy(trd)
        previous_a_remplazar_trd=copy.copy(trd_a_remplazar)
        previous_remplazante_ccd=copy.copy(ccd)
        previous_a_remplazar_ccd=copy.copy(ccd_a_remplazar)

        if ccd_a_remplazar and trd_a_remplazar and tca_a_remplazar:
            if ccd.actual == True:
                raise ValidationError('No puede activar los instrumentos archivisticos asociados a un CCD ya activo')
            
            if ccd.actual == False and trd.actual == False and tca.actual == False:
                ccd_a_remplazar.actual = False
                ccd.actual = True
                trd_a_remplazar.actual = False
                trd.actual =True
                tca_a_remplazar.actual=False
                tca.actual= True
                
                ccd.fecha_puesta_produccion = datetime.now()
                trd.fecha_puesta_produccion = datetime.now()
                tca.fecha_puesta_produccion = datetime.now()
                
                ccd.justificacion = data['justificacion']
                
                ccd_a_remplazar.fecha_retiro_produccion = datetime.now()
                trd_a_remplazar.fecha_retiro_produccion = datetime.now()
                tca_a_remplazar.fecha_retiro_produccion = datetime.now()
                
                ccd_a_remplazar.save()
                ccd.save()
                trd_a_remplazar.save()
                trd.save()
                tca_a_remplazar.save()
                tca.save()

                #auditoria CCD desactivado
                descripcion = {"NombreCCD":str(ccd_a_remplazar.nombre),"VersionCCD":str(ccd_a_remplazar.version)}
                valores_actualizados={'previous':previous_a_remplazar_ccd, 'current':ccd_a_remplazar}
                auditoria_data = {'id_usuario': user_logeado,'id_modulo': 27,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
                Util.save_auditoria(auditoria_data)

                #auditoria TRD desactivado
                descripcion = {"NombreTRD":str(trd_a_remplazar.nombre),"VersionTRD":str(trd_a_remplazar.version)}
                valores_actualizados={'previous':previous_a_remplazar_trd, 'current':trd_a_remplazar}
                auditoria_data = {'id_usuario': user_logeado,'id_modulo': 29,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
                Util.save_auditoria(auditoria_data)
                
                #auditoria TCA desactivado
                descripcion = {"NombreTCA":str(tca_a_remplazar.nombre),"VersionTCA":str(tca_a_remplazar.version)}
                valores_actualizados={'previous':previous_a_remplazar_tca, 'current':tca_a_remplazar}
                auditoria_data = {'id_usuario': user_logeado,'id_modulo': 31,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
                Util.save_auditoria(auditoria_data)

                #auditoria CCD activado
                descripcion = {"NombreCCD":str(ccd.nombre),"VersionCCD":str(ccd.version)}
                valores_actualizados={'previous':previous_remplazante_ccd, 'current':ccd}
                auditoria_data = {'id_usuario': user_logeado,'id_modulo': 27,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
                Util.save_auditoria(auditoria_data)

                #auditoria TRD activado
                descripcion = {"NombreTRD":str(trd.nombre),"VersionTRD":str(trd.version)}
                valores_actualizados={'previous':previous_remplazante_trd, 'current':trd}
                auditoria_data = {'id_usuario': user_logeado,'id_modulo': 29,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
                Util.save_auditoria(auditoria_data)
                
                #auditoria TCA activado
                descripcion = {"NombreTCA":str(tca.nombre),"VersionTCA":str(tca.version)}
                valores_actualizados={'previous':previous_remplazante_tca, 'current':tca}
                auditoria_data = {'id_usuario': user_logeado,'id_modulo': 31,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
                Util.save_auditoria(auditoria_data)

                return Response({'success':True, 'detail':'Activación exitosa'}, status=status.HTTP_201_CREATED)

        if not ccd_a_remplazar and not trd_a_remplazar and not tca_a_remplazar:
            ccd.actual = True
            trd.actual =True
            tca.actual = True
            
            ccd.fecha_puesta_produccion = datetime.now()
            trd.fecha_puesta_produccion = datetime.now()
            tca.fecha_puesta_produccion = datetime.now()
            
            ccd.justificacion = data['justificacion']
            
            tca.save()
            trd.save()
            ccd.save()

            #auditoria CCD activado
            descripcion = {"NombreCCD":str(ccd.nombre),"VersionCCD":str(ccd.version)}
            valores_actualizados={'previous':previous_remplazante_ccd, 'current':ccd}
            auditoria_data = {'id_usuario': user_logeado,'id_modulo': 27,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
            Util.save_auditoria(auditoria_data)

            #auditoria TRD activado
            descripcion = {"NombreTRD":str(trd.nombre),"VersionTRD":str(trd.version)}
            valores_actualizados={'previous':previous_remplazante_trd, 'current':trd}
            auditoria_data = {'id_usuario': user_logeado,'id_modulo': 29,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
            Util.save_auditoria(auditoria_data)
            
            #auditoria TCA activado
            descripcion = {"NombreTCA":str(tca.nombre),"VersionTCA":str(tca.version)}
            valores_actualizados={'previous':previous_remplazante_tca, 'current':tca}
            auditoria_data = {'id_usuario': user_logeado,'id_modulo': 31,'cod_permiso': 'AC','subsistema': 'GEST','dirip': dirip, 'descripcion': descripcion,'valores_actualizados': valores_actualizados}
            Util.save_auditoria(auditoria_data)

            return Response({'success':True, 'detail':'Activación exitosa'}, status=status.HTTP_201_CREATED)
        
        else:
            raise ValidationError('Debe garantizar que el CCD elegido tenga asociado una TRD y una TCA ya terminados')