from seguridad.choices.cod_categoria_alerta_choices import CATEGORIA_ALERTA_CHOICES

cod_categoria_LIST = []
for choice in CATEGORIA_ALERTA_CHOICES:
    item = {
        "value": choice[0],
        "label": choice[1]
    }
    cod_categoria_LIST.append(item)