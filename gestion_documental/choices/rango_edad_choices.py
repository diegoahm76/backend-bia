RANGO_EDAD_CHOICES = [
    ('A', 'De 18 a 25 años'),
    ('B', 'De 26 a 36 años'),
    ('C', 'De 37 a 46 años'),
    ('D', 'De 47 a 56 años'),
    ('E', 'Mayores de 56 años')
]


RANGO_EDAD_LIST = []
for choice in RANGO_EDAD_CHOICES:
    item = {
        "value": choice[0],
        "label": choice[1]
    }
    RANGO_EDAD_LIST.append(item)