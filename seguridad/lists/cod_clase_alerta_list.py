from seguridad.choices.cod_clase_alerta_choices import COD_TIPO_ALERTA_CHOICES

cod_clase_alerta_LIST = []
for choice in COD_TIPO_ALERTA_CHOICES:
    item = {
        "value": choice[0],
        "label": choice[1]
    }
    cod_clase_alerta_LIST.append(item)