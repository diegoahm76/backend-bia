from rest_framework import serializers
from unittest.util import _MAX_LENGTH
from wsgiref.validate import validator
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
from almacen.models.hoja_de_vida_models import HojaDeVidaComputadores, HojaDeVidaOtrosActivos, HojaDeVidaVehiculos, DocumentosVehiculo
from transversal.models.base_models import Municipio, ApoderadoPersona, ClasesTerceroPersona, Personas
from almacen.models.vehiculos_models import  InspeccionesVehiculosDia, PersonasSolicitudViaje, VehiculosAgendables_Conductor, VehiculosArrendados, Marcas, ViajesAgendados,BitacoraViaje



from almacen.models.vehiculos_models import (
    PeriodoArriendoVehiculo,
    VehiculosAgendadosDiaDisponible,
    VehiculosArrendados,
    VehiculosAgendables_Conductor,
    SolicitudesViajes
    # ViajesAgendados
    )

class RegistrarVehiculoArrendadoSerializer(serializers.ModelSerializer):
    nombre_marca = serializers.ReadOnlyField(source='id_marca.nombre')
    id_hoja_de_vida = serializers.SerializerMethodField()

    class Meta:
        model = VehiculosArrendados
        fields = ['id_vehiculo_arrendado', 'nombre', 'descripcion', 'placa', 'nombre_marca', 'empresa_contratista', 'tiene_hoja_de_vida', 'id_marca','id_hoja_de_vida']
        extra_kwargs = {
            'id_marca': {'required': False}
        }
    
    #fk-pk
    def get_id_hoja_de_vida(self, obj):
        id_hoja_de_vida = obj.hojadevidavehiculos_set.first()
        id_hoja_de_vida = id_hoja_de_vida.id_hoja_de_vida if id_hoja_de_vida else None
        
        return id_hoja_de_vida


class ActualizarVehiculoArrendadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehiculosArrendados
        fields = ['descripcion','id_marca','empresa_contratista']
        
class VehiculosAgendablesConductorSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehiculosAgendables_Conductor
        fields = '__all__'
        # Excluir el campo id_persona_que_asigna de la lista de campos requeridos
        extra_kwargs = {
            'id_persona_que_asigna': {'required': False},
            'activo': {'required': False, 'default': True}  
            
        }

class PeriodoVehiculoArrendadoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodoArriendoVehiculo
        fields = '__all__'
        
class CrearAgendaVehiculoDiaSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehiculosAgendadosDiaDisponible
        fields = '__all__'
class UpdateArrendarVehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodoArriendoVehiculo
        fields = ['id_vehiculo_arrendado','fecha_fin']


class SolicitudViajeSerializer(serializers.ModelSerializer):
    cod_departamento = serializers.ReadOnlyField(source='cod_municipio.cod_departamento.cod_departamento')
    nombre_persona_solicita = serializers.SerializerMethodField()
    nombre_persona_responsable = serializers.SerializerMethodField()

    class Meta:
        model = SolicitudesViajes
        fields = '__all__'


    def get_nombre_persona_solicita(self, obj):
        nombre_persona_solicita = None
        if obj.id_persona_solicita:
            nombre_list = [obj.id_persona_solicita.primer_nombre, obj.id_persona_solicita.segundo_nombre,
                            obj.id_persona_solicita.primer_apellido, obj.id_persona_solicita.segundo_apellido]
            nombre_persona_solicita = ' '.join(item for item in nombre_list if item is not None)
            nombre_persona_solicita = nombre_persona_solicita if nombre_persona_solicita != "" else None
        return nombre_persona_solicita
    
    def get_nombre_persona_responsable(self, obj):
        nombre_persona_responsable = None
        if obj.id_persona_responsable:
            nombre_list = [obj.id_persona_responsable.primer_nombre, obj.id_persona_responsable.segundo_nombre,
                            obj.id_persona_responsable.primer_apellido, obj.id_persona_responsable.segundo_apellido]
            nombre_persona_responsable = ' '.join(item for item in nombre_list if item is not None)
            nombre_persona_responsable = nombre_persona_responsable if nombre_persona_responsable != "" else None
        return nombre_persona_responsable

class HojaDeVidaVehiculosSerializer(serializers.ModelSerializer):
    placa = serializers.SerializerMethodField()
    marca = serializers.SerializerMethodField()
    nombre = serializers.SerializerMethodField()
    asignable = serializers.SerializerMethodField()
    tipo_vehiculo = serializers.CharField(source='get_cod_tipo_vehiculo_display', default= None)


    class Meta:
        model = HojaDeVidaVehiculos
        fields = '__all__'

    def get_placa(self, obj):
        placa = None
        if obj.es_arrendado:
            placa = obj.id_vehiculo_arrendado.placa
        else:
            placa = obj.id_articulo.doc_identificador_nro
        
        return placa
    
    def get_marca(self, obj):
        marca = None
        if obj.es_arrendado:
            marca = obj.id_vehiculo_arrendado.id_marca.nombre
        else:
            marca = obj.id_articulo.id_marca.nombre

        return marca    
    
    def get_nombre(self, obj):
        nombre = None
        if obj.es_arrendado:
            nombre = obj.id_vehiculo_arrendado.nombre
        else:
            nombre = obj.id_articulo.nombre
        
        return nombre
    
    def get_asignable(self, obj):
        asignable = True
        vehiculos_asignables = obj.vehiculosagendables_conductor_set.all()
        if vehiculos_asignables:
            asignable = False if vehiculos_asignables.filter(activo=True).first() else True 
        return asignable


class ClaseTerceroPersonaSerializer(serializers.ModelSerializer):
    tipo_documento = serializers.ReadOnlyField(source='id_persona.tipo_documento.cod_tipo_documento', default=None)
    numero_documento = serializers.ReadOnlyField(source='id_persona.numero_documento', default=None)
    email = serializers.ReadOnlyField(source='id_persona.email', default=None)
    email_empresarial = serializers.ReadOnlyField(source='id_persona.email_empresarial', default=None)
    telefono_empresa = serializers.ReadOnlyField(source='id_persona.telefono_empresa', default=None)
    telefono_celular = serializers.ReadOnlyField(source='id_persona.telefono_celular', default=None)
    fecha_nacimiento = serializers.ReadOnlyField(source='id_persona.fecha_nacimiento', default=None)
    asignable = serializers.SerializerMethodField()
    nombre_clase_tercero = serializers.ReadOnlyField(source='id_clase_tercero.nombre', default=None)
    nombre_persona = serializers.SerializerMethodField()
    class Meta:
        model = ClasesTerceroPersona
        fields = '__all__'

    def get_asignable(self, obj):
        asignable = True
        conductores_asignables = obj.id_persona.T072id_persona_conductor.all()
        if conductores_asignables:
            asignable = False if conductores_asignables.filter(activo=True).first() else True 
        return asignable
    
    def get_nombre_persona(self, obj):
        nombre_persona = None
        if obj.id_persona:
            nombre_list = [obj.id_persona.primer_nombre, obj.id_persona.segundo_nombre,
                            obj.id_persona.primer_apellido, obj.id_persona.segundo_apellido]
            nombre_persona = ' '.join(item for item in nombre_list if item is not None)
            nombre_persona = nombre_persona if nombre_persona != "" else None
        return nombre_persona

class AsignacionVehiculoSerializer(serializers.ModelSerializer):
    tipo_vehiculo = serializers.CharField(source='id_hoja_vida_vehiculo.cod_tipo_vehiculo')
    marca = serializers.SerializerMethodField()
    placa = serializers.SerializerMethodField()
    tipo_conductor = serializers.SerializerMethodField()
    nombre_conductor = serializers.SerializerMethodField()
    nro_documento_conductor = serializers.CharField(source='id_persona_conductor.numero_documento')
    id_asignacion = serializers.IntegerField(source='id_vehiculo_conductor')  

    class Meta:
        model = VehiculosAgendables_Conductor
        fields = '__all__'

    def get_tipo_conductor(self, obj):
        # Verificar si el conductor es interno o externo
        clases_tercero_persona = ClasesTerceroPersona.objects.filter(id_persona=obj.id_persona_conductor)
        for ctp in clases_tercero_persona:
            if ctp.id_clase_tercero.nombre == "Conductor":
                return "Interno"
            elif ctp.id_clase_tercero.nombre == "Conductor Externo":
                return "Externo"
        return None

    def get_nombre_conductor(self, obj):
        return f"{obj.id_persona_conductor.primer_nombre} {obj.id_persona_conductor.primer_apellido}"

    def get_marca(self, obj):
        if obj.id_hoja_vida_vehiculo.id_vehiculo_arrendado:
            return obj.id_hoja_vida_vehiculo.id_vehiculo_arrendado.id_marca.nombre
        return None

    def get_placa(self, obj):
        if obj.id_hoja_vida_vehiculo.id_vehiculo_arrendado:
            return obj.id_hoja_vida_vehiculo.id_vehiculo_arrendado.placa
        return None

    


class PutSolicitudViajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SolicitudesViajes
        fields = ['motivo_viaje',
                  'cod_municipio', 
                  'tiene_expediente_asociado', 
                  'id_expediente_asociado', 
                  'direccion', 'nro_pasajeros', 
                  'fecha_partida', 'hora_partida', 
                  'fecha_retorno', 
                  'hora_retorno', 
                  'requiere_compagnia_militar',
                  'requiere_carga', 
                  'consideraciones_adicionales', 
                  'indicaciones_destino', 
                  'estado_solicitud']
        extra_kwargs = {
            'fecha_solicitud': {'required': False},
            'estado_solicitud': {'required': False},
            'id_persona_solicita': {'required': False},
            'id_unidad_org_solicita': {'required': False},
        }


class VehiculoConductorSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehiculosAgendables_Conductor
        fields = '__all__'

class BusquedaVehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = HojaDeVidaVehiculos
        fields = '__all__'

    
class VehiculoPersonaLogueadaSerializer(serializers.ModelSerializer):
    marca = serializers.SerializerMethodField()
    contratista = serializers.CharField(source='id_hoja_vida_vehiculo.id_vehiculo_arrendado.empresa_contratista', read_only=True)
    placa = serializers.CharField(source='id_hoja_vida_vehiculo.id_vehiculo_arrendado.placa', read_only=True)

    class Meta:
        model = VehiculosAgendables_Conductor
        fields = ['id_vehiculo_conductor', 'id_hoja_vida_vehiculo', 'id_persona_conductor', 'marca', 'contratista', 'placa']

    def get_marca(self, obj):
        if obj.id_hoja_vida_vehiculo.id_vehiculo_arrendado:
            return obj.id_hoja_vida_vehiculo.id_vehiculo_arrendado.id_marca.nombre
        return None

    def to_representation(self, instance):
        persona_logueada = self.context['request'].user.persona
        vehiculos_asociados = VehiculosAgendables_Conductor.objects.filter(id_persona_conductor=persona_logueada)
        serialized_data = []
        for vehiculo in vehiculos_asociados:
            vehiculo_data = {
                'id_vehiculo_conductor': vehiculo.id_vehiculo_conductor,
                'id_hoja_vida_vehiculo': vehiculo.id_hoja_vida_vehiculo.id_hoja_de_vida,
                'id_persona_conductor': vehiculo.id_persona_conductor.id_persona,
                'marca': self.get_marca(vehiculo),
                'contratista': vehiculo.id_hoja_vida_vehiculo.id_vehiculo_arrendado.empresa_contratista if vehiculo.id_hoja_vida_vehiculo.id_vehiculo_arrendado else None,
                'placa': vehiculo.id_hoja_vida_vehiculo.id_vehiculo_arrendado.placa if vehiculo.id_hoja_vida_vehiculo.id_vehiculo_arrendado else None
            }
            serialized_data.append(vehiculo_data)
        return serialized_data


class InspeccionesVehiculosDiaCreateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = InspeccionesVehiculosDia
        fields = '__all__'
        extra_kwargs = {
            'dia_inspeccion': {'required': False},
            'fecha_registro': {'required': False},
            'id_persona_inspecciona': {'required': False},
            'observaciones': {'required': False},
        }

    
    def validate(self, data):
        # Realizamos las validaciones personalizadas

        # Si es_agendable no está presente o es True, no se actualiza el kilometraje ni la fecha
        if 'es_agendable' in data and not data['es_agendable']:
            # Si el vehículo no es agendable, actualizamos el kilometraje y la fecha solo para vehículos NO arrendados
            hoja_de_vida_vehiculo = data.get('id_hoja_vida_vehiculo')
            if hoja_de_vida_vehiculo and not hoja_de_vida_vehiculo.id_vehiculo_arrendado:
                # Actualizamos el kilometraje y la fecha
                hoja_de_vida_vehiculo.ultimo_kilometraje = data.get('kilometraje')
                hoja_de_vida_vehiculo.fecha_ultimo_kilometraje = data.get('dia_inspeccion')
                hoja_de_vida_vehiculo.save()

        # Verificamos si algún elemento de la inspección está mal
        campos_booleanos = [
            'dir_llantas_delanteras', 'dir_llantas_traseras', 'limpiabrisas_delantero',
            'limpiabrisas_traseros', 'nivel_aceite', 'estado_frenos', 'nivel_refrigerante',
            'apoyo_cabezas_piloto', 'apoyo_cabezas_copiloto', 'apoyo_cabezas_traseros',
            'frenos_generales', 'freno_emergencia', 'llantas_delanteras', 'llantas_traseras',
            'llanta_repuesto', 'espejos_laterales', 'espejo_retrovisor', 'cinturon_seguridad_delantero',
            'cinturon_seguridad_trasero', 'luces_altas', 'luces_media', 'luces_bajas', 'luces_parada',
            'luces_parqueo', 'luces_reversa', 'kit_herramientas', 'botiquin_completo', 'pito'
        ]

        if any(data.get(campo) == False for campo in campos_booleanos):
            # Si algún elemento está mal, marcamos el atributo requiere_verificacion como True
            data['requiere_verificacion'] = True

            # Si algún elemento está mal, se permite adjuntar una observación
            if 'observaciones' not in data or not data['observaciones']:
                raise serializers.ValidationError("Se requiere una observación debido a que hay elementos de inspección que están mal")

        # Si no hay elementos de inspección malos, requiere_verificacion se establece en False
        else:
            data['requiere_verificacion'] = False

        # verificacion_superior_realizada se establece en False por defecto
        data['verificacion_superior_realizada'] = False

        return data
    


class InspeccionVehiculoSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspeccionesVehiculosDia
        fields = '__all__'


class BusquedaSolicitudViajeSerializer(serializers.ModelSerializer):
    nombre_solicitante = serializers.SerializerMethodField()
    nombre_municipio = serializers.SerializerMethodField()

    class Meta:
        model = SolicitudesViajes
        fields = '__all__'

    def get_nombre_solicitante(self, obj):
        # Combinar el primer nombre y el primer apellido del solicitante
        return f"{obj.id_persona_solicita.primer_nombre} {obj.id_persona_solicita.primer_apellido}"

    def get_nombre_municipio(self, obj):
        # Obtener el nombre del municipio
        return obj.cod_municipio.nombre
    


class ViajesAgendadosSerializer(serializers.ModelSerializer):
    nombre_conductor = serializers.ReadOnlyField(source='id_vehiculo_conductor.id_persona_conductor.primer_nombre', default=None)
    apellido_conductor = serializers.ReadOnlyField(source='id_vehiculo_conductor.id_persona_conductor.primer_apellido', default=None)

    class Meta:
        model = ViajesAgendados
        fields = '__all__'




class ViajesAgendadosSolcitudSerializer(serializers.ModelSerializer):
    nombre_conductor = serializers.ReadOnlyField(source='id_vehiculo_conductor.id_persona_conductor.primer_nombre', default=None)
    apellido_conductor = serializers.ReadOnlyField(source='id_vehiculo_conductor.id_persona_conductor.primer_apellido', default=None)
    fecha_nacimiento = serializers.ReadOnlyField(source='id_vehiculo_conductor.id_persona_conductor.fecha_nacimiento', default=None)
    telefono_celular = serializers.ReadOnlyField(source='id_vehiculo_conductor.id_persona_conductor.telefono_celular', default=None)
    telefono_celular_empresa = serializers.ReadOnlyField(source='id_vehiculo_conductor.id_persona_conductor.telefono_celular_empresa', default=None)
    email = serializers.ReadOnlyField(source='id_vehiculo_conductor.id_persona_conductor.email', default=None)
    email_empresarial = serializers.ReadOnlyField(source='id_vehiculo_conductor.id_persona_conductor.email_empresarial', default=None)
    tipo_documento = serializers.SerializerMethodField()
    numero_documento = serializers.SerializerMethodField()
    placa = serializers.SerializerMethodField()
    marca = serializers.SerializerMethodField()
    nombre = serializers.SerializerMethodField()
    nombre_persona_autoriza = serializers.SerializerMethodField()

    class Meta:
        model = ViajesAgendados
        fields = '__all__'

    def get_tipo_documento(self, obj):
        tipo_documento_nombre = None
        tipo_documento_obj = obj.id_vehiculo_conductor.id_persona_conductor.tipo_documento
        if tipo_documento_obj:
            tipo_documento_nombre = tipo_documento_obj.nombre
        return tipo_documento_nombre

    
    def get_numero_documento(self, obj):
        numero_documento_nombre = None
        numero_documento_obj = obj.id_vehiculo_conductor.id_persona_conductor.numero_documento
        if numero_documento_obj:
            numero_documento_nombre = numero_documento_obj
        return numero_documento_nombre


    def get_placa(self, obj):
        placa = None
        if obj.id_vehiculo_conductor.id_hoja_vida_vehiculo.es_arrendado:
            placa = obj.id_vehiculo_conductor.id_hoja_vida_vehiculo.id_vehiculo_arrendado.placa
        else:
            placa = obj.id_vehiculo_conductor.id_hoja_vida_vehiculo.id_articulo.doc_identificador_nro
        
        return placa
    
    def get_marca(self, obj):
        marca = None
        if obj.id_vehiculo_conductor.id_hoja_vida_vehiculo.es_arrendado:
            marca = obj.id_vehiculo_conductor.id_hoja_vida_vehiculo.id_vehiculo_arrendado.id_marca.nombre
        else:
            marca = obj.id_vehiculo_conductor.id_hoja_vida_vehiculo.id_articulo.id_marca.nombre

        return marca    
    
    def get_nombre(self, obj):
        nombre = None
        if obj.id_vehiculo_conductor.id_hoja_vida_vehiculo.es_arrendado:
            nombre = obj.id_vehiculo_conductor.id_hoja_vida_vehiculo.id_vehiculo_arrendado.nombre
        else:
            nombre = obj.id_vehiculo_conductor.id_hoja_vida_vehiculo.id_articulo.nombre
        
        return nombre
    
    def get_nombre_persona_autoriza(self, obj):
        nombre_persona_autoriza = None
        if obj.id_persona_autoriza:
            nombre_list = [obj.id_persona_autoriza.primer_nombre, obj.id_persona_autoriza.segundo_nombre,
                            obj.id_persona_autoriza.primer_apellido, obj.id_persona_autoriza.segundo_apellido]
            nombre_persona_autoriza = ' '.join(item for item in nombre_list if item is not None)
            nombre_persona_autoriza = nombre_persona_autoriza if nombre_persona_autoriza != "" else None
        return nombre_persona_autoriza
    
    
    


class ViajesAgendadosPorIDSerializer(serializers.ModelSerializer):
    nombre_conductor = serializers.ReadOnlyField(source='id_vehiculo_conductor.id_persona_conductor.primer_nombre', default=None)
    apellido_conductor = serializers.ReadOnlyField(source='id_vehiculo_conductor.id_persona_conductor.primer_apellido', default=None)
    placa = serializers.SerializerMethodField()
    marca = serializers.SerializerMethodField()
    nombre = serializers.SerializerMethodField()
    class Meta:
        model = ViajesAgendados
        fields = '__all__'

    def get_placa(self, obj):
        placa = None
        if obj.id_vehiculo_conductor.id_hoja_vida_vehiculo.es_arrendado:
            placa = obj.id_vehiculo_conductor.id_hoja_vida_vehiculo.id_vehiculo_arrendado.placa
        else:
            placa = obj.id_vehiculo_conductor.id_hoja_vida_vehiculo.id_articulo.doc_identificador_nro
        
        return placa
    
    def get_marca(self, obj):
        marca = None
        if obj.id_vehiculo_conductor.id_hoja_vida_vehiculo.es_arrendado:
            marca = obj.id_vehiculo_conductor.id_hoja_vida_vehiculo.id_vehiculo_arrendado.id_marca.nombre
        else:
            marca = obj.id_vehiculo_conductor.id_hoja_vida_vehiculo.id_articulo.id_marca.nombre

        return marca    
    
    def get_nombre(self, obj):
        nombre = None
        if obj.id_vehiculo_conductor.id_hoja_vida_vehiculo.es_arrendado:
            nombre = obj.id_vehiculo_conductor.id_hoja_vida_vehiculo.id_vehiculo_arrendado.nombre
        else:
            nombre = obj.id_vehiculo_conductor.id_hoja_vida_vehiculo.id_articulo.nombre
        
        return nombre
    
        



        
class BusquedaVehiculosGRLSerializer(serializers.ModelSerializer):
    nombre_marca = serializers.ReadOnlyField(source='id_marca.nombre')
    conductor = serializers.SerializerMethodField()
    tiene_platon = serializers.SerializerMethodField()
    es_arrendado = serializers.BooleanField(source='id_vehiculo_arrendado', default=False)
    
    class Meta:
        model = HojaDeVidaVehiculos
        fields = ['id_vehiculo_arrendado', 'nombre', 'descripcion', 'placa', 'nombre_marca', 'empresa_contratista', 'tiene_hoja_de_vida', 'id_marca', 'conductor', 'tiene_platon', 'es_arrendado']
        extra_kwargs = {
            'id_marca': {'required': False}
        }
    
    def get_conductor(self, obj):
        # Verificar si es un vehículo arrendado
        if obj.id_vehiculo_arrendado:
            vehiculo_agendable_conductor = obj.id_vehiculo_arrendado
            if vehiculo_agendable_conductor:
                return vehiculo_agendable_conductor.id_persona_conductor.nombre_completo
        # Verificar si es un vehículo propio arrendado
        elif obj.id_articulo:
            vehiculo_agendable_conductor = HojaDeVidaVehiculos.objects.filter(id_vehiculo_arrendado=None, id_articulo=obj.id_articulo).first()
            if vehiculo_agendable_conductor:
                return vehiculo_agendable_conductor.id_persona_conductor.nombre_completo
        return None

    def get_tiene_platon(self, obj):
        # Verificar si es un vehículo arrendado
        if obj.id_vehiculo_arrendado:
            vehiculo_agendable_conductor = obj.id_vehiculo_arrendado
            if vehiculo_agendable_conductor:
                return vehiculo_agendable_conductor.tiene_platon
        # Verificar si es un vehículo propio arrendado
        elif obj.id_articulo:
            vehiculo_agendable_conductor = HojaDeVidaVehiculos.objects.filter(id_vehiculo_arrendado=None, id_articulo=obj.id_articulo).first()
            if vehiculo_agendable_conductor:
                return vehiculo_agendable_conductor.tiene_platon
        return None
    


class VehiculosArrendadosSerializer(serializers.ModelSerializer):
    class Meta:
        model = VehiculosArrendados
        fields = '__all__'  


class BusquedaAvanzadaGRLSerializer(serializers.ModelSerializer):
    # id_vehiculo_arrendado = serializers.SerializerMethodField()
    id_vehiculo_arrendado = serializers.ReadOnlyField(source='id_hoja_vida_vehiculo.id_vehiculo_arrendado.id_vehiculo_arrendado', default=None)
    id_articulo = serializers.ReadOnlyField(source='id_hoja_vida_vehiculo.id_articulo.id_bien', default=None)
    tiene_platon = serializers.ReadOnlyField(source='id_hoja_vida_vehiculo.tiene_platon', default=None)
    es_arrendado = serializers.ReadOnlyField(source='id_hoja_vida_vehiculo.es_arrendado', default=None)
    placa = serializers.SerializerMethodField()
    nombre = serializers.SerializerMethodField()
    marca = serializers.SerializerMethodField()
    id_marca = serializers.SerializerMethodField()
    empresa_contratista = serializers.SerializerMethodField()
    persona_conductor = serializers.SerializerMethodField()

    class Meta:
        model = VehiculosAgendables_Conductor
        fields = ['id_vehiculo_conductor',
                  'id_persona_conductor',
                  'id_hoja_vida_vehiculo', 
                  'id_articulo', 
                  'id_vehiculo_arrendado', 
                  'tiene_platon', 
                  'es_arrendado',
                  'id_vehiculo_arrendado',
                  'placa',
                  'nombre',
                  'marca',
                  'id_marca',
                  'empresa_contratista',
                  'persona_conductor']


    def get_placa(self, obj):
        placa = None
        if obj.id_hoja_vida_vehiculo.es_arrendado:
            placa = obj.id_hoja_vida_vehiculo.id_vehiculo_arrendado.placa
        else:
            placa = obj.id_hoja_vida_vehiculo.id_articulo.doc_identificador_nro
        
        return placa
    

    def get_nombre(self, obj):
        nombre = None
        if obj.id_hoja_vida_vehiculo.es_arrendado:
            nombre = obj.id_hoja_vida_vehiculo.id_vehiculo_arrendado.nombre
        else:
            nombre = obj.id_hoja_vida_vehiculo.id_articulo.nombre
        
        return nombre
    
    def get_marca(self, obj):
        marca = None
        if obj.id_hoja_vida_vehiculo.es_arrendado:
            marca = obj.id_hoja_vida_vehiculo.id_vehiculo_arrendado.id_marca.nombre
        else:
            marca = obj.id_hoja_vida_vehiculo.id_articulo.id_marca
            marca = marca.nombre if marca else None
        
        return marca
    
    def get_id_marca(self, obj):
        id_marca = None
        if obj.id_hoja_vida_vehiculo.es_arrendado:
            id_marca = obj.id_hoja_vida_vehiculo.id_vehiculo_arrendado.id_marca.id_marca
        else:
            id_marca = obj.id_hoja_vida_vehiculo.id_articulo.id_marca
            id_marca = id_marca.id_marca if id_marca else None
        
        return id_marca
    
    def get_empresa_contratista(self, obj):
        empresa_contratista = None
        if obj.id_hoja_vida_vehiculo.es_arrendado:
            empresa_contratista = obj.id_hoja_vida_vehiculo.id_vehiculo_arrendado.empresa_contratista
    
        return empresa_contratista
    
    def get_persona_conductor(self, obj):
        persona_conductor = None
        if obj.id_persona_conductor:
            nombre_list = [obj.id_persona_conductor.primer_nombre, obj.id_persona_conductor.segundo_nombre,
                            obj.id_persona_conductor.primer_apellido, obj.id_persona_conductor.segundo_apellido]
            persona_conductor = ' '.join(item for item in nombre_list if item is not None)
            persona_conductor = persona_conductor if persona_conductor != "" else None
        return persona_conductor


class RegistrarVehiculoArrendadoSerializer(serializers.ModelSerializer):
    nombre_marca = serializers.ReadOnlyField(source='id_marca.nombre')
    id_hoja_de_vida = serializers.SerializerMethodField()

    class Meta:
        model = VehiculosArrendados
        fields = ['id_vehiculo_arrendado', 'nombre', 'descripcion', 'placa', 'nombre_marca', 'empresa_contratista', 'tiene_hoja_de_vida', 'id_marca','id_hoja_de_vida']
        extra_kwargs = {
            'id_marca': {'required': False}
        }
    
    #fk-pk
    def get_id_hoja_de_vida(self, obj):
        id_hoja_de_vida = obj.hojadevidavehiculos_set.first()
        id_hoja_de_vida = id_hoja_de_vida.id_hoja_de_vida if id_hoja_de_vida else None
        
        return id_hoja_de_vida
    


class DetallesViajeSerializer(serializers.ModelSerializer):

    placa = serializers.SerializerMethodField()
    nombre = serializers.SerializerMethodField()
    marca = serializers.SerializerMethodField()
    id_marca = serializers.SerializerMethodField()
    empresa_contratista = serializers.SerializerMethodField()
    persona_conductor = serializers.SerializerMethodField()

    class Meta:
        model = ViajesAgendados
        fields = '__all__'

    def get_placa(self, obj):
        if obj.id_vehiculo_conductor:
            if obj.id_vehiculo_conductor.id_hoja_vida_vehiculo:
                if obj.id_vehiculo_conductor.id_hoja_vida_vehiculo.es_arrendado:
                    return obj.id_vehiculo_conductor.id_hoja_vida_vehiculo.id_vehiculo_arrendado.placa
                else:
                    return obj.id_vehiculo_conductor.id_hoja_vida_vehiculo.id_articulo.doc_identificador_nro
        
        return None

    def get_nombre(self, obj):
        if obj.id_vehiculo_conductor:
            if obj.id_vehiculo_conductor.id_hoja_vida_vehiculo:
                if obj.id_vehiculo_conductor.id_hoja_vida_vehiculo.es_arrendado:
                    return obj.id_vehiculo_conductor.id_hoja_vida_vehiculo.id_vehiculo_arrendado.nombre
                else:
                    return obj.id_vehiculo_conductor.id_hoja_vida_vehiculo.id_articulo.nombre
        
        return None
    
    def get_marca(self, obj):
        if obj.id_vehiculo_conductor:
            if obj.id_vehiculo_conductor.id_hoja_vida_vehiculo:
                if obj.id_vehiculo_conductor.id_hoja_vida_vehiculo.es_arrendado:
                    return obj.id_vehiculo_conductor.id_hoja_vida_vehiculo.id_vehiculo_arrendado.id_marca.nombre
                else:
                    marca = obj.id_vehiculo_conductor.id_hoja_vida_vehiculo.id_articulo.id_marca
                    return marca.nombre if marca else None
        
        return None
    
    def get_id_marca(self, obj):
        if obj.id_vehiculo_conductor:
            if obj.id_vehiculo_conductor.id_hoja_vida_vehiculo:
                if obj.id_vehiculo_conductor.id_hoja_vida_vehiculo.es_arrendado:
                    return obj.id_vehiculo_conductor.id_hoja_vida_vehiculo.id_vehiculo_arrendado.id_marca.id_marca
                else:
                    id_marca = obj.id_vehiculo_conductor.id_hoja_vida_vehiculo.id_articulo.id_marca
                    return id_marca.id_marca if id_marca else None
        
        return None
    
    def get_empresa_contratista(self, obj):
        if obj.id_vehiculo_conductor:
            if obj.id_vehiculo_conductor.id_hoja_vida_vehiculo:
                if obj.id_vehiculo_conductor.id_hoja_vida_vehiculo.es_arrendado:
                    return obj.id_vehiculo_conductor.id_hoja_vida_vehiculo.id_vehiculo_arrendado.empresa_contratista
    
        return None
    
    def get_persona_conductor(self, obj):
        if obj.id_vehiculo_conductor:
            if obj.id_vehiculo_conductor.id_persona_conductor:
                nombre_list = [obj.id_vehiculo_conductor.id_persona_conductor.primer_nombre, obj.id_vehiculo_conductor.id_persona_conductor.segundo_nombre,
                            obj.id_vehiculo_conductor.id_persona_conductor.primer_apellido, obj.id_vehiculo_conductor.id_persona_conductor.segundo_apellido]
                persona_conductor = ' '.join(item for item in nombre_list if item is not None)
                persona_conductor = persona_conductor if persona_conductor != "" else None
                return persona_conductor
        


class ViajesAgendadosDeleteSerializer(serializers.ModelSerializer):

    class Meta:
        model = ViajesAgendados
        fields = '__all__'


class BitacoraViajeSerializer(serializers.ModelSerializer):
    id_conductor_que_parte = serializers.PrimaryKeyRelatedField(queryset=Personas.objects.all(), required=False)

    class Meta:
        model = BitacoraViaje    
        fields = ['id_bitacora', 
                  'id_viaje_agendado', 
                  'es_conductor_asignado', 
                  'id_conductor_que_parte', 
                  'fecha_inicio_recorrido', 
                  'novedad_salida', 
                  'fecha_llegada_recorrido', 
                  'novedad_llegada']
        extra_kwargs = {
            'id_conductor_que_parte': {'required': False}
        }


class BitacoraSalidaSerializer(serializers.ModelSerializer):
    class Meta:
        model = BitacoraViaje
        fields = ['id_bitacora', 'id_viaje_agendado', 'es_conductor_asignado', 'id_conductor_que_parte', 'fecha_inicio_recorrido', 'novedad_salida']


class BitacoraLlegadaSerializer(serializers.ModelSerializer):
    class Meta:
        model = BitacoraViaje
        fields = '__all__'


class BusquedaSolicitudViajeIdSerializer(serializers.ModelSerializer):
    nombre_estado_solicitud = serializers.CharField(source='get_estado_solicitud_display',read_only=True,default=None)
    class Meta:
        model = SolicitudesViajes
        fields = ['id_solicitud_viaje','estado_solicitud', 'nombre_estado_solicitud']

class PersonasSolicitudViajeSerializer(serializers.ModelSerializer):
    nombre_persona_viaja = serializers.SerializerMethodField()
    tipo_documento_persona_viaja = serializers.ReadOnlyField(source='id_persona_viaja.tipo_documento.cod_tipo_documento', default=None)
    numero_documento_persona_viaja = serializers.ReadOnlyField(source='id_persona_viaja.numero_documento', default=None)
    celular_documento_persona_viaja = serializers.ReadOnlyField(source='id_persona_viaja.telefono_celular', default=None)
    email_persona_viaja = serializers.ReadOnlyField(source='id_persona_viaja.email', default=None)


    class Meta:
        model = PersonasSolicitudViaje
        fields = '__all__'

    def get_nombre_persona_viaja(self, obj):
        nombre_persona_viaja = None
        if obj.id_persona_viaja:
            nombre_list = [obj.id_persona_viaja.primer_nombre, obj.id_persona_viaja.segundo_nombre,
                            obj.id_persona_viaja.primer_apellido, obj.id_persona_viaja.segundo_apellido]
            nombre_persona_viaja = ' '.join(item for item in nombre_list if item is not None)
            nombre_persona_viaja = nombre_persona_viaja if nombre_persona_viaja != "" else None
        return nombre_persona_viaja

    