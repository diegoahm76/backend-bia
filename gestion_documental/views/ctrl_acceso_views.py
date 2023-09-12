from rest_framework import generics,status
from rest_framework.response import Response
from gestion_documental.models.ctrl_acceso_models import CtrlAccesoClasificacionExpCCD
from gestion_documental.serializers.ctrl_acceso_serializers import CtrlAccesoCatUndPutSerializer, CtrlAccesoCodClasifPutSerializer, CtrlAccesoGetSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied

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
    permission_classes = [IsAuthenticated]

    def put(self, request):
        data = request.data
        id_ccd = data['id_ccd']
        cod_clasificacion_exp = data['cod_clasificacion_exp']
        id_cat_serie_und_org_ccd = data['id_cat_serie_und_org_ccd']
        
        if cod_clasificacion_exp and id_cat_serie_und_org_ccd:
            raise ValidationError('Solo debe seleccionar un tipo de configuración')
        
        if cod_clasificacion_exp:
            instance = self.queryset.filter(id_ccd=id_ccd, cod_clasificacion_exp=cod_clasificacion_exp).first()
            if instance:
                serializer = self.serializer_class_cod_clasif(instance, data=data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
            else:
                serializer = self.serializer_class_cod_clasif(data=data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
        elif id_cat_serie_und_org_ccd:
            # VALIDAR SI ESTÁN EN FALSE TODAS LAS OPCIONES PARA ELIMINAR O NO GUARDAR REGISTRO
            values_data = list(data.values())
            false_values = values_data.count(False)
            
            instance = self.queryset.filter(id_ccd=id_ccd, id_cat_serie_und_org_ccd=id_cat_serie_und_org_ccd).first()
            if instance:
                if false_values == 14:
                    instance.delete()
                
                serializer = self.serializer_class_cod_clasif(instance, data=data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
            else:
                if false_values != 14:
                    serializer = self.serializer_class_cod_clasif(data=data)
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
        
        return Response({'succes': True, 'detail':'Se ha realizado el guardado correctamente', 'data':serializer.data}, status=status.HTTP_200_OK)