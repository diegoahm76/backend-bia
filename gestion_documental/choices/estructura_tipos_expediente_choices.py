tipo_expediente_CHOICES =[('C', 'Complejo'), ('S', 'Simple')]


tipo_expediente_LIST = []
for choice in tipo_expediente_CHOICES:
    item = {
        "value": choice[0],
        "label": choice[1]
    }
    tipo_expediente_LIST.append(item)