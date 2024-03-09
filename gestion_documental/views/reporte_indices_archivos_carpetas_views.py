from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response
from gestion_documental.models.expedientes_models import  ExpedientesDocumentales




from rest_framework.exceptions import ValidationError,NotFound,PermissionDenied
import os
from rest_framework.permissions import IsAuthenticated

from gestion_documental.serializers.reporte_indices_archivos_carpetas_serializers import ReporteIndicesTodosGetSerializer






class ReporteIndicesTodosGet(generics.ListAPIView):
    serializer_class = ReporteIndicesTodosGetSerializer
    queryset = ExpedientesDocumentales.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get(self,request):
        
        intance =ExpedientesDocumentales.objects.all()
        print(len(intance))

        intance =ExpedientesDocumentales.objects.filter(estado='A')
        print(len(intance))
        intance =ExpedientesDocumentales.objects.filter(estado='C')
        print(len(intance))
        serializador = self.serializer_class(intance,many=True)
        
        return Response({'success':True,'detail':'Se encontraron los siguientes registros.','data':serializador.data},status=status.HTTP_200_OK)
        
