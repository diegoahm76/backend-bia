from tramites.choices.cod_calendario_habiles_choices import cod_calendario_habiles_CHOICES

cod_calendario_habiles_LIST = []
for choice in cod_calendario_habiles_CHOICES:
    item = {
        "value": choice[0],
        "label": choice[1]
    }
    cod_calendario_habiles_LIST.append(item)