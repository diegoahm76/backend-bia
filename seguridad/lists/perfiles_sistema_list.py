from seguridad.choices.perfiles_sistema_choices import PERFIL_SISTEMA_CHOICES

perfiles_LIST = []
for choice in PERFIL_SISTEMA_CHOICES:
    item = {
        "value": choice[0],
        "label": choice[1]
    }
    perfiles_LIST.append(item)