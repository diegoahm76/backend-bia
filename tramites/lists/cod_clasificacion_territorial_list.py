from tramites.choices.cod_clasificacion_territorial_choices import cod_clasificacion_territorial_CHOICES

cod_clasificacion_territorial_LIST = []
for choice in cod_clasificacion_territorial_CHOICES:
    item = {
        "value": choice[0],
        "label": choice[1]
    }
    cod_clasificacion_territorial_LIST.append(item)