from seguridad.choices.niveles_prioridad_alertas import NIVELES_PRIORIDAD_ALERTA_CHOICES

niveles_list = []
for choice in NIVELES_PRIORIDAD_ALERTA_CHOICES:
    item = {
        "value": choice[0],
        "label": choice[1]
    }
    niveles_list.append(item)