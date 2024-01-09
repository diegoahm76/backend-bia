from tramites.choices.cod_tipo_desistimiento_choices import cod_tipo_desistimiento_CHOICES

cod_tipo_desistimiento_LIST = []
for choice in cod_tipo_desistimiento_CHOICES:
    item = {
        "value": choice[0],
        "label": choice[1]
    }
    cod_tipo_desistimiento_LIST.append(item)