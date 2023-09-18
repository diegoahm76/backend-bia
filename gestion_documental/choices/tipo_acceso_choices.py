tipo_acceso_CHOICES=(('TC', 'Todos Colaboradores'), ('RT', 'Restringido'))


tipo_acceso_list = []
for choice in tipo_acceso_CHOICES:
    item = {
        "value": choice[0],
        "label": choice[1]
    }
    tipo_acceso_list.append(item)