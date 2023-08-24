TIPOS_RADICADO_CHOICES =(
        ('E', 'Entrada'),
        ('S', 'Salida'),
        ('I', 'Interno'),
        ('U', 'Unico'),
    )

cod_tipos_radicados_LIST = []
for choice in TIPOS_RADICADO_CHOICES:
    item = {
        "value": choice[0],
        "label": choice[1]
    }
    cod_tipos_radicados_LIST.append(item)