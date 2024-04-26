from rest_framework import generics,status
from rest_framework.response import Response
from gestion_documental.models.ccd_models import CatalogosSeriesUnidad, CuadrosClasificacionDocumental
from gestion_documental.models.ctrl_acceso_models import CtrlAccesoClasificacionExpCCD
from gestion_documental.serializers.ctrl_acceso_serializers import CtrlAccesoCatUndPutSerializer, CtrlAccesoCodClasifPutSerializer, CtrlAccesoGetSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
import copy

from seguridad.permissions.permissions_gestor import PermisoActualizarControlAccesoClasificacionExpedientes, PermisoCrearControlAccesoClasificacionExpedientes
from seguridad.utils import Util

class CtrlAccesoGetView(generics.ListAPIView):
    serializer_class = CtrlAccesoGetSerializer 
    queryset = CtrlAccesoClasificacionExpCCD.objects.filter()
    permission_classes = [IsAuthenticated]

    def get(self, request):
        id_ccd = request.query_params.get('id_ccd', '')
        cod_clasificacion_exp = request.query_params.get('cod_clasificacion_exp', None)
        id_cat_serie_und = request.query_params.get('id_cat_serie_und', None)
        
        if id_ccd == '':
            raise ValidationError('Debe enviar el CCD seleccionado')
        
        if cod_clasificacion_exp:
            ctrl_acceso = self.queryset.filter(id_ccd=id_ccd, cod_clasificacion_exp=cod_clasificacion_exp)
        elif id_cat_serie_und:
            ctrl_acceso = self.queryset.filter(id_ccd=id_ccd, id_cat_serie_und_org_ccd=id_cat_serie_und)
        else:
            ctrl_acceso = self.queryset.filter(id_ccd=id_ccd)
        
        serializador = self.serializer_class(ctrl_acceso, many=True)
        
        return Response({'succes': True, 'detail':'Resultados encontrados', 'data':serializador.data}, status=status.HTTP_200_OK)

class CtrlAccesoPutView(generics.UpdateAPIView):
    serializer_class_cod_clasif = CtrlAccesoCodClasifPutSerializer
    serializer_class_cat_und = CtrlAccesoCatUndPutSerializer
    queryset = CtrlAccesoClasificacionExpCCD.objects.filter()
    permission_classes = [IsAuthenticated, (PermisoCrearControlAccesoClasificacionExpedientes|PermisoActualizarControlAccesoClasificacionExpedientes)]

    def put(self, request):
        data = request.data
        id_ccd = data['id_ccd']
        cod_clasificacion_exp = data['cod_clasificacion_exp']
        id_cat_serie_und_org_ccd = data['id_cat_serie_und_org_ccd']
        
        ccd_instance = CuadrosClasificacionDocumental.objects.filter(id_ccd=id_ccd).first()
        
        if not ccd_instance:
            raise ValidationError('Debe enviar un CCD que exista')
        
        if cod_clasificacion_exp and id_cat_serie_und_org_ccd:
            raise ValidationError('Solo debe seleccionar un tipo de configuración')
        
        # DATA AUDITORIA
        descripcion = {"NombreCCD": ccd_instance.nombre, "VersionCCD": ccd_instance.version}
        cod_permiso = 'CR'
        valores_actualizados = None
        usuario = request.user.id_usuario
        direccion=Util.get_client_ip(request)
        serializer = None
        
        if cod_clasificacion_exp:
            instance = self.queryset.filter(id_ccd=id_ccd, cod_clasificacion_exp=cod_clasificacion_exp).first()
            descripcion["ClasificacionExpediente"] = cod_clasificacion_exp
            if instance:
                cod_permiso = 'AC'
                valores_actualizados = {'previous':copy.copy(instance)}
                
                serializer = self.serializer_class_cod_clasif(instance, data=data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                
                valores_actualizados['current'] = instance
            else:
                serializer = self.serializer_class_cod_clasif(data=data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
        elif id_cat_serie_und_org_ccd:
            cat_serie_und_org_ccd_instance = CatalogosSeriesUnidad.objects.filter(id_cat_serie_und = id_cat_serie_und_org_ccd).first()
            if not cat_serie_und_org_ccd_instance:
                raise ValidationError("Debe elegir un registro del Catalogo de Serie-Subserie-Unidad existente")
            
            descripcion['NombreUnidad'] = cat_serie_und_org_ccd_instance.id_unidad_organizacional.nombre
            descripcion['NombreSerie'] = cat_serie_und_org_ccd_instance.id_catalogo_serie.id_serie_doc.nombre
            if cat_serie_und_org_ccd_instance.id_catalogo_serie.id_subserie_doc:
                descripcion['NombreSubserie'] = cat_serie_und_org_ccd_instance.id_catalogo_serie.id_subserie_doc.nombre
            
            # VALIDAR SI ESTÁN EN FALSE TODAS LAS OPCIONES PARA ELIMINAR O NO GUARDAR REGISTRO
            values_data = list(data.values())
            false_values = values_data.count(False)
            
            instance = self.queryset.filter(id_ccd=id_ccd, id_cat_serie_und_org_ccd=id_cat_serie_und_org_ccd).first()
            if instance:
                if false_values == 14:
                    cod_permiso = 'BO'
                    instance.delete()
                else:
                    cod_permiso = 'AC'
                    valores_actualizados = {'previous':copy.copy(instance)}
                    
                    serializer = self.serializer_class_cat_und(instance, data=data)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    
                    valores_actualizados['current'] = instance
            else:
                if false_values != 14:
                    serializer = self.serializer_class_cat_und(data=data)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
        
        # AUDITORIA
        auditoria_data = {
            'id_usuario': usuario,
            'id_modulo': 136,
            'cod_permiso': cod_permiso,
            'subsistema': 'GEST',
            'dirip': direccion,
            'descripcion': descripcion
        }
        
        if valores_actualizados:
            auditoria_data['valores_actualizados'] = valores_actualizados
        
        if cod_permiso != 'BO':
            Util.save_auditoria(auditoria_data)
        
        serializer_data = serializer.data if serializer else {}
        
        return Response({'succes': True, 'detail':'Se ha realizado el guardado correctamente', 'data':serializer_data}, status=status.HTTP_200_OK)