from tramites.choices.cod_tipo_solicitud_juridica_choices import cod_tipo_solicitud_juridica_CHOICES

cod_tipo_solicitud_juridica_LIST = []
for choice in cod_tipo_solicitud_juridica_CHOICES:
    item = {
        "value": choice[0],
        "label": choice[1]
    }
    cod_tipo_solicitud_juridica_LIST.append(item)