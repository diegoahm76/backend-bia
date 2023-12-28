from django.forms import model_to_dict
from rest_framework import serializers
from gestion_documental.models.ccd_models import SeriesDoc, SubseriesDoc
from gestion_documental.models.depositos_models import BandejaEstante, CajaBandeja, CarpetaCaja, Deposito, EstanteDeposito
from gestion_documental.models.expedientes_models import ExpedientesDocumentales

from gestion_documental.models.transferencias_documentales_models import TransferenciasDocumentales
from gestion_documental.models.trd_models import TablaRetencionDocumental
from transversal.models.organigrama_models import UnidadesOrganizacionales
from transversal.models.personas_models import Personas


class UnidadesOrganizacionalesSerializer(serializers.ModelSerializer):

    class Meta:
        model = UnidadesOrganizacionales
        fields = [
            'id_unidad_organizacional',
            'nombre'
        ]

class HistoricoTransferenciasSerializer(serializers.ModelSerializer):
    expediente = serializers.SerializerMethodField()
    nombre_completo_persona_transfirio = serializers.SerializerMethodField()
    nombre_tipo_transferencia = serializers.ReadOnlyField(source='get_cod_tipo_transferencia_display')
    nombre_serie = serializers.SerializerMethodField()
    nombre_subserie = serializers.SerializerMethodField()
    unidad_organizacional = serializers.SerializerMethodField()

    def get_expediente(self, obj):
        expediente = ExpedientesDocumentales.objects.all().filter(id_expediente_documental = obj.id_expedienteDoc_id).first()
        expediente_Serializer = ExpedienteSerializer(expediente).data
        return expediente_Serializer
    
    def get_nombre_completo_persona_transfirio(self, obj):
        persona = Personas.objects.filter(id_persona=obj.id_persona_transfirio_id).first()
        nombre_completo = None
        nombre_list = [persona.primer_nombre, persona.segundo_nombre, persona.primer_apellido, persona.segundo_apellido]
        nombre_completo = ' '.join(item for item in nombre_list if item is not None)
        return nombre_completo
    
    def get_nombre_serie(self, obj):
        nombre_serie = None
        if obj.id_serie_origen_id:
            serie = SeriesDoc.objects.all().filter(id_serie_doc = obj.id_serie_origen_id).first()
            nombre_serie = serie.nombre
        return nombre_serie
    
    def get_nombre_subserie(self, obj):
        nombre_subSerie = None
        if obj.id_subserie_origen_id:
            subSerie = SubseriesDoc.objects.all().filter(id_subserie_doc = obj.id_subserie_origen_id).first()
            nombre_subSerie = subSerie.nombre
        return nombre_subSerie
    
    def get_unidad_organizacional(self, obj):
        unidad_organizacional = UnidadesOrganizacionales.objects.all().filter(id_unidad_organizacional = obj.id_unidad_org_propietaria_id).first()
        return unidad_organizacional.nombre
    
    class Meta:
        model = TransferenciasDocumentales
        fields = '__all__'


class ExpedienteSerializer(serializers.ModelSerializer):
    codigo_completo = serializers.SerializerMethodField()
    nombre_trd_origen = serializers.SerializerMethodField()
    nombre_und_seccion_propietaria_serie = serializers.SerializerMethodField()
    nombre_serie_origen = serializers.SerializerMethodField()
    nombre_subserie_origen = serializers.SerializerMethodField()
    nombre_persona_titular_exp_complejo = serializers.SerializerMethodField()
    nombre_unidad_org_oficina_respon_original = serializers.SerializerMethodField()
    nombre_tipo_expediente = serializers.ReadOnlyField(source='get_cod_tipo_expediente_display')
    nombre_etapa_de_archivo_actual_exped = serializers.ReadOnlyField(source='get_cod_etapa_de_archivo_actual_exped_display')
    nombre_und_org_oficina_respon_actual = serializers.SerializerMethodField()
    nombre_estado = serializers.ReadOnlyField(source='get_estado_display')
    ubicacion_expediente = serializers.SerializerMethodField()

    def get_codigo_completo(self, obj):
        codigo_list = [obj.codigo_exp_und_serie_subserie, obj.codigo_exp_Agno, obj.codigo_exp_consec_por_agno]
        codigo_completo = '.'.join(str(item) for item in codigo_list if item is not None)
        return codigo_completo
    
    def get_nombre_trd_origen(self, obj):
        trd_origen = TablaRetencionDocumental.objects.all().filter(id_trd = obj.id_trd_origen_id).first()
        return trd_origen.nombre
    
    def get_nombre_und_seccion_propietaria_serie(self, obj):
        unidad_organizacional = UnidadesOrganizacionales.objects.all().filter(id_unidad_organizacional = obj.id_und_seccion_propietaria_serie_id).first()
        return unidad_organizacional.nombre
    
    def get_nombre_serie_origen(self, obj):
        nombre_serie = None
        if obj.id_serie_origen_id:
            serie = SeriesDoc.objects.all().filter(id_serie_doc = obj.id_serie_origen_id).first()
            nombre_serie = serie.nombre
        return nombre_serie
    
    def get_nombre_subserie_origen(self, obj):
        nombre_subSerie = None
        if obj.id_subserie_origen_id:
            subSerie = SubseriesDoc.objects.all().filter(id_subserie_doc = obj.id_subserie_origen_id).first()
            nombre_subSerie = subSerie.nombre
        return nombre_subSerie
    
    def get_nombre_persona_titular_exp_complejo(self, obj):
        nombre_completo = None
        if obj.id_persona_titular_exp_complejo_id:
            persona = Personas.objects.filter(id_persona=obj.id_persona_titular_exp_complejo_id).first()
            nombre_completo = None
            nombre_list = [persona.primer_nombre, persona.segundo_nombre, persona.primer_apellido, persona.segundo_apellido]
            nombre_completo = ' '.join(item for item in nombre_list if item is not None)
        
        return nombre_completo
    
    def get_nombre_unidad_org_oficina_respon_original(self, obj):
        unidad_organizacional = UnidadesOrganizacionales.objects.all().filter(id_unidad_organizacional = obj.id_unidad_org_oficina_respon_original_id).first()
        return unidad_organizacional.nombre

    def get_nombre_und_org_oficina_respon_actual(self, obj):
        unidad_organizacional = UnidadesOrganizacionales.objects.all().filter(id_unidad_organizacional = obj.id_und_org_oficina_respon_actual_id).first()
        return unidad_organizacional.nombre
    
    def get_ubicacion_expediente(self, obj):
        depositos = []
        carpetasCaja = CarpetaCaja.objects.all().filter(id_expediente = obj.id_expediente_documental)
        for carpetaCajaInstance in carpetasCaja:
            carpetaCaja = model_to_dict(carpetaCajaInstance)
            cajaBandeja = model_to_dict(CajaBandeja.objects.all().filter(id_caja_bandeja = carpetaCaja['id_caja_bandeja']).first())
            bandejaEstante = model_to_dict(BandejaEstante.objects.all().filter(id_bandeja_estante = cajaBandeja['id_bandeja_estante']).first())
            estanteDeposito = model_to_dict(EstanteDeposito.objects.all().filter(id_estante_deposito = bandejaEstante['id_estante_deposito']).first())
            deposito = model_to_dict(Deposito.objects.all().filter(id_deposito = estanteDeposito['id_deposito']).first())

            deposito_filtrado = next((item_deposito for item_deposito in depositos if item_deposito['id_deposito'] == deposito['id_deposito']), None)
            if deposito_filtrado is not None:
                indice_deposito = depositos.index(deposito_filtrado)
                estantes = depositos[indice_deposito]['estantes']
                estante_filtrado = next((item_estante for item_estante in estantes if item_estante.id_estante_deposito == estanteDeposito.id_estante_deposito), None)
                if estante_filtrado is not None:
                    indice_estante = depositos[indice_deposito]['estantes'].index(estante_filtrado)
                    bandejas = depositos[indice_deposito]['estantes'][indice_estante]['bandejas']
                    bandeja_filtrada = next((item_bandeja for item_bandeja in bandejas if item_bandeja.id_bandeja_estante == bandejaEstante.id_bandeja_estante), None)
                    if bandeja_filtrada is not None:
                        indice_bandeja = depositos[indice_deposito]['estantes'][indice_estante]['bandejas'].index(bandeja_filtrada)
                        cajas = depositos[indice_deposito]['estantes'][indice_estante]['bandejas'][indice_bandeja]['cajas']
                        caja_filtrada = next((item_caja for item_caja in cajas if item_caja.id_caja_bandeja == cajaBandeja.id_caja_bandeja), None)
                        if caja_filtrada is not None:
                            indice_caja = depositos[indice_deposito]['estantes'][indice_estante]['bandejas'][indice_bandeja]['cajas'].index(caja_filtrada)
                            depositos[indice_deposito]['estantes'][indice_estante]['bandejas'][indice_bandeja]['cajas'][indice_caja]['carpetas'].append(carpetaCaja)
                        else:
                            cajaBandeja['carpetas'] = [carpetaCaja]
                            depositos[indice_deposito]['estantes'][indice_estante]['bandejas'][indice_bandeja]['cajas'].append(cajaBandeja)
                    else:
                        cajaBandeja['carpetas'] = [carpetaCaja]
                        bandejaEstante['cajas'] = [cajaBandeja]
                        depositos[indice_deposito]['estantes'][indice_estante]['bandejas'].append(bandejaEstante)
                else:
                    cajaBandeja['carpetas'] = [carpetaCaja]
                    bandejaEstante['cajas'] = [cajaBandeja]
                    estanteDeposito['bandejas'] = [bandejaEstante]
                    depositos[indice_deposito]['estantes'].append(estanteDeposito)
            
            else:
                cajaBandeja['carpetas'] = [carpetaCaja]
                bandejaEstante['cajas'] = [cajaBandeja]
                estanteDeposito['bandejas'] = [bandejaEstante]
                deposito['estantes'] = [estanteDeposito]
                depositos.append(deposito)
        
        return depositos


    class Meta:
        model =  ExpedientesDocumentales
        fields = [
            'id_expediente_documental',
            'codigo_exp_und_serie_subserie',
            'codigo_exp_Agno',
            'codigo_exp_consec_por_agno',
            'codigo_completo',
            'titulo_expediente',
            'id_trd_origen',
            'nombre_trd_origen',
            'id_und_seccion_propietaria_serie',
            'nombre_und_seccion_propietaria_serie',
            'id_serie_origen',
            'nombre_serie_origen',
            'id_subserie_origen',
            'nombre_subserie_origen',
            'id_persona_titular_exp_complejo',
            'nombre_persona_titular_exp_complejo',
            'id_unidad_org_oficina_respon_original',
            'nombre_unidad_org_oficina_respon_original',
            'cod_tipo_expediente',
            'nombre_tipo_expediente',
            'cod_etapa_de_archivo_actual_exped',
            'nombre_etapa_de_archivo_actual_exped',
            'fecha_folio_inicial',
            'fecha_folio_final',
            'id_und_org_oficina_respon_actual',
            'nombre_und_org_oficina_respon_actual',
            'estado',
            'nombre_estado',
            'ubicacion_expediente'
        ]