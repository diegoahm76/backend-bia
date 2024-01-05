TIPOS_PQR = [
        ('PG', 'Petición General'),
        ('PD', 'Petición De Documentos o Información'),
        ('PC', 'Petición De Consulta'),
        ('Q', 'Queja'),
        ('R', 'Reclamo'),
        ('S', 'Sugerencia'),
        ('D', 'Denuncia'),
        ('F', 'Felicitación'),
    ]

COD_TIPO_TAREA_CHOICES = (
    ('Rpqr', 'Responder PQRSDF'),
    ('Rtra', 'Responder Trámite'),
  
)

COD_ESTADO_ASIGNACION_CHOICES = (
    ('Ac', 'Aceptado'),
    ('Re', 'Rechazado'),
 
)

COD_ESTADO_SOLICITUD_CHOICES = (
    ('De', 'Delegada'),
    ('Ep', 'En Proceso de Respuesta'),
    ('Re', 'Respondida por el propietario'),
   
)

RELACION_TITULAR = (
    ('MP', 'Misma persona'),
    ('RL', 'Representante legal'),
    ('AP', 'Apoderado'),

)

FORMA_PRESENTACION = (
    ('V', 'Verbal'),
    ('E', 'Escrita'),

)

TIPOS_OFICIO_CHOICES = (
    ('S', 'Solicitud'),
    ('R', 'Requerimiento'),

)


TIPO_SOLICITUD_PQRSDF = (
    ('PQ', 'PQRSDF'),
    ('TS', 'Tramites y servicios'),
    ('OP', 'OPAS'),
    ('OT', 'Otros'),

)

def choices_to_list(choices):
    choices_list = []
    for choice in choices:
        item = {"value": choice[0], "label": choice[1]}
        choices_list.append(item)
    return choices_list

cond_tipos_pqr_list = choices_to_list(TIPOS_PQR)
cod_tipo_tarea_choices_list = choices_to_list(COD_TIPO_TAREA_CHOICES)
cod_estado_asignacion_choices_list = choices_to_list(COD_ESTADO_ASIGNACION_CHOICES)
cod_estado_solicitud_choices_list = choices_to_list(COD_ESTADO_SOLICITUD_CHOICES)
relacion_titular_list = choices_to_list(RELACION_TITULAR)
forma_presentacion_list = choices_to_list(FORMA_PRESENTACION)
tipos_oficio_choices_list = choices_to_list(TIPOS_OFICIO_CHOICES)
