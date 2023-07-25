from transversal.choices.indicativo_paises_choices import indicativo_paises_CHOICES

indicativo_paises_LIST = []
for choice in indicativo_paises_CHOICES:
    item = {
        "value": choice[0],
        "label": choice[1]
    }
    indicativo_paises_LIST.append(item)
