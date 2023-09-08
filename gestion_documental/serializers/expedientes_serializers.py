from rest_framework import serializers
from rest_framework.serializers import ReadOnlyField
from django.db.models import F
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from django.db.models import Max 

from gestion_documental.models.expedientes_models import ExpedientesDocumentales,ArchivosDigitales,DocumentosDeArchivoExpediente,IndicesElectronicosExp,Docs_IndiceElectronicoExp,CierresReaperturasExpediente,ArchivosSoporte_CierreReapertura


######################### SERIALIZERS DEPOSITO #########################

#Buscar-Expediente
class ExpedienteSearchSerializer(serializers.ModelSerializer):
    
    class Meta:
        model =  ExpedientesDocumentales
        fields = '__all__'