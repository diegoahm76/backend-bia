from tramites.choices.cod_tipo_predio_choices import cod_tipo_predio_CHOICES

cod_tipo_predio_LIST = []
for choice in cod_tipo_predio_CHOICES:
    item = {
        "value": choice[0],
        "label": choice[1]
    }
    cod_tipo_predio_LIST.append(item)