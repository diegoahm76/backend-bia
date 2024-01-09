from tramites.choices.cod_tipo_solicitud_al_requerimiento_choices import cod_tipo_solicitud_al_requerimiento_CHOICES

cod_tipo_solicitud_al_requerimiento_LIST = []
for choice in cod_tipo_solicitud_al_requerimiento_CHOICES:
    item = {
        "value": choice[0],
        "label": choice[1]
    }
    cod_tipo_solicitud_al_requerimiento_LIST.append(item)