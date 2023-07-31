from transversal.choices.municipios_choices import municipios_CHOICES

municipios_LIST = []
for choice in municipios_CHOICES:
    item = {
        "value": choice[0],
        "label": choice[1]
    }
    municipios_LIST.append(item)
