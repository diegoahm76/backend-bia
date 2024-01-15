from datetime import datetime


def actuallizarEstadoVriable():
       fecha_actual = datetime.now().date()
       valores=ValoresVariables.objects.all()
