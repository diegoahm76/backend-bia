from datetime import datetime
from recaudo.models.base_models import ValoresVariables


def actualizarEstadoVariable():
    fecha_actual = datetime.now().date()
    
    # Obtener todas las variables
    variables = ValoresVariables.objects.all()
    
    for variable in variables:
        fecha_fin = variable.fecha_fin
        
        # Realiza la lógica para actualizar el estado según la fecha_actual y fecha_fin
        if fecha_actual >= fecha_fin:
            # Si la fecha actual es igual o mayor a la fecha_fin, establece el estado en False
            variable.estado = False
        else:
            # Si la fecha actual es anterior a la fecha_fin, mantiene el estado en True
            variable.estado = True
        
        # Guarda los cambios en la base de datos
        variable.save()

# Llama a la función para ejecutar la lógica de actualización
actualizarEstadoVariable()