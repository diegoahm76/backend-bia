from rest_framework import serializers
from gestion_documental.models.bandeja_tareas_models import ReasignacionesTareas, TareasAsignadas
from gestion_documental.models.expedientes_models import DobleVerificacionTmp
from gestion_documental.serializers.trd_serializers import ConsecutivoTipologiaDocTareasSerializer

from gestion_documental.models.radicados_models import AsignacionDocs, ConfigTiposRadicadoAgno, BandejaTareasPersona
from transversal.models.base_models import Departamento

from transversal.models.personas_models import Personas



class AsignacionDocsGetSerializer(serializers.ModelSerializer):
    persona_firmo = serializers.SerializerMethodField(default=None)

    def get_persona_firmo(self, obj):
        persona_firmo = None
        if obj.firma:
            doble_verificacion = DobleVerificacionTmp.objects.filter(id_persona_firma=obj.id_persona_asignada, id_consecutivo_tipologia=obj.id_consecutivo).first()
            if doble_verificacion:
                persona_firmo = True if doble_verificacion.verificacion_exitosa else False
        return persona_firmo

    class Meta:
        model = AsignacionDocs
        fields = '__all__'

class TareasAsignadasDocsGetSerializer(serializers.ModelSerializer):
   
    #cod_tipo_tarea es un choices
    tipo_tarea =serializers.ReadOnlyField(source='get_cod_tipo_tarea_display',default=None)
    asignado_por = serializers.SerializerMethodField()
    asignado_para = serializers.SerializerMethodField()
    asignaciones = serializers.SerializerMethodField()
    consecutivo = serializers.SerializerMethodField()
    fecha_consecutivo = serializers.SerializerMethodField()    #persona_genera = serializers.SerializerMethodField()
    radicado = serializers.SerializerMethodField(default=None)
    fecha_radicado =  serializers.SerializerMethodField(default=None)
    
    estado_tarea = serializers.ReadOnlyField(source='get_cod_estado_solicitud_display',default=None)
    estado_asignacion_tarea = serializers.ReadOnlyField(source='get_cod_estado_asignacion_display',default=None)#cod_estado_solicitud
    documento = serializers.SerializerMethodField(default=None)
    # respondida_por = serializers.ReadOnlyField(source='nombre_persona_que_responde',default=None)

    class Meta:#
        model = TareasAsignadas
        fields = '__all__'
        #fields = ['id_tarea_asignada','tipo_tarea','asignado_por','asignado_para', 'consecutivo', 'asignaciones', 'fecha_consecutivo', 'radicado', 'fecha_radicado','fecha_asignacion','comentario_asignacion','radicado','fecha_radicado','estado_tarea','estado_asignacion_tarea','unidad_org_destino','estado_reasignacion_tarea', 'documento', 'tarea_reasignada_a','id_tarea_asignada_padre_inmediata']
        
    def get_asignaciones(self,obj):
        asignaciones = AsignacionDocs.objects.filter(id_asignacion_doc=obj.id_asignacion).first()
        return AsignacionDocsGetSerializer(asignaciones).data

    def get_fecha_consecutivo(self,obj):
        tarea = obj
        documento = None

        if tarea.id_asignacion:
                asignacion = AsignacionDocs.objects.filter(id_asignacion_doc=tarea.id_asignacion).first()
                documento = asignacion.id_consecutivo
        else:

            while tarea:
                tarea = tarea.id_tarea_asignada_padre_inmediata

                if tarea.id_asignacion:
                    asignacion = AsignacionDocs.objects.filter(id_asignacion_doc=tarea.id_asignacion).first()

                    documento = asignacion.id_consecutivo
                    break

        cadena = ""
        if  documento:
            cadena = documento.fecha_consecutivo

        return cadena


    def get_documento(self,obj):
        #buscamos la asignacion
        
      
           
        tarea = obj
        documento = None

        if tarea.id_asignacion:
                asignacion = AsignacionDocs.objects.filter(id_asignacion_doc=tarea.id_asignacion).first()
                documento = asignacion.id_consecutivo
        else:

            while tarea:
                tarea = tarea.id_tarea_asignada_padre_inmediata

                if tarea.id_asignacion:
                    asignacion = AsignacionDocs.objects.filter(id_asignacion_doc=tarea.id_asignacion).first()

                    documento = asignacion.id_consecutivo
                    break
        if not documento:
            return None
        return ConsecutivoTipologiaDocTareasSerializer(documento).data
    
    def get_consecutivo(self,obj):
        tarea = obj
        documento = None
        if tarea.id_asignacion:
                asignacion = AsignacionDocs.objects.filter(id_asignacion_doc=tarea.id_asignacion).first()
                documento = asignacion.id_consecutivo
        else:

            while tarea:
                tarea = tarea.id_tarea_asignada_padre_inmediata

                if tarea.id_asignacion:
                    asignacion = AsignacionDocs.objects.filter(id_asignacion_doc=tarea.id_asignacion).first()

                    documento = asignacion.id_consecutivo
                    break

        cadena = ""
        if  documento:
            if documento.CatalogosSeriesUnidad:
                cadena = f"{documento.prefijo_consecutivo}.{documento.id_unidad_organizacional.codigo}.{documento.CatalogosSeriesUnidad.id_catalogo_serie.id_serie_doc.codigo}.{documento.CatalogosSeriesUnidad.id_catalogo_serie.id_subserie_doc.codigo}.{documento.agno_consecutivo}.{documento.nro_consecutivo}"
            else:
                cadena= f"{documento.prefijo_consecutivo}.{documento.id_unidad_organizacional.codigo}.{documento.agno_consecutivo}.{documento.nro_consecutivo}"
        
        return cadena
    
    
    def get_asignado_por(self,obj):
        #buscamos la asignacion
        tarea = obj
    
        if tarea.id_asignacion:
                tarea = obj
        else:
            while not  tarea.id_asignacion:
                tarea = tarea.id_tarea_asignada_padre_inmediata
                if tarea.id_asignacion:
             
                    break
             
        persona = None
        asignacion_tarea = AsignacionDocs.objects.filter(id_asignacion_doc=tarea.id_asignacion).first()

        if not asignacion_tarea:
            return None

        if not tarea:
            return None
        persona = asignacion_tarea.id_persona_asigna
        nombre_completo = None
        nombre_list = [persona.primer_nombre, persona.segundo_nombre,
                        persona.primer_apellido, persona.segundo_apellido]
        nombre_completo = ' '.join(item for item in nombre_list if item is not None)
        nombre_completo = nombre_completo if nombre_completo != "" else None
        return nombre_completo
    
    def get_asignado_para(self,obj):
        #buscamos la asignacion
        tarea = obj
    
        if tarea.id_asignacion:
                tarea = obj
        else:
            while not  tarea.id_asignacion:
                tarea = tarea.id_tarea_asignada_padre_inmediata
                if tarea.id_asignacion:
             
                    break
             
        persona = None
        asignacion_tarea = AsignacionDocs.objects.filter(id_asignacion_doc=tarea.id_asignacion).first()

        if not asignacion_tarea:
            return None

        if not tarea:
            return None
        persona = asignacion_tarea.id_persona_asignada
        nombre_completo = None
        nombre_list = [persona.primer_nombre, persona.segundo_nombre,
                        persona.primer_apellido, persona.segundo_apellido]
        nombre_completo = ' '.join(item for item in nombre_list if item is not None)
        nombre_completo = nombre_completo if nombre_completo != "" else None
        return nombre_completo
    

    def get_radicado(self,obj):
        #buscamos la asignacion
        
      
           
        tarea = obj
        documento = None

        if tarea.id_asignacion:
                asignacion = AsignacionDocs.objects.filter(id_asignacion_doc=tarea.id_asignacion).first()
                documento = asignacion.id_consecutivo
        else:

            while tarea:
                tarea = tarea.id_tarea_asignada_padre_inmediata

                if tarea.id_asignacion:
                    asignacion = AsignacionDocs.objects.filter(id_asignacion_doc=tarea.id_asignacion).first()

                    documento = asignacion.id_consecutivo
                    break


            
        # print("PQRSDF")
        # print(pqrsdf)
        cadena = ""
        if  documento and documento.id_radicado:
            instance_config_tipo_radicado = ConfigTiposRadicadoAgno.objects.filter(agno_radicado=documento.id_radicado.agno_radicado,cod_tipo_radicado=documento.id_radicado.cod_tipo_radicado).first()
            numero_con_ceros = str(documento.id_radicado.nro_radicado).zfill(instance_config_tipo_radicado.cantidad_digitos)
            cadena= instance_config_tipo_radicado.prefijo_consecutivo+'-'+str(instance_config_tipo_radicado.agno_radicado)+'-'+numero_con_ceros
        
        return cadena

    def get_fecha_radicado(self,obj):
        #buscamos la asignacion
        
      
           
        tarea = obj
        documento = None

        if tarea.id_asignacion:
                asignacion = AsignacionDocs.objects.filter(id_asignacion_doc=tarea.id_asignacion).first()
                documento = asignacion.id_consecutivo
        else:

            while tarea:
                tarea = tarea.id_tarea_asignada_padre_inmediata

                if tarea.id_asignacion:
                    asignacion = AsignacionDocs.objects.filter(id_asignacion_doc=tarea.id_asignacion).first()

                    documento = asignacion.id_consecutivo
                    break
        if not documento:
            return None
        return documento.fecha_radicado      

        





class TareasAsignadasOotrosUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TareasAsignadas
        fields = '__all__'

class AsignacionDocsPostSerializer(serializers.ModelSerializer):
    persona_asginada = serializers.SerializerMethodField()
    persona_asigna = serializers.SerializerMethodField()
    unidad_organizacional_asignada = serializers.ReadOnlyField(source='id_persona_asignada.id_unidad_organizacional_actual.nombre',default=None)
    class Meta:
        model = AsignacionDocs
        fields = '__all__'

    def get_persona_asginada(self,obj):
        persona = obj.id_persona_asignada
        nombre_completo = None
        nombre_list = [persona.primer_nombre, persona.segundo_nombre,
                        persona.primer_apellido, persona.segundo_apellido]
        nombre_completo = ' '.join(item for item in nombre_list if item is not None)
        nombre_completo = nombre_completo if nombre_completo != "" else None
        return nombre_completo
    
    def get_persona_asigna(self,obj):
        persona = obj.id_persona_asigna
        nombre_completo = None
        nombre_list = [persona.primer_nombre, persona.segundo_nombre,
                        persona.primer_apellido, persona.segundo_apellido]
        nombre_completo = ' '.join(item for item in nombre_list if item is not None)
        nombre_completo = nombre_completo if nombre_completo != "" else None
        return nombre_completo
    

class PersonasBandejaSerializer(serializers.ModelSerializer):
    nombre_unidad_organizacional_actual=serializers.ReadOnlyField(source='id_unidad_organizacional_actual.nombre',default=None)
    tiene_usuario = serializers.SerializerMethodField()
    primer_nombre = serializers.SerializerMethodField()
    segundo_nombre = serializers.SerializerMethodField()
    primer_apellido = serializers.SerializerMethodField()
    segundo_apellido = serializers.SerializerMethodField()
    cod_departamento_expedicion = serializers.ReadOnlyField(source='cod_municipio_expedicion_id.cod_departamento.cod_departamento',default=None)
    cod_departamento_residencia = serializers.SerializerMethodField()
    cod_departamento_notificacion = serializers.SerializerMethodField()
    cod_departamento_laboral = serializers.SerializerMethodField()
    tiene_bandeja = serializers.SerializerMethodField()

    def get_tiene_usuario(self, obj):
        bandeja = BandejaTareasPersona.objects.filter(id_persona=obj.id_persona).exists()   
        return bandeja
    
    def get_cod_departamento_residencia(self, obj):
        cod_departamento_residencia = None
        departamento = Departamento.objects.filter(cod_departamento=obj.municipio_residencia.cod_municipio[:2]).first() if obj.municipio_residencia else None
        if departamento:
            cod_departamento_residencia = departamento.cod_departamento
        return cod_departamento_residencia
    
    def get_cod_departamento_notificacion(self, obj):
        cod_departamento_notificacion = None
        departamento = Departamento.objects.filter(cod_departamento=obj.cod_municipio_notificacion_nal.cod_municipio[:2]).first() if obj.cod_municipio_notificacion_nal else None
        if departamento:
            cod_departamento_notificacion = departamento.cod_departamento
        return cod_departamento_notificacion
    
    def get_cod_departamento_laboral(self, obj):
        cod_departamento_laboral = None
        departamento = Departamento.objects.filter(cod_departamento=obj.cod_municipio_laboral_nal.cod_municipio[:2]).first() if obj.cod_municipio_laboral_nal else None
        if departamento:
            cod_departamento_laboral = departamento.cod_departamento
        return cod_departamento_laboral
    
    # def get_tiene_usuario(self, obj):
    #    usuario = User.objects.filter(persona=obj.id_persona).exists()   
     #   return usuario
    
    def get_primer_nombre(self, obj):
        primer_nombre2 = obj.primer_nombre
        primer_nombre2 = primer_nombre2.upper() if primer_nombre2 else primer_nombre2
        return primer_nombre2
    
    def get_segundo_nombre(self, obj):
        segundo_nombre2 = obj.segundo_nombre
        segundo_nombre2 = segundo_nombre2.upper() if segundo_nombre2 else segundo_nombre2
        return segundo_nombre2
    
    def get_primer_apellido(self, obj):
        primer_apellido2 = obj.primer_apellido
        primer_apellido2 = primer_apellido2.upper() if primer_apellido2 else primer_apellido2
        return primer_apellido2
        
    def get_segundo_apellido(self, obj):
        segundo_apellido2 = obj.segundo_apellido
        segundo_apellido2 = segundo_apellido2.upper() if segundo_apellido2 else segundo_apellido2
        return segundo_apellido2
    
    #MOSTRAR EL NOMBRE EN MAYUSCULA
        
    class Meta:
        model = Personas
        fields = '__all__'
        fields = ['id', 'tien_bandeja']
