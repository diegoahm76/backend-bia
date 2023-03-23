from seguridad.choices.departamentos_choices import departamentos_CHOICES

departamentos_LIST = []
for choice in departamentos_CHOICES:
    item = {
        "value": choice[0],
        "label": choice[1]
    }
    departamentos_LIST.append(item)
