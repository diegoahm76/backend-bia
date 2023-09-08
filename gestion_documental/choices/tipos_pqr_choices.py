TIPOS_PQR = [
        ('P', 'Petición'),
        ('Q', 'Queja'),
        ('R', 'Reclamo'),
        ('S', 'Sugerencia'),
        ('D', 'Denuncia'),
        ('F', 'Felicitación'),
    ]

cond_tipos_pqr_list = []
for choice in TIPOS_PQR:
    item = {
        "value": choice[0],
        "label": choice[1]
    }
    cond_tipos_pqr_list.append(item)