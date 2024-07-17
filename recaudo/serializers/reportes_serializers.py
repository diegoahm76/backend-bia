from rest_framework import serializers
from recaudo.models.cobros_models import Cartera, ConceptoContable
from recaudo.models.liquidaciones_models import Deudores
from recaudo.models.facilidades_pagos_models import DetallesFacilidadPago, FacilidadesPago
from recaudo.models.base_models import RangosEdad
from gestion_documental.models import ExpedientesDocumentales
from recaudo.models import extraccion_model_recaudo , Rt970Tramite



# class CarteraGeneralSerializer(serializers.ModelSerializer):
#     valor_sancion = serializers.DecimalField(max_digits=30, decimal_places=2, source='calcular_valor_total')
#     concepto_deuda = serializers.SerializerMethodField()
    
#     def get_concepto_deuda(self, obj):
#         return obj.codigo_contable.descripcion

#     class Meta:
#         model = Cartera
#         fields = ('codigo_contable', 'concepto_deuda', 'valor_sancion')


class CarteraGeneralSerializer(serializers.ModelSerializer):
    valor_sancion = serializers.SerializerMethodField()
    concepto_deuda = serializers.ReadOnlyField(source='descripcion', default=None)

    def get_valor_sancion(self, obj):
        fecha_corte = self.context.get('fecha_corte_s')
        carteras = Cartera.objects.filter(codigo_contable=obj.id).filter(fin=fecha_corte)
        monto_total = sum(cartera.monto_inicial for cartera in carteras)
        intereses_total = sum(cartera.valor_intereses for cartera in carteras)
        valor_sancion = monto_total + intereses_total
        return valor_sancion
    
    class Meta:
        model = ConceptoContable
        fields = ('id','codigo_contable', 'concepto_deuda', 'valor_sancion')




class CarteraGeneralDetalleSerializer(serializers.ModelSerializer):
    valor_sancion = serializers.DecimalField(max_digits=30, decimal_places=2, source='calcular_valor_total')
    nombre_deudor = serializers.SerializerMethodField()
    identificacion = serializers.SerializerMethodField()
    expediente = serializers.SerializerMethodField()
    resolucion = serializers.SerializerMethodField()
    auto = serializers.SerializerMethodField()
    recurso = serializers.SerializerMethodField()
    codigo_contable = serializers.ReadOnlyField(source='codigo_contable.codigo_contable')
    concepto_deuda = serializers.ReadOnlyField(source='codigo_contable.descripcion')

    def get_nombre_deudor(self, obj):
        if obj.id_deudor.id_persona_deudor:
            if obj.id_deudor.id_persona_deudor.razon_social:
                nombre_completo = obj.id_deudor.id_persona_deudor.razon_social
            else:
                nombre_completo = ' '.join(filter(None, [obj.id_deudor.id_persona_deudor.primer_nombre, obj.id_deudor.id_persona_deudor.segundo_nombre, obj.id_deudor.id_persona_deudor.primer_apellido, obj.id_deudor.id_persona_deudor.segundo_apellido]))
            return nombre_completo
        elif obj.id_deudor.id_persona_deudor_pymisis:
            return f"{obj.id_deudor.id_persona_deudor_pymisis.t03nombre}"
        else:
            return None
        
    def get_identificacion(self, obj):
        if obj.id_deudor.id_persona_deudor:
            return obj.id_deudor.id_persona_deudor.numero_documento
        elif obj.id_deudor.id_persona_deudor_pymisis:
            return obj.id_deudor.id_persona_deudor_pymisis.t03nit
        else:
            return None
    
    def get_expediente(self, obj):
        expediente_doc = obj.id_expediente.id_expediente_doc
        if expediente_doc:
            codigo_exp = f"{expediente_doc.codigo_exp_und_serie_subserie}{expediente_doc.codigo_exp_Agno}{expediente_doc.codigo_exp_consec_por_agno}"
            return codigo_exp
        else:
            expediente_pimisys = obj.id_expediente.id_expediente_pimisys
            if expediente_pimisys:
                return expediente_pimisys.t920codexpediente
            else:
                return None

    def get_resolucion(self, obj):
        expediente_doc = obj.id_expediente.id_expediente_doc
        if expediente_doc:
            codigo_exp = f"{expediente_doc.codigo_exp_und_serie_subserie}{expediente_doc.codigo_exp_Agno}{expediente_doc.codigo_exp_consec_por_agno}"
            return codigo_exp
        else:
            expediente_pimisys = obj.id_expediente.id_expediente_pimisys
            if expediente_pimisys:
                tramite = Rt970Tramite.objects.filter(t970codexpediente=expediente_pimisys.t920codexpediente).first()
                if tramite:
                    return tramite.t970numresolperm
                else:
                    return None
            else:
                return None
            
    
    def get_auto(self, obj):
        expediente_doc = obj.id_expediente.id_expediente_doc
        return expediente_doc.cod_auto if expediente_doc else None
    
    def get_recurso(self, obj):
        expediente_doc = obj.id_expediente.id_expediente_doc
        return expediente_doc.cod_recurso if expediente_doc else None
     
    class Meta:
        model = Cartera
        fields = ('id','codigo_contable', 'concepto_deuda', 'identificacion', 'nombre_deudor', 'numero_factura', 'expediente', 'resolucion', 'auto', 'recurso', 'valor_sancion')




class CarteraEdadesSerializer(serializers.ModelSerializer):
    valor_sancion = serializers.DecimalField(max_digits=30, decimal_places=2, source='calcular_valor_total')
    nombre_deudor = serializers.ReadOnlyField()
    identificacion = serializers.SerializerMethodField()
    expediente = serializers.SerializerMethodField()
    resolucion = serializers.SerializerMethodField()

    def get_identificacion(self, obj):
        try:
            deudor = Deudores.objects.get(id=obj.id_deudor.id)
            return f"{deudor.identificacion}"
        except Deudores.DoesNotExist:
            return None
        
    def get_expediente(self, obj):
        expediente = obj.id_expediente
        return expediente.cod_expediente if expediente else None

    def get_resolucion(self, obj):
        resolucion = obj.id_expediente.numero_resolucion
        return resolucion if resolucion else None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        try:
            deudor = Deudores.objects.get(id=instance.id_deudor.id)
            representation['nombre_deudor'] = f"{deudor.nombres} {deudor.apellidos}"
        except Deudores.DoesNotExist:
            representation['nombre_deudor'] = None
        return representation

    class Meta:
        model = Cartera
        fields = ('identificacion', 'nombre_deudor', 'expediente', 'resolucion', 'id_rango', 'valor_sancion')

class ReporteFacilidadesPagosSerializer(serializers.ModelSerializer):
    total_sanciones_coactivo = serializers.DecimalField(max_digits=30, decimal_places=2)
    total_sanciones_persuasivo = serializers.DecimalField(max_digits=30, decimal_places=2)
    total_general = serializers.DecimalField(max_digits=30, decimal_places=2)

    class Meta:
        model = DetallesFacilidadPago
        fields = ('total_sanciones_coactivo','total_sanciones_persuasivo','total_general')

class ReporteFacilidadesPagosDetalleSerializer(serializers.ModelSerializer):
    tipo_cobro = serializers.CharField()
    identificacion = serializers.CharField()
    nombre_deudor = serializers.CharField()
    cod_expediente = serializers.CharField()
    numero_resolucion = serializers.CharField()
    numero_factura = serializers.CharField()
    valor_sancion = serializers.DecimalField(max_digits=30, decimal_places=2)
    concepto_deuda = serializers.CharField()

    class Meta:
        model = DetallesFacilidadPago
        fields = ('tipo_cobro', 'identificacion', 'nombre_deudor', 'concepto_deuda','cod_expediente', 'numero_resolucion',
                  'numero_factura', 'valor_sancion')
        

class RangosEdadSerializer(serializers.ModelSerializer):
    class Meta:
        model = RangosEdad
        fields = '__all__'

class CarteraSerializer(serializers.ModelSerializer):
    codigo_contable__descripcion = serializers.CharField(source='codigo_contable.descripcion', read_only=True)
    class Meta:
        model = Cartera
        fields = '__all__'

class CarteraDeudaYEtapaSerializer(serializers.ModelSerializer):
    codigo_contable__descripcion = serializers.CharField(source='codigo_contable.descripcion', read_only=True)
    codigo_contable_valor = serializers.CharField(source='codigo_contable.codigo_contable', read_only=True)
    etapa = serializers.SerializerMethodField()
    class Meta:
        model = Cartera
        fields = '__all__'

    def get_etapa(self, obj):
        etapa= None
        proceso_cartera = obj.procesos_set.first()
        if proceso_cartera:
            etapa = proceso_cartera.id_etapa.etapa
        return etapa


class ConceptoContableSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConceptoContable
        fields = '__all__'

class DeudorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Deudores
        fields = '__all__'

class DeudorSumSerializer(serializers.ModelSerializer):
    total_sancion = serializers.DecimalField(max_digits=30, decimal_places=2)
    identificacion = serializers.SerializerMethodField()
    nombres = serializers.SerializerMethodField()
    telefono = serializers.SerializerMethodField()
    direccion = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    fecha_nacimiento = serializers.SerializerMethodField()


    class Meta:
        model = Deudores
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['total_sancion'] = instance.total_sancion
        return representation
    
    def get_nombres(self, obj):
        if obj.id_persona_deudor:
            if obj.id_persona_deudor.razon_social:
                nombre_completo = obj.id_persona_deudor.razon_social
            else:
                nombre_completo = ' '.join(filter(None, [obj.id_persona_deudor.primer_nombre, obj.id_persona_deudor.segundo_nombre, obj.id_persona_deudor.primer_apellido, obj.id_persona_deudor.segundo_apellido]))
            return nombre_completo
        elif obj.id_persona_deudor_pymisis:
            return f"{obj.id_persona_deudor_pymisis.t03nombre}"
        else:
            return None

    def get_identificacion(self, obj):
        if obj.id_persona_deudor:
            return obj.id_persona_deudor.numero_documento
        elif obj.id_persona_deudor_pymisis:
            return obj.id_persona_deudor_pymisis.t03nit
        else:
            return None
        
    def get_telefono(self, obj):
        if obj.id_persona_deudor:
            return obj.id_persona_deudor.telefono_celular
        elif obj.id_persona_deudor:
            return obj.id_persona_deudor.telefono_empresa
        elif obj.id_persona_deudor_pymisis:
            return obj.id_persona_deudor_pymisis.t03telefono
        else:
            return None
        
    def get_direccion(self, obj):
        if obj.id_persona_deudor:
            return obj.id_persona_deudor.direccion_residencia
        elif obj.id_persona_deudor_pymisis:
            return obj.id_persona_deudor_pymisis.t03direccion
        else:
            return None
        
    def get_email(self, obj):
        if obj.id_persona_deudor:
            return obj.id_persona_deudor.email
        elif obj.id_persona_deudor:
            return obj.id_persona_deudor.email_empresarial
        elif obj.id_persona_deudor_pymisis:
            return obj.id_persona_deudor_pymisis.t03email
        else:
            return None
        
    def get_fecha_nacimiento(self, obj):
        if obj.id_persona_deudor:
            return obj.id_persona_deudor.fecha_nacimiento
        elif obj.id_persona_deudor_pymisis:
            return obj.id_persona_deudor_pymisis.t03fechanacimiento
        else:
            return None
    
    
