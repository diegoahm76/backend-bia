from tramites.choices.cod_tipo_permiso_ambiental_choices import cod_tipo_permiso_ambiental_CHOICES

cod_tipo_permiso_ambiental_LIST = []
for choice in cod_tipo_permiso_ambiental_CHOICES:
    item = {
        "value": choice[0],
        "label": choice[1]
    }
    cod_tipo_permiso_ambiental_LIST.append(item)