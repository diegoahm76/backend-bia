from tramites.choices.cod_tipo_calidad_persona_choices import cod_tipo_calidad_persona_CHOICES

cod_tipo_calidad_persona_LIST = []
for choice in cod_tipo_calidad_persona_CHOICES:
    item = {
        "value": choice[0],
        "label": choice[1]
    }
    cod_tipo_calidad_persona_LIST.append(item)