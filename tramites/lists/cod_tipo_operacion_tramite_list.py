from tramites.choices.cod_tipo_operacion_tramite_choices import cod_tipo_operacion_tramite_CHOICES

cod_tipo_operacion_tramite_LIST = []
for choice in cod_tipo_operacion_tramite_CHOICES:
    item = {
        "value": choice[0],
        "label": choice[1]
    }
    cod_tipo_operacion_tramite_LIST.append(item)