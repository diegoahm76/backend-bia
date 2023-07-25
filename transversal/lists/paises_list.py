from transversal.choices.paises_choices import paises_CHOICES

paises_LIST = []
for choice in paises_CHOICES:
    item = {
        "value": choice[0],
        "label": choice[1]
    }
    paises_LIST.append(item)
