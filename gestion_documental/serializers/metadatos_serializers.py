from gestion_documental.models.metadatos_models import MetadatosPersonalizados, ListaValores_MetadatosPers
from rest_framework import serializers



########################## CRUD DE METADATO ##########################

class MetadatosPersonalizadosSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetadatosPersonalizados
        fields = '__all__'

    def validate(self, data):
        cod_tipo_dato_alojar = data.get('cod_tipo_dato_alojar')
        longitud_dato_alojar = data.get('longitud_dato_alojar')
        valor_minimo = data.get('valor_minimo')
        valor_maximo = data.get('valor_maximo')
        aplica_para_documento = data.get('aplica_para_documento')
        aplica_para_expediente = data.get('aplica_para_expediente')

        # Validación de tipos de datos
        if cod_tipo_dato_alojar == 'Tx':
            if longitud_dato_alojar is None:
                raise serializers.ValidationError("Si el tipo de dato es 'Tx', se debe proporcionar la longitud del dato")
            if valor_minimo is not None or valor_maximo is not None:
                raise serializers.ValidationError("Los campos valor_minimo y valor_maximo no son aplicables si el tipo de dato es 'Nm'")
        elif cod_tipo_dato_alojar == 'Fe':
            if longitud_dato_alojar is not None or valor_minimo is not None or valor_maximo is not None:
                raise serializers.ValidationError("Los campos longitud_dato_alojar, valor_minimo y valor_maximo no son aplicables si el tipo de dato es 'Fe'")
        elif cod_tipo_dato_alojar == 'Nm':
            if valor_minimo is None or valor_maximo is None:
                raise serializers.ValidationError("Si el tipo de dato es 'Nm', debes proporcionar ambos campos valor_minimo y valor_maximo.")
            if longitud_dato_alojar is None:
                raise serializers.ValidationError("Si el tipo de dato es 'Nm', se debe proporcionar la longitud del dato.")
        else:
            if valor_minimo is not None or valor_maximo is not None:
                raise serializers.ValidationError("Los campos valor_minimo y valor_maximo solo son aplicables si el tipo de dato es 'Tx' o 'Nm'.")
            if longitud_dato_alojar is not None:
                raise serializers.ValidationError("La longitud del dato solo es aplicable si el tipo de dato es 'Tx' o 'Nm'.")

        # Validación de los campos documento y expediente
        if not aplica_para_documento and not aplica_para_expediente:
            raise serializers.ValidationError("Al menos uno de los atributos 'aplica_para_documento' o 'aplica_para_expediente' debe estar en True.")

        return data

class MetadatosPersonalizadosGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetadatosPersonalizados
        fields = '__all__'

class GetMetadatosPersonalizadosOrdenSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetadatosPersonalizados
        fields = '__all__'

class MetadatosPersonalizadosDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetadatosPersonalizados
        fields = '__all__'

class MetadatosPersonalizadosUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetadatosPersonalizados
        fields = '__all__'

    def validate(self, data):
        cod_tipo_dato_alojar = data.get('cod_tipo_dato_alojar')
        longitud_dato_alojar = data.get('longitud_dato_alojar')
        valor_minimo = data.get('valor_minimo')
        valor_maximo = data.get('valor_maximo')
        aplica_para_documento = data.get('aplica_para_documento')
        aplica_para_expediente = data.get('aplica_para_expediente')

        # Validación de tipos de datos
        if cod_tipo_dato_alojar == 'Tx':
            if longitud_dato_alojar is None:
                raise serializers.ValidationError("Si el tipo de dato es 'Tx', se debe proporcionar la longitud del dato")
            if valor_minimo is not None or valor_maximo is not None:
                raise serializers.ValidationError("Los campos valor_minimo y valor_maximo no son aplicables si el tipo de dato es 'Nm'")
        elif cod_tipo_dato_alojar == 'Fe':
            if longitud_dato_alojar is not None or valor_minimo is not None or valor_maximo is not None:
                raise serializers.ValidationError("Los campos longitud_dato_alojar, valor_minimo y valor_maximo no son aplicables si el tipo de dato es 'Fe'")
        elif cod_tipo_dato_alojar == 'Nm':
            if valor_minimo is None or valor_maximo is None:
                raise serializers.ValidationError("Si el tipo de dato es 'Nm', debes proporcionar ambos campos valor_minimo y valor_maximo.")
            if longitud_dato_alojar is None:
                raise serializers.ValidationError("Si el tipo de dato es 'Nm', se debe proporcionar la longitud del dato.")
        else:
            if valor_minimo is not None or valor_maximo is not None:
                raise serializers.ValidationError("Los campos valor_minimo y valor_maximo solo son aplicables si el tipo de dato es 'Tx' o 'Nm'.")
            if longitud_dato_alojar is not None:
                raise serializers.ValidationError("La longitud del dato solo es aplicable si el tipo de dato es 'Tx' o 'Nm'.")

        # Validación de los campos documento y expediente
        if not aplica_para_documento and not aplica_para_expediente:
            raise serializers.ValidationError("Al menos uno de los atributos 'aplica_para_documento' o 'aplica_para_expediente' debe estar en True.")

        return data
    
    

class MetadatosPersonalizadosSearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetadatosPersonalizados
        fields = ['id_metadato_personalizado','nombre_metadato','descripcion','orden_aparicion']




########################## CRUD DE VALORES DE METADATOS ##########################

class MetadatosValoresCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model =  ListaValores_MetadatosPers
        fields = '__all__'

class MetadatosValoresGetOrdenSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListaValores_MetadatosPers
        fields = '__all__'

class MetadatosValoresGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListaValores_MetadatosPers
        fields = '__all__'


class ValoresMetadatosDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MetadatosPersonalizados
        fields = '__all__'